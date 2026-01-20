import psycopg2
from psycopg2.extras import DictCursor
from .conn import get_db_connection


def fetch_trusted_sources():

    db_conn = None
    trusted_sources_list = []

    query = "select source from news_source order by id;"

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


def fetch_categories():
    db_conn = None
    query = "select category_name from categories order by id;"
    try:
        db_conn = get_db_connection(None)

        if db_conn:
            cur = db_conn.cursor(cursor_factory=DictCursor)
            cur.execute(query)

            results = cur.fetchall()
            category = [row['category_name']for row in results]

            # trusted_sources_list = [item[0] for item in results]

            cur.close()

    except (Exception, psycopg2.Error) as error:
        print(f"Error fetching trusted sources: {error}")

    finally:
        if db_conn:
            db_conn.close()

    return category


def getPreference(category, sources):
    db_conn = None

    query = """
    with source as(
        select id,source from news_source
        where source in %s
    ),
    category as (
        select id from categories where category_name=%s
    ),
    preference as(
        select s.source, p.preference, row_number() over (order by p.preference asc) as rank
        from source s
        join news_source_preference p
        on s.id=p.source_id
        join category c
        on c.id=p.category_id
    )
    select source from preference
    where rank=1

    """

    try:
        db_conn = get_db_connection(None)

        if db_conn:
            cur = db_conn.cursor(cursor_factory=DictCursor)
            cur.execute(query, (tuple(sources), category))
            result = cur.fetchone()[0]

            cur.close()

    except (Exception, psycopg2.Error) as error:
        print(f"Error fetching trusted sources: {error}")

    finally:
        if db_conn:
            db_conn.close()
        return result


def fetchSelectors(source):

    print(source)
    db_conn = None

    query = """
    select content_selector from news_source ns where ns.source=%s ;
    """
    try:
        db_conn = get_db_connection(None)
        if db_conn:
            cur = db_conn.cursor(cursor_factory=DictCursor)

            cur.execute(query, (source,))
            result = cur.fetchone()['content_selector']
            cur.close()

    except (Exception, psycopg2.Error) as error:
        print(f"Error fetching trusted sources: {error}")

    finally:
        if db_conn:
            db_conn.close()
        return result
