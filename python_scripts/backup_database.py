import os
import subprocess
import gzip
import shutil
from dotenv import load_dotenv

# Load environment variables from .env (optional)
load_dotenv()

# Global path to pg_dump
PG_DUMP_PATH = "/Users/Shared/DBngin/postgresql/15.1/bin/pg_dump"
BACKUP_DIR = "/Users/lokeshsanapalli/Library/CloudStorage/Dropbox/Backups"

def backup_database(
    db_host, db_port, db_user, db_password,
    db_name, schema_name, output_basename
):
    backup_filename = os.path.join(BACKUP_DIR, f"{output_basename}.tar")

    dump_cmd = [
        PG_DUMP_PATH,
        "-h", db_host,
        "-p", str(db_port),
        "-U", db_user,
        "-F", "t",  # TAR format
        "-f", backup_filename,
        "-n", schema_name,
        db_name
    ]

    print(f"Backing up schema '{schema_name}' from database '{db_name}'...")
    result = subprocess.run(
        dump_cmd,
        env={**os.environ, "PGPASSWORD": db_password},
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"pg_dump failed for {db_name}:{schema_name}: {result.stderr.strip()}"
        )
    print(f"✅ Backup saved to {backup_filename}")


def main():
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    # Metabase DB details
    mb_user = os.getenv("MB_DB_USERNAME")
    mb_pass = os.getenv("MB_DB_PASSWORD")
    mb_name = "metabase"

    # PFM DB details
    pfm_user = os.getenv("PFM_DB_USERNAME")
    pfm_pass = os.getenv("PFM_DB_PASSWORD")
    pfm_name = "pfm"

    # Backup metabase DB: public schema only
    backup_database(
        db_host=db_host,
        db_port=db_port,
        db_user=mb_user,
        db_password=mb_pass,
        db_name=mb_name,
        schema_name="public",
        output_basename="dump_metabase"
    )

    # Backup pfm DB: public schema only
    backup_database(
        db_host=db_host,
        db_port=db_port,
        db_user=pfm_user,
        db_password=pfm_pass,
        db_name=pfm_name,
        schema_name="public",
        output_basename="dump_pfm"
    )

if __name__ == "__main__":
    main()

