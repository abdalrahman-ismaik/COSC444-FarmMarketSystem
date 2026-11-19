"""Check the configured database before the GUI is launched without a console."""
import db


try:
    connection = db.get_connection()
    connection.close()
except Exception as exc:
    settings = db.db_settings()
    print(f"Database check failed for {settings['host']}:{settings['port']}.")
    print(db.friendly_error(exc))
    code = exc.args[0] if getattr(exc, "args", None) else None
    local_demo_stopped = (code == 2003 and settings["host"] == "127.0.0.1"
                          and settings["port"] == 3307)
    raise SystemExit(2 if local_demo_stopped else 1)

print("Database connection is ready.")
