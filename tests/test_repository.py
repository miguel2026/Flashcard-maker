import pytest
from src.repository.functions import *
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

class FakeConnection:
    def __init__(self, engine):
        self.engine = engine
        self.session = Session(engine)



engine = create_engine('postgresql://postgres:postgres@127.0.0.1:54322/postgres')
test_connection = FakeConnection(engine)


def delete_user(id):
    with test_connection.session as session:
        session.execute(
            text(
                "DELETE from public.user WHERE id = :id"
            ), {"id": id})
        session.commit()

def delete_chat(id):
    with test_connection.session as session:
        session.execute(
            text(
                "DELETE from public.chat WHERE id = :id"
            ), {"id": id}
        )
        session.commit()


class TestUser:
        
    def test_save_user(self):
        result = save_user('test','test_email@gmail.com',12, test_connection)
        assert type(result) is int

        delete_user(result)


    def test_get_id_from_email(self):
        id = save_user('test','test_email@gmail.com',12, test_connection)
        result = get_id_from_email('test_email@gmail.com', test_connection)
        assert type(result) is int
        assert id == result

        delete_user(id)

    def test_get_user_info(self):
        id = save_user('test1','test1@gmail.com', conn = test_connection)
        id2 = save_user('test2','test2@gmail.com', 1, conn = test_connection)
        
        result = get_user_info(id, test_connection)
        delete_user(id)
        assert type(result) is dict
        assert result['id'] == id
        assert result['email'] == 'test1@gmail.com'
        assert result['age'] == None

        result2 = get_user_info(id2, test_connection)
        delete_user(id2)
        
        assert type(result2) is dict
        assert result2['id'] == id2
        assert result2['email'] == 'test2@gmail.com'
        assert result2['age'] == 1

class TestChat:
    def test_get_chats(self):
        pass

    def test_get_chat(self):
        pass

    def test_save_chat(self):
        user_id = save_user('test','test_email@gmail.com',12, test_connection)
        
        chat = Chat(topic='testing')

        result = save_chat(user_id, chat, test_connection)

        assert result is not None

        delete_chat(result)
        delete_user(user_id)