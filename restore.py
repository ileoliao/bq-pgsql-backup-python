import os
import subprocess
from google.cloud import storage
from datetime import datetime

def run_pg_restore(pg_user, db_name, bucket, restore_file):
    pg_host = "127.0.0.1"
    pg_port = "5432"
    print(f"Downloading {restore_file} from GCS...")
    local_file = f"/restore/{restore_file}"
    storage.Client().bucket(bucket).blob(f"pgsql-backups/{restore_file}").download_to_filename(local_file)

    print("Restoring database...")
    gunzip = subprocess.Popen(["gunzip", "-c", local_file], stdout=subprocess.PIPE)
    psql = subprocess.Popen([
        "psql",
        "-h", pg_host,
        "-p", pg_port,
        "-U", pg_user,
        "-d", db_name
    ], stdin=gunzip.stdout)
    gunzip.stdout.close()
    psql.communicate()

def run_bq_restore(project, dataset, bucket, restore_date):
    print("Downloading AVRO files from GCS...")
    client = storage.Client()
    bucket_ref = client.bucket(bucket)
    prefix = f"bq-backups/{dataset}/{restore_date}/"
    blobs = list(client.list_blobs(bucket_ref, prefix=prefix))

    for blob in blobs:
        filename = blob.name.split("/")[-1]
        table = filename.replace("table-", "").replace(".avro", "")
        local_path = f"/restore/{filename}"
        blob.download_to_filename(local_path)
        print(f"Restoring table: {table}")
        subprocess.run([
            "bq", "load",
            "--source_format=AVRO",
            f"{project}:{dataset}.{table}",
            local_path
        ], check=True)

if __name__ == "__main__":
    if os.getenv("ENABLE_PG_RESTORE", "false").lower() == "true":
        run_pg_restore(
            os.environ["PGUSER"],
            os.environ["DB_NAME"],
            os.environ["GCS_BUCKET"],
            os.environ["RESTORE_FILE"]
        )
    if os.getenv("ENABLE_BQ_RESTORE", "false").lower() == "true":
        run_bq_restore(
            os.environ["BQ_PROJECT"],
            os.environ["BQ_DATASET"],
            os.environ["GCS_BUCKET"],
            os.environ["RESTORE_DATE"]
        )