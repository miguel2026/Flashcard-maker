from streamlit import connection
from models import User, Chat, Iteration
from sqlalchemy import text
from dataclasses import asdict


### User

conn = connection('postgresql', type='sql')

def save_user(name:str, email:str, age: int | None = None) -> int:
    with conn.session as session:

        if session.execute(text('SELECT 1 FROM users WHERE email = :email'), {'email': email}).scalar() is not None:
            raise ValueError("User with this email already exists")
        
        id = session.execute(text(
            """
            INSERT INTO public.user (name, email, age) 
            VALUES (:name, :email, :age)
            RETURNING id"
            """),
            {'name': name, 'email': email, 'age': age}
        ).scalar()
        
        session.commit()

        if id is None:
            raise ValueError("User ID should not be None after commit")
        
        return id


def get_id_from_email(email:str) -> int | bool:
    with conn.session as session:
        result = session.execute(
            text("SELECT id FROM public.user WHERE email = :email"),params={'email':email}
        ).one_or_none()
        if result is not None:
            return result.id
        else:
            return False

def get_user_info(id:int):
    with conn.session as session:
        result = session.execute(text("SELECT user where id = :id"), {"id": id}).scalar()

### Chat

def get_chats(user_id: int, limit: int = 20) -> list[Chat]:
    with conn.session as session:
        result = session.execute(
        text(
        """
        SELECT * FROM public.chat 
        WHERE user_id = :user_id
        ORDER BY timestamp DESC
        LIMIT :limit
        """
        ).bindparams(),
        {'user_id': user_id,
         'limit': limit}
        ).mappings().all()
        
        chats = [Chat(**row) for row in result]
        
        for chat in chats:
            result = session.execute(
                text(
                    "SELECT * FROM public.iteration WHERE chat_id = :chat_id"
                ),{'chat_id': chat.id}
            ).mappings().all()
            chat.iterations.extend([Iteration(**iteration) for iteration in result])
        return chats

def get_chat(user_id: int, chat_id: int) -> Chat:
    with conn.session as session:
        result = session.execute(
        text(
            "SELECT * FROM public.chat WHERE id = :chat_id AND user_id = :user_id"
        ),
        {'chat_id':chat_id,
         'user_id': user_id}
        ).mappings().one()

        return Chat(**result)


def get_chat_from_topic(user_id: int, topic: str) -> tuple[int | None,list[dict[str,str]]]:
    with conn.session as session:
        chat_id = session.execute(
            text(
                "SELECT id FROM public.chat WHERE topic = :topic AND user_id = :user_id"
            ),
            {'topic': topic,
             'user_id': user_id}).scalar_one_or_none()
        
        if chat_id is None:
            return None, []
        
        iterations = session.execute(
            text(
                "SELECT * FROM public.iteration WHERE chat_id = :chat_id"
            ),
            {'chat_id': chat_id}
        ).mappings().all()

        iterations = [Iteration(**iteration) for iteration in iterations]

        return (int(chat_id), 
                [value for iteration in iterations for value in iteration.get_iteration()])


def save_chat(user_id: int, chat: Chat) -> int | None:
    if user_id is None:
        raise ValueError('user_id é necessário, pois é foreign key')
    
    with conn.session as session:
        chat.user_id = user_id
        result = session.execute(
            text(
                "INSERT INTO public.chat (user_id, topic, timestamp) " \
                "VALUES (:user_id, :topic, :timestamp)" \
                "RETURNING id"
            ),
            asdict(chat)
        ).scalar()
        session.commit()

        return result

### Iteration


def save_iteration(iteration: Iteration) -> None:
    if iteration.chat_id is None:
        raise ValueError('chat_id é necessário, pois é foreign key')
    
    with conn.session as session:
        session.execute(
            text(
                "INSERT INTO public.iteration (chat_id ,message, response) VALUES (:chat_id, :message, :response)"
            ),
            asdict(iteration))
        session.commit()
