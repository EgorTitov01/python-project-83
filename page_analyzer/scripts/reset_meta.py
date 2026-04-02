from page_analyzer.repositories import db_reset
from page_analyzer.models import metadata_obj
from page_analyzer.repositories import engine


if __name__ == '__main__':
    metadata_obj.create_all(engine)
    db_reset()
