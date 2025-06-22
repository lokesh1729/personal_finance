import os
import subprocess
import gzip
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env (optional)
load_dotenv()

# Global path to pg_dump
PG_DUMP_PATH = "/Users/Shared/DBngin/postgresql/15.1/bin/pg_dump"

def backup_database(
    db_host, db_port, db_user, db_password,
    db_name, schema_name
):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    backup_filename = f"dump_{db_name}_{schema_name}_{timestamp}.gz"

    dump_cmd = [
        PG_DUMP_PATH,
        "-h", db_host,
        "-p", str(db_port),
        "-U", db_user,
        "-n", schema_name,
        db_name
    ]

    print(f"Backing up schema '{schema_name}' from database '{db_name}'...")
    with open(backup_filename, "wb") as f_out:
        proc = subprocess.Popen(
            dump_cmd,
            stdout=subprocess.PIPE,
            env={**os.environ, "PGPASSWORD": db_password}
        )
        with gzip.GzipFile(fileobj=f_out, mode="wb") as gz_out:
            shutil.copyfileobj(proc.stdout, gz_out)
        proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"pg_dump failed for {db_name}:{schema_name}")
    print(f"✅ Backup saved to {backup_filename}")


def main():
    # Personal Finance DB details
    pf_host = os.getenv("DB_HOST")
    pf_port = os.getenv("DB_PORT")
    pf_user = os.getenv("PF_DB_USERNAME")
    pf_pass = os.getenv("PF_DB_PASSWORD")
    pf_name = "personal_finance"

    # Metabase DB details
    mb_user = os.getenv("MB_DB_USERNAME")
    mb_pass = os.getenv("MB_DB_PASSWORD")
    mb_name = "metabase"

    # Backup personal_finance DB: public and dropshipping schemas
    for schema in ["public", "dropshipping"]:
        backup_database(
            db_host=pf_host,
            db_port=pf_port,
            db_user=pf_user,
            db_password=pf_pass,
            db_name=pf_name,
            schema_name=schema
        )

    # Backup metabase DB: public schema only
    backup_database(
        db_host=pf_host,  # assuming same host and port
        db_port=pf_port,
        db_user=mb_user,
        db_password=mb_pass,
        db_name=mb_name,
        schema_name="public"
    )

if __name__ == "__main__":
    main()

