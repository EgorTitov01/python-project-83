import psycopg2
from psycopg2.extras import RealDictCursor


class UrlsRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def get_content(self):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls ORDER BY id DESC")
                return cur.fetchall()

    def find_by_url(self, parsed_url):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s",
                            (parsed_url,))
                return cur.fetchone()

    def find_by_id(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
                return cur.fetchone()

    def save(self, url_data):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO urls (name, created_at) VALUES (%s, %s)
                    RETURNING id""",
                    (url_data['name'], url_data['created_at'])
                )
                url_data['id'] = cur.fetchone()[0]

            conn.commit()
        return url_data['id']

    def clear(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM urls")
            conn.commit()

    def refresh(self):
        self.clear()
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("ALTER SEQUENCE urls_id_seq RESTART;", (id,))
            conn.commit()
