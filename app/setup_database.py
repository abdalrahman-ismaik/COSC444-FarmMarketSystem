"""One-time setup: creates the .env file (if missing) and loads schema.sql into MySQL.

Run:  python setup_database.py      (or double-click setup.bat)
WARNING: this re-creates the farm_market_db database with fresh sample data.
"""
import os
import sys
import getpass

BASE = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE, ".env")


def create_env():
    print("First-time setup: let's create your .env settings file.\n")
    host = input("MySQL host [localhost]: ").strip() or "localhost"
    port = input("MySQL port [3306]: ").strip() or "3306"
    user = input("MySQL user [root]: ").strip() or "root"
    password = getpass.getpass("MySQL password (hidden while typing): ")
    key = input("Gemini API key (press Enter to skip for now): ").strip()
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(f"DB_HOST={host}\nDB_PORT={port}\nDB_USER={user}\nDB_PASSWORD={password}\n"
                f"DB_NAME=farm_market_db\nGEMINI_API_KEY={key or 'YOUR_API_KEY'}\nGEMINI_MODEL=gemini-3.1-flash-lite\n")
    print("[OK] .env file created.\n")


def split_sql(text):
    statements, current = [], []
    for line in text.splitlines():
        if line.strip().startswith("--") and not current:
            continue
        current.append(line)
        if line.rstrip().endswith(";"):
            stmt = "\n".join(current).strip()
            if stmt and stmt != ";":
                statements.append(stmt)
            current = []
    return statements


def main():
    if not os.path.exists(ENV_PATH):
        create_env()
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH, override=True)
    import pymysql

    try:
        conn = pymysql.connect(host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", "3306")),
                               user=os.getenv("DB_USER", "root"), password=os.getenv("DB_PASSWORD", ""),
                               charset="utf8mb4", autocommit=True, connect_timeout=5)
    except pymysql.err.OperationalError as e:
        code = e.args[0] if e.args else None
        if code == 1045:
            print("[ERROR] MySQL rejected the user name or password. Fix them in the .env file and run setup again.")
        else:
            print("[ERROR] Cannot reach MySQL. Make sure the MySQL server is installed and running.")
        sys.exit(1)

    with open(os.path.join(BASE, "schema.sql"), encoding="utf-8") as f:
        statements = split_sql(f.read())
    print(f"Loading database ({len(statements)} SQL statements)...")
    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
        cur.execute("USE farm_market_db")
        cur.execute("SELECT (SELECT COUNT(*) FROM farms), (SELECT COUNT(*) FROM harvest_lots), "
                    "(SELECT COUNT(*) FROM market_requests), (SELECT COUNT(*) FROM harvest_lot_images)")
        farms, lots, reqs, imgs = cur.fetchone()
    conn.close()
    print(f"[OK] Database ready: {farms} farms, {lots} harvest lots, {reqs} market requests, {imgs} photos.")
    print("Now double-click run.bat (or run: python app.py).")


if __name__ == "__main__":
    main()
