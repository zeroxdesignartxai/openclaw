from app.db.session import Base, engine
from app.db import models  # noqa: F401


def main():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()
