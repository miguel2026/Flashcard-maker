import streamlit as st
from models import Chat
from repository.functions import save_user, get_id_from_email, get_chats
from typing import cast


def history(ss, id: int):
    ss.topic = ss.chats[id].topic
    ss.atual_chat = ss.chats[id]

def new_chat(ss):

    if len(ss.chats) == 0 or ss.chats[0].topic != '...':
        ss.chats.insert(0, Chat(iterations=[]))
        ss.topic = ss.chats[0].topic
        ss.atual_chat = ss.chats[0]


def check_email(ss) -> int:

    if not st.user.is_logged_in:

        if st.button('sign up/login with google'):

            st.login('google')

            if st.user.get('email') is not None:
                id = save_user(str(st.user.given_name), str(st.user.email))

    else:
        id = get_id_from_email(str(st.user.email))
    
    return id

def display_chats(ss):

    with st.sidebar:

        st.button('New chat', on_click= new_chat, args = [ss])

        st.write('History')

        for i, chat in enumerate(ss.chats):
            st.button(label=chat.topic, key=i, on_click= history, args=[ss, i])

avatar = """
<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#FFFFFF"><path d="M338-320q-14 0-25-8.5T299-351l-73-306q-2-11 .5-21t10.5-18l216-199q11-11 27-11t27 11l216 199q8 8 10.5 18t.5 21l-73 306q-3 14-14 22.5t-25 8.5H338Zm32-80h220l61-253-131-121v106q14 10 22 25t8 33q0 29-20.5 49.5T480-540q-29 0-49.5-20.5T410-610q0-18 8-33t22-25v-106L309-653l61 253ZM215-120q-20 0-32.5-16.5T177-173l5-12q8-25 29-40t47-15h444q26 0 47 15t29 40l5 12q7 20-5.5 36.5T745-120H215Z"/></svg>
"""

bot = """
<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#FFFFFF"><path d="M228-457h104l19 53q2 6 7 9.5t12 3.5q11 0 17.5-9t2.5-19l-82-216q-2-6-7.5-10t-12.5-4h-16q-7 0-12.5 4t-7.5 10l-82 216q-4 10 2.5 19t17.5 9q7 0 12.5-3.5T210-405l18-52Zm13-37 38-107h2l38 107h-78Zm19 174q47 0 91.5 10.5T440-278v-394q-41-24-87-36t-93-12q-36 0-71.5 7T120-692v396q35-12 69.5-18t70.5-6Zm260 42q44-21 88.5-31.5T700-320q36 0 70.5 6t69.5 18v-396q-33-14-68.5-21t-71.5-7q-47 0-93 12t-87 36v394ZM280-499Zm200 318q-14 0-26.5-3.5T430-194q-39-23-82-34.5T260-240q-42 0-82.5 11T100-198q-21 11-40.5-1T40-234v-482q0-11 5.5-21T62-752q46-24 96-36t102-12q58 0 113.5 15T480-740q51-30 106.5-45T700-800q52 0 102 12t96 36q11 5 16.5 15t5.5 21v482q0 23-19.5 35t-40.5 1q-37-20-77.5-31T700-240q-45 0-88 11.5T530-194q-11 6-23.5 9.5T480-181Zm80-428q0-9 6.5-18.5T581-640q29-10 58-15t61-5q20 0 39.5 2.5T778-651q9 2 15.5 10t6.5 18q0 17-11 25t-28 4q-14-3-29.5-4.5T700-600q-26 0-51 5t-48 13q-18 7-29.5-1T560-609Zm0 220q0-9 6.5-18.5T581-420q29-10 58-15t61-5q20 0 39.5 2.5T778-431q9 2 15.5 10t6.5 18q0 17-11 25t-28 4q-14-3-29.5-4.5T700-380q-26 0-51 4.5T601-363q-18 7-29.5-.5T560-389Zm0-110q0-9 6.5-18.5T581-530q29-10 58-15t61-5q20 0 39.5 2.5T778-541q9 2 15.5 10t6.5 18q0 17-11 25t-28 4q-14-3-29.5-4.5T700-490q-26 0-51 5t-48 13q-18 7-29.5-1T560-499Z"/></svg>
"""