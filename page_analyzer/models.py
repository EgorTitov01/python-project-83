from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Identity, func, String, Integer, Date


metadata_obj = MetaData()

urls = Table(
    "urls",
    metadata_obj,
    Column("id", Integer, Identity(always=True), primary_key=True),
    Column("name", String(255), unique=True, nullable=False),
    Column("created_at", Date, nullable=False)
)

url_checks = Table(
    "url_checks",
    metadata_obj,
    Column("id", Integer, Identity(always=True), primary_key=True),
    Column("url_id", Integer, nullable=False),
    Column("status_code", Integer),
    Column("h1", String),
    Column("title", String),
    Column("description", String),
    Column("created_at", Date, default=func.current_date())
)
