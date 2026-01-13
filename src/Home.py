import streamlit as st
from streamlit import session_state as ss
from agent import load_model
from repository.functions import *
from UI import check_email

load_model()

if not st.user.is_logged_in:
    check_email(ss)
    
st.title("Skill Loop", text_alignment='center')

b = bytes([0xF0, 0x9F, 0x96, 0x8A])
s = b.decode("utf-8")

st.markdown(
f"""
## An LLM focused study tool. {s}

### <a href=/exercise target= '_self'>Exercise</a>
#### It's an agent focused on giving broad and depth lists of exercises based on your level.
This feature improves as you use Skill Loop. Data is saved if you're logged in.
            
### <a href=/flashcards target= '_self'>Flashcards</a>
#### Create flashcards that can be exported to Anki!
You can reuse old exercises.

### <a href=/tutor target= '_self'>Tutor</a>
#### Search for new knowledge from the web!

""",unsafe_allow_html=True)