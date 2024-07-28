from sqlalchemy.orm import sessionmaker
from models import create_tables, Word, New_word
import json
import sqlalchemy

login = str(input('Введите логин:'))
password = str(input('Введите пароль:'))
name_bd = str(input('Введите название базы данных:'))
DSN = f'postgresql+psycopg2://{login}:{password}@localhost:5432/{name_bd}'
engine = sqlalchemy.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()

create_tables(engine)

def load_db():
    with open ('База_данных_json.json', encoding='utf-8') as f:
        data = json.load(f)

    for record in data:
        model = {
            'word': Word,
            'new_word': New_word,
        }[record.get('model')]
        session.add(model(id=record.get('pk'), rus=record.get('rus'), en=record.get('en'), w_en_1=record.get('w_en_1'), w_en_2=record.get('w_en_2'), w_en_3=record.get('w_en_3')))
    session.commit()

load_db()