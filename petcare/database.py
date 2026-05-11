from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./petcare.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


SQLITE_COLUMN_MIGRATIONS = {
    "pets": [
        {
            "name": "breed",
            "ddl": "ALTER TABLE pets ADD COLUMN breed VARCHAR(50)",
        },
        {
            "name": "created_at",
            "ddl": "ALTER TABLE pets ADD COLUMN created_at DATETIME",
            "backfill": "UPDATE pets SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL",
        },
        {
            "name": "updated_at",
            "ddl": "ALTER TABLE pets ADD COLUMN updated_at DATETIME",
            "backfill": "UPDATE pets SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL",
        },
        {
            "name": "owner_id",
            "ddl": "ALTER TABLE pets ADD COLUMN owner_id INTEGER",
        },
    ],
    "health_records": [
        {
            "name": "created_at",
            "ddl": "ALTER TABLE health_records ADD COLUMN created_at DATETIME",
            "backfill": "UPDATE health_records SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL",
        },
        {
            "name": "updated_at",
            "ddl": "ALTER TABLE health_records ADD COLUMN updated_at DATETIME",
            "backfill": "UPDATE health_records SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL",
        },
        {
            "name": "hospital_id",
            "ddl": "ALTER TABLE health_records ADD COLUMN hospital_id INTEGER",
        },
        {
            "name": "diagnosis",
            "ddl": "ALTER TABLE health_records ADD COLUMN diagnosis VARCHAR(200)",
        },
        {
            "name": "prescription",
            "ddl": "ALTER TABLE health_records ADD COLUMN prescription VARCHAR(200)",
        },
        {
            "name": "veterinarian_name",
            "ddl": "ALTER TABLE health_records ADD COLUMN veterinarian_name VARCHAR(100)",
        },
        {
            "name": "visit_type",
            "ddl": "ALTER TABLE health_records ADD COLUMN visit_type VARCHAR(20)",
        },
        {
            "name": "severity",
            "ddl": "ALTER TABLE health_records ADD COLUMN severity VARCHAR(20)",
        },
    ],
    "vaccinations": [
        {
            "name": "created_at",
            "ddl": "ALTER TABLE vaccinations ADD COLUMN created_at DATETIME",
            "backfill": "UPDATE vaccinations SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL",
        },
        {
            "name": "updated_at",
            "ddl": "ALTER TABLE vaccinations ADD COLUMN updated_at DATETIME",
            "backfill": "UPDATE vaccinations SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL",
        },
    ],
    "schedules": [
        {
            "name": "created_at",
            "ddl": "ALTER TABLE schedules ADD COLUMN created_at DATETIME",
            "backfill": "UPDATE schedules SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL",
        },
        {
            "name": "updated_at",
            "ddl": "ALTER TABLE schedules ADD COLUMN updated_at DATETIME",
            "backfill": "UPDATE schedules SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL",
        },
    ],
}


def run_startup_migrations() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)

    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON"))

        for table_name, migrations in SQLITE_COLUMN_MIGRATIONS.items():
            if not inspector.has_table(table_name):
                continue

            existing_columns = {
                column["name"] for column in inspector.get_columns(table_name)
            }

            for migration in migrations:
                if migration["name"] not in existing_columns:
                    conn.execute(text(migration["ddl"]))
                    existing_columns.add(migration["name"])
                if migration.get("backfill"):
                    conn.execute(text(migration["backfill"]))
