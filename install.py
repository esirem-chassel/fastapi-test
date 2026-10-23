from sqlmodel import SQLModel
from database import engine

if __name__ == '__main__':
    SQLModel.metadata.create_all(engine)