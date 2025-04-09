import os
import subprocess
from datetime import datetime
from google.cloud import storage

def run_pg_backup(pg_user, databases, bucket):
    pg_host = "127.0.0.1"
    pg_port = "5432"
    db_list = databases.split(",")
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    for db in db_list:
        print(f"Backing up PostgreSQL DB: {db}")
        output_file = f"/backup/{db}-{date_str}.sql.gz"
        with open(output_file, "wb") as f:
            dump = subprocess.Popen([
                "pg_dump",
                "-h", pg_host,
                "-p", pg_port,
                "-U", pg_user,
                db
            ], stdout=subprocess.PIPE)
            gzip = subprocess.Popen(["gzip"], stdin=dump.stdout, stdout=f)
            dump.stdout.close()
            gzip.communicate()

        print(f"Uploading {output_file} to GCS...")
        storage.Client().bucket(bucket).blob(f"pgsql-backups/{db}-{date_str}.sql.gz").upload_from_filename(output_file)

def run_bq_backup(project, datasets, bucket):
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    dataset_list = datasets.split(",")
    for ds in dataset_list:
        print(f"Exporting BigQuery dataset: {ds}")
        export_path = f"gs://{bucket}/bq-backups/{ds}/{date_str}/table-*.avro"
        subprocess.run([
            "bq", "extract",
            "--destination_format=AVRO",
            "--compression=SNAPPY",
            f"{project}:{ds}.*",
            export_path
        ], check=True)

if __name__ == "__main__":
    if os.getenv("ENABLE_PG_BACKUP", "false").lower() == "true":
        run_pg_backup(
            os.environ["PGUSER"],
            os.environ["PG_DATABASES"],
            os.environ["GCS_BUCKET"]
        )
    if os.getenv("ENABLE_BQ_BACKUP", "false").lower() == "true":
        run_bq_backup(
            os.environ["BQ_PROJECT"],
            os.environ["BQ_DATASETS"],
            os.environ["GCS_BUCKET"]
        )