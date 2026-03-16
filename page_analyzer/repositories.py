import os
from dotenv import load_dotenv
from sqlalchemy import (create_engine, select, delete, insert, func,
                        desc, text)
from .models import urls, url_checks


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
db_pool = None
engine = create_engine(DATABASE_URL, echo=True)


class UrlsRepository:
    def __init__(self):
        self.eng = engine

    def get_content(self):
        subq = select(func.max(url_checks.c.id).label("id")).group_by(
            url_checks.c.id).subquery()
        stmt = select(
            urls.c.id.label("id"),
            urls.c.name,
            url_checks.c.created_at.label("check_date"),
            url_checks.c.status_code
        ).outerjoin(url_checks, urls.c.id == url_checks.c.id).where(
            url_checks.c.id.in_(subq) | url_checks.c.id.is_(None)
        ).order_by(desc("id"))

        with self.eng.begin() as conn:
            conn.execute(stmt)
            result = [dict(m) for m in conn.execute(stmt).mappings().all()]
        return result

    def find_by_url(self, parsed_url):
        stmt = select(urls).where(urls.c.name == parsed_url)
        with self.eng.begin() as conn:
            mapp_result = conn.execute(stmt).mappings().first()

        return dict(mapp_result) if mapp_result else {}

    def find_by_id(self, id_):
        stmt = select(urls).where(urls.c.id == id_)
        with self.eng.begin() as conn:
            mapp_result = conn.execute(stmt).mappings().first()

        return dict(mapp_result) if mapp_result else {}

    def save(self, url_data):
        stmt = insert(urls).values(
            name=url_data["name"],
            created_at=url_data["created_at"]
        ).returning(urls.c.id)

        with self.eng.begin() as conn:
            url_data["id"] = conn.execute(stmt).fetchone()[0]
        return url_data['id']

    def clear(self):
        stmt = delete(urls)
        with self.eng.begin() as conn:
            conn.execute(stmt)

    def refresh(self):
        self.clear()
        with self.eng.begin() as conn:
            conn.execute(text("ALTER SEQUENCE urls_id_seq RESTART"))


class ChecksRepository:
    def __init__(self):
        self.eng = engine

    def get_content(self):
        stmt = select(url_checks)
        with self.eng.begin() as conn:
            result = [dict(m) for m in conn.execute(stmt).mappings().all()]
        return result

    def find(self, url_id):
        stmt = select(url_checks).where(url_checks.c.url_id == url_id)
        with self.eng.begin() as conn:
            result = [dict(m) for m in conn.execute(stmt).mappings().all()]
        return result

    def save(self, check_data):
        stmt = insert(url_checks).values(
            url_id=check_data['url_id'],
            status_code=check_data['status_code'],
            h1=check_data['h1_content'],
            title=check_data['title'],
            description=check_data['description'],
            created_at=check_data['created_at']
        )
        with self.eng.begin() as conn:
            conn.execute(stmt)

    def clear(self):
        stmt = delete(url_checks)
        with self.eng.begin() as conn:
            conn.execute(stmt)

    def refresh(self):
        self.clear()
        with self.eng.begin() as conn:
            conn.execute(text("ALTER SEQUENCE url_checks_id_seq RESTART"))

if __name__ == "__main__":

    ref = ChecksRepository()
    ref.clear()
    ref.refresh()

