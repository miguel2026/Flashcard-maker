from langgraph.graph import START, END, StateGraph
from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from typing import Annotated, TypedDict
import streamlit as st


class ModelState(TypedDict):
    mode: str | None
    messages : list[AnyMessage]
    response: str | None
    topic: str | None
    iteration: int | None

def agent():
    model = init_chat_model("llama3.2:1b-instruct-q4_K_M", model_provider='ollama', configurable_fields='any')
    
 
    def tutor(state: ModelState) -> ModelState:
        return {
            **state,
            "response": model.invoke(
                [SystemMessage("You're a helpful study assistant focused on explaining topics in an easy and detailed manner.")]
                + state['messages']
            ).content
        }

    def topic(state: ModelState) -> ModelState:

        return {
            **state,
            'topic': model.invoke(
                    [SystemMessage(("You're a helpuful assistant whoose job is to summarize conversations in a single topic or theme. That will be in the format of a single sentence with an maximum of 5 words. Example:"
                    "User: What is the diameter of the sun?"
                    "Assistant: The diameter of the sun is approximately 1,392,000 kilometers (865,000 miles)."
                    "What is the topic of this conversation?"
                    "Sun's diameter"))] +
                    state['messages']
                ).content
        }

    def resume_topic(state: ModelState) -> ModelState:
        return {
            **state,
            'topic': model.invoke(
                [SystemMessage("You're a cataloguer of conversations. Always keep the topics of the conversations very short at maximum 5 words."),
                 HumanMessage(state['topic'])]
            ).content
        }

    def deck(state: ModelState):
        pass
    
    def flashcard(state: ModelState):
        return {
            **state,
            'flashcard': model.invoke(
                [SystemMessage((f"You're a helpful assistant whose job is to make one flashcard based on a topic that you will be given.\n"
                                f"Iteration: {state['iteration']}\n\n"
                                "Write exactly in this format:\n"
                                "Q: <question>\n"
                                "A: <answer>"))] +
                state['messages']
            )
        }



    def decide(state: ModelState):
        return state['mode']

    def short_enough(state: ModelState):
        if type(state['topic']) == str and len(state['topic'].split()) <= 5:
            return END
        else:
            return 'resume_topic'
    


    graph = StateGraph(ModelState)
    
    graph.add_node('tutor', tutor)
    graph.add_node('topic', topic)
    graph.add_node('resume_topic', resume_topic)


    graph.add_conditional_edges(START,decide)
    graph.add_conditional_edges('resume_topic',short_enough)

    graph.add_edge('tutor',END)
    graph.add_edge('topic','resume_topic')

    return graph.compile()

@st.cache_resource
def load_model():
    return agent()