import os, sqlalchemy, ssl, psycopg2

class SQLClient:
    def __init__(self):
        try:
            SQL_SERVER = "34.47.131.52"
            SQL_DATABASE = "cricdata"
            SQL_USER = "postgres"
            SQL_PASSWORD = "sagar12@" 
            SQL_PORT = "5432"

            host = os.getenv("SQL_HOST") if os.getenv("SQL_HOST") else SQL_SERVER
            dbname = os.getenv("SQL_DB") if os.getenv("SQL_DB") else SQL_DATABASE
            user = os.getenv("SQL_USER") if os.getenv("SQL_USER") else SQL_USER
            password = os.getenv("SQL_PASSWORD") if os.getenv("SQL_PASSWORD") else SQL_PASSWORD
            port = os.getenv("SQL_PORT") if os.getenv("SQL_PORT") else SQL_PORT

            self.engine = sqlalchemy.create_engine(
                # Equivalent URL:
                # postgresql+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
                sqlalchemy.engine.url.URL.create(
                    drivername="postgresql+pg8000",
                    username=user,
                    password=password,
                    host=host,
                    port=port,
                    database=dbname,
                ),
            )

            # Test the connection
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(sqlalchemy.text("SELECT version()")).fetchone()
                    version = result[0]
                    print(f"PostgreSQL version: {version}")
            except Exception as e:
                print(f"Error connecting to the database: {e}")
                raise

        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            raise