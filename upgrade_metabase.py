import os
import subprocess
import requests
import gzip
import shutil
from datetime import datetime
from markdown import markdown
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Step 1: Backup the database
def backup_database():
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    backup_filename = f"metabase_backup_{timestamp}.gz"

    env_vars = ['MB_DB_HOST', 'MB_DB_PORT', 'MB_DB_USER', 'MB_DB_PASS', 'MB_DB_DBNAME']

    for var in env_vars:
        if var not in os.environ:
            raise EnvironmentError(f"{var} not set")

    dump_cmd = [
        "/Users/Shared/DBngin/postgresql/15.1/bin/pg_dump",
        "-h", os.environ["MB_DB_HOST"],
        "-p", os.environ["MB_DB_PORT"],
        "-U", os.environ["MB_DB_USER"],
        os.environ["MB_DB_DBNAME"]
    ]

    print("Backing up Metabase database...")
    with open(backup_filename, "wb") as f_out:
        proc = subprocess.Popen(dump_cmd, stdout=subprocess.PIPE, env={**os.environ, "PGPASSWORD": os.environ["MB_DB_PASS"]})
        with gzip.GzipFile(fileobj=f_out, mode="wb") as gz_out:
            shutil.copyfileobj(proc.stdout, gz_out)
        proc.wait()

    if proc.returncode != 0:
        raise RuntimeError("pg_dump failed")
    print(f"Backup saved to {backup_filename}")

# Step 2: Get latest Metabase JAR URL from GitHub release body
def get_latest_metabase_jar_url():
    print("Fetching latest release info from GitHub...")
    response = requests.get("https://api.github.com/repos/metabase/metabase/releases/latest")
    response.raise_for_status()
    release = response.json()
    body = release.get("body", "")

    # Convert Markdown to HTML
    html = markdown(body)
    soup = BeautifulSoup(html, "html.parser")

    # Look for the heading and JAR URL under it

    for h2 in soup.find_all("h2"):
        if "Metabase Open Source" in h2.text:
            for sibling in h2.find_next_siblings():
                if "JAR download:" in sibling.text:
                    import ipdb;ipdb.set_trace()
                    jar_url = sibling.text.split("JAR download:")[1].strip()
                    print(f"Found JAR URL: {jar_url}")

                    return jar_url

            break

    raise ValueError("Could not find Metabase JAR URL in release body")

# Step 3: Download and replace the JAR file
def download_and_replace_jar(jar_url):
    version = jar_url.split('/')[-2]  # e.g. v0.55.4.x
    jar_name = f"metabase.{version}.jar"

    print(f"Downloading Metabase JAR: {jar_name}")
    response = requests.get(jar_url, stream=True)
    response.raise_for_status()

    with open(jar_name, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    if os.path.exists("metabase.jar"):
        os.rename("metabase.jar", "metabase.old.jar")
        print("Renamed old metabase.jar to metabase.old.jar")

    os.rename(jar_name, "metabase.jar")
    print("Renamed downloaded JAR to metabase.jar")

# Main flow

if __name__ == "__main__":
    backup_database()
    jar_url = get_latest_metabase_jar_url()
    download_and_replace_jar(jar_url)
    print("✅ Metabase upgrade complete.")

