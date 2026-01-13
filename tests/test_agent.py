import pytest
from src.agent import agent, InputState
from typing import cast


class TestAgent:
    def test_input(self):
        model = agent()
        response = model.invoke(cast(InputState, {"messages": [{"role":"human", "content": "How do i study better"}], 'mode': 'tutor'}))
        assert response
        assert response['response']
