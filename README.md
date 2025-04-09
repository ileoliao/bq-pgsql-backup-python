# 🛡️ Unified GCP Backup & Restore (Python-based, Multi-DB + Multi-Dataset)

This project provides a unified, Kubernetes-native solution for backing up and restoring:

- **Cloud SQL (PostgreSQL)** using `pg_dump` with IAM authentication
- **BigQuery datasets** using `bq extract/load` with **AVRO** format

Designed to run as a Kubernetes CronJob or one-time Job, this solution supports multiple PostgreSQL databases and multiple BigQuery datasets in a single container and run.

---

## ✨ Features

- ✅ Python-powered backup/restore scripts for better flexibility and error handling
- ✅ PostgreSQL logical backups using IAM authentication (no passwords)
- ✅ BigQuery exports to AVRO with schema integrity
- ✅ Stores all data in GCS buckets
- ✅ Uses a PVC to handle 50GB+ backups
- ✅ Uses Cloud SQL Proxy as a sidecar container
- ✅ Configurable via environment variables

---

## 🧱 Project Structure

```
.
├── Dockerfile              # Builds the backup/restore container
├── backup.py               # Python script to back up PostgreSQL and BigQuery
├── restore.py              # Python script to restore PostgreSQL and BigQuery
├── pvc.yaml                # PersistentVolumeClaim for disk-based backups
├── cronjob-backup.yaml     # CronJob to run daily backups
├── restore-job.yaml        # Job to perform manual restore
```

---

## 🔧 Setup

### 1. Build and Push Docker Image

```bash
docker build -t gcr.io/YOUR_PROJECT/unified-backup:latest .
docker push gcr.io/YOUR_PROJECT/unified-backup:latest
```

### 2. Create Kubernetes PVC

```bash
kubectl apply -f pvc.yaml
```

### 3. Configure and Deploy CronJob

Edit `cronjob-backup.yaml` with your values (e.g. DB names, GCS bucket), then:

```bash
kubectl apply -f cronjob-backup.yaml
```

### 4. Run Restore Job

Edit `restore-job.yaml` with the file or dataset to restore, then:

```bash
kubectl apply -f restore-job.yaml
```

---

## 🔐 Required IAM Roles

Ensure your GKE workload identity or service account has:

- `roles/cloudsql.client`
- `roles/storage.objectAdmin`
- `roles/bigquery.dataViewer`
- `roles/bigquery.jobUser`

---

## 🧪 Environment Variables

| Variable                | Description                                  |
|------------------------|----------------------------------------------|
| `ENABLE_PG_BACKUP`     | Enable PostgreSQL backup (`true`/`false`)    |
| `ENABLE_BQ_BACKUP`     | Enable BigQuery backup (`true`/`false`)      |
| `ENABLE_PG_RESTORE`    | Enable PostgreSQL restore (`true`/`false`)   |
| `ENABLE_BQ_RESTORE`    | Enable BigQuery restore (`true`/`false`)     |
| `PGUSER`               | IAM Postgres user (email)                    |
| `PG_DATABASES`         | Comma-separated PostgreSQL DB list           |
| `DB_NAME`              | DB name to restore to                        |
| `INSTANCE_CONNECTION_NAME` | Cloud SQL instance name (project:region:instance) |
| `GCS_BUCKET`           | GCS bucket for storing backups               |
| `RESTORE_FILE`         | GCS file name to restore (.sql.gz)           |
| `RESTORE_DATE`         | Date folder for BigQuery restore             |
| `BQ_PROJECT`           | BigQuery project                             |
| `BQ_DATASETS`          | Comma-separated BigQuery datasets (for backup) |
| `BQ_DATASET`           | BigQuery dataset for restore                 |

---

## 📌 Notes

- PostgreSQL backups are compressed `.sql.gz` dumps.
- BigQuery backups are exported as `table-*.avro` under date-stamped folders.
- PVC is mounted to `/backup` and `/restore` inside the container.
- Cloud SQL Proxy uses Unix sockets at `/cloudsql`.

---

## 📄 License

MIT — free to use, modify, and adapt for your organization.