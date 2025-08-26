import psycopg2
from .conn import get_db_connection


def fetch_trusted_sources():

    db_conn = None
    trusted_sources_list = []

    query = "select source from news_source;"

    try:
        db_conn = get_db_connection(None)

        if db_conn:
            cur = db_conn.cursor()
            cur.execute(query)

            results = cur.fetchall()
            trusted_sources_list = [item[0] for item in results]

            cur.close()

    except (Exception, psycopg2.Error) as error:
        print(f"Error fetching trusted sources: {error}")

    finally:
        if db_conn:
            db_conn.close()

    return trusted_sources_list
