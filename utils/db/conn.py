import psycopg2
import sys
import os
from dotenv import load_dotenv

load_dotenv()


config = {
    "dbname":   os.environ.get("DB_NAME"),
    "user":     os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host":     os.environ.get("DB_HOST", "localhost"),
}


def get_db_connection(existing_conn):
    if existing_conn is None or existing_conn.closed:

        try:
            connection = psycopg2.connect(**config)
            return connection
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error, file=sys.stderr)
            return None

    return existing_conn
