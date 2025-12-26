import streamlit as st
from streamlit import session_state as ss
from repository.functions import *
from agent import load_model, ModelState
from typing import cast, Optional, TYPE_CHECKING
from UI import check_email, new_chat, display_chats, avatar, bot


model = load_model()

if "chats" not in ss:
    ss.chats = []
    new_chat(ss)

id = check_email(ss)
ss.user_id = id

if type(id) is int and 'chats_loaded' not in ss:
    ss.chats_loaded = True
    ss.chats.extend(get_chats(id))

display_chats(ss)

for iteration in ss.atual_chat.iterations:

    iteration = iteration.get_iteration()
    for message in iteration:
        with st.chat_message(message["role"], avatar= avatar if message['role'] == 'user' else bot):
            st.markdown(message["content"])

if prompt := st.chat_input("Escreva sua mágica aqui:"):

    ss.atual_chat = cast(Chat, ss.atual_chat)
    ss.atual_chat.put_iteration(prompt)

    with st.chat_message("user", avatar=avatar):
        st.markdown(prompt)
    
    response = model.invoke(cast(ModelState,{"messages": ss.atual_chat.get_iterations(), 'mode': 'tutor'}))['response']
    ss.atual_chat.iterations[-1].response = response

    with st.chat_message('assistant', avatar= bot):
        st.markdown(response)

    if ss.topic == '...':
        iterations = ss.atual_chat.iterations.copy()
        
        iterations.append(Iteration('What is the topic of this conversation?'))
        topic = model.invoke(cast(ModelState, {'messages': ss.atual_chat.get_iterations(), 'mode': 'topic'}))['topic']
        
        old_topic, ss.topic = ss.topic, topic

        ss.atual_chat.topic = topic

        if st.user.is_logged_in:
            ss.atual_chat.id = save_chat(ss['user_id'], ss.atual_chat)
            ss.atual_chat.change_ids_iterations()
            save_iteration(ss.atual_chat.iterations[-1])
            st.rerun()
    else:
        save_iteration(ss.atual_chat.iterations[-1])