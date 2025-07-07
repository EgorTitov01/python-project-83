from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool


class UrlsRepository:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection_pool = SimpleConnectionPool(4, 5, dsn=db_url)

    def get_connection(self):
        return self.connection_pool.getconn()

    def get_content(self):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('''
                SELECT
                    urls.id AS id,
                    name,
                    checks.created_at AS check_date,
                    status_code
                FROM urls LEFT JOIN url_checks AS checks
                    ON urls.id = checks.url_id
                WHERE checks.id in (
                    SELECT MAX(id) AS id
                    FROM url_checks
                    GROUP BY url_id
                ) OR checks.id IS NULL
                ORDER BY id DESC
                ''')
                result = cur.fetchall()

        self.connection_pool.putconn(conn)
        return result

    def find_by_url(self, parsed_url):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s",
                            (parsed_url,))
                result = cur.fetchone()

        self.connection_pool.putconn(conn)
        return result

    def find_by_id(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
                result = cur.fetchone()

        self.connection_pool.putconn(conn)
        return result

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
        self.connection_pool.putconn(conn)
        return url_data['id']

    def clear(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM urls")
            conn.commit()
        self.connection_pool.putconn(conn)

    def refresh(self):
        self.clear()
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("ALTER SEQUENCE urls_id_seq RESTART")
            conn.commit()
        self.connection_pool.putconn(conn)


class ChecksRepository:
    def __init__(self, db_url):
        self.connection_pool = SimpleConnectionPool(4, 5, db_url)

    def get_connection(self):
        return self.connection_pool.getconn()

    def get_content(self):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM url_checks")
                result = cur.fetchall()

        self.connection_pool.putconn(conn)
        return result

    def find(self, url_id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM url_checks WHERE url_id = %s",
                            (url_id,))
                result = cur.fetchall()

        self.connection_pool.putconn(conn)
        return result

    def save(self, check_data):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO url_checks (
                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        created_at
                        )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        check_data['url_id'],
                        check_data['status_code'],
                        check_data['h1_content'],
                        check_data['title'],
                        check_data['description'],
                        check_data['created_at']
                    ))

            conn.commit()
            self.connection_pool.putconn(conn)

    def clear(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM url_checks")
            conn.commit()
            self.connection_pool.putconn(conn)

    def refresh(self):
        self.clear()
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("ALTER SEQUENCE url_checks_id_seq RESTART")
            conn.commit()
            self.connection_pool.putconn(conn)
