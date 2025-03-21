from dataclasses import dataclass
import psycopg2


@dataclass
class PostgresArgs:
    user: str
    password: str
    host: str
    port: str
    database: str


def create_tables(args: PostgresArgs, file_path: str):

    # Read schema from SQL file
    with open(file_path, "r") as file:
        schema_sql = file.read()

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=args.database,
            user=args.user,
            password=args.password,
            host=args.host,
            port=args.port
        )
        cursor = conn.cursor()

        # Execute the schema SQL
        cursor.execute(schema_sql)

        # Commit changes
        conn.commit()
        print("✅ Tables created successfully!")

    except Exception as e:
        print("❌ Error creating tables:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
