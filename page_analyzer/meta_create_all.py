from .models import metadata_obj
from .repositories import engine


def create_db_meta():
    metadata_obj.create_all(engine)


if __name__ == '__main__':
    create_db_meta()
