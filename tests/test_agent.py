import pytest
from src.agent import agent, InputState
from typing import cast
import dotenv

class TestAgent:
    def test_input(self):

        url = dotenv.get_key('.env','OLLAMA_HOST')
        if not url:
            raise ValueError('Sem OLLAMA_HOST no .env')
        
        model = agent(url)
        response = model.invoke(cast(InputState, {"messages": [{"role":"human", "content": "How do i study better"}], 'mode': 'tutor'}))
        assert response
        assert response['response']
