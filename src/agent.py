from langgraph.graph import START, END, StateGraph
from langchain_ollama import ChatOllama
from langchain.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from typing import Annotated, TypedDict, Literal, cast, Optional
from prompts import *
from dataclasses import dataclass
import streamlit as st


class InputState(TypedDict):
    mode: str | None
    messages: list[AnyMessage] | list[dict]

@dataclass
class OutputState:
    response: Optional[str]
    topic: Optional[str]
    summary: Optional[str]
    sources: Optional[list[str]]

def agent():

    class Context(TypedDict):
        messages: list[AnyMessage] 
        research_count: int

    class QueryState(Context):
        query: str
        summary: str

    class SummaryState(Context):
        summary: str
        texts: list[list[str]]
        sources: list[str]

    class ReflectState(Context):
        summary: str
        sources: list[str]

    class TopicState(TypedDict):
        topic: str | None

    class FinalState(TypedDict):
        response: str
        summary: str
        sources: list[str]


    model = ChatOllama(model="llama3.2:1b-instruct-q4_K_M")

    ## Tutor

    def generate_query(state: InputState) -> QueryState:
        ai_like = ['ai','assistant']

        if isinstance(state["messages"][0], dict):
            messages = cast(list[dict], state["messages"])
            state['messages'] = [AIMessage(message['content']) if (message.get('type', None) or message.get('role', None)) in ai_like else HumanMessage(message['content']) for message in messages]

        state['messages'] = cast(list[AnyMessage], state['messages'])  
    
        messages = [ str(message.content) for message in state['messages']]
        snippet = "\n".join(messages)
        fallback_query = f"Tell me more about the topic of this conversation: {snippet}"

        @tool
        def query_tool(query:str, rationale:str):
            """This tool is used to generate a query for web search.
            
            Args:
                query: The actual search string
                rationale: Brief explanation fo why this query is relevant
            """
            return {
                "query": query,
                "rationale": rationale 
            }
        

        model_with_tools = model.bind_tools([query_tool])
        result = model_with_tools.invoke(
                [SystemMessage(content=query_writer_instructions.format(current_date=get_current_date(), research_topic=snippet))] + state['messages'])
        
        if not result.tool_calls:
            query = fallback_query
        else:
            tool_data = result.tool_calls[0]["args"]
            query = tool_data.get('query', fallback_query)

        return {
            "messages": state['messages'],
            "query": query,
            "research_count": 0,
            "summary": ""
        }

    def search_web(state: QueryState) -> SummaryState:

        api_wrapper = DuckDuckGoSearchAPIWrapper(max_results=3, region="br-pt")

        search_engine = DuckDuckGoSearchResults(output_format="list", api_wrapper=api_wrapper)
        
        results = search_engine.invoke(state["query"])
        
        return {
            "messages": state['messages'],
            "texts": [[result["snippet"] for result in results]],
            "sources": [result["link"] for result in results],
            "summary": state['summary'],
            "research_count": state["research_count"] + 1
        }

    def summarize_search(state: SummaryState) -> ReflectState:
        conversation = "".join([str(message.content) for message in state['messages']])

        if not state['summary']:
            human_message_content = (
                f"<Existing Summary> \n {state['summary']} \n </Existing Summary>\n\n"
                f"<New Context> \n {"".join(state['texts'][-1])} \n </New Context>"
                f"Update the Existing Summary with the New Context on this topic: \n <User Input> \n {conversation} \n </User Input>\n\n"
            )
        else:
            human_message_content = (
                f"<Context> \n {"".join(state['texts'][-1])} \n </Context>"
                f"Create a Summary using the Context on this conversation: \n <User Input> \n {conversation} \n </User Input>\n\n"
            )

        result = model.invoke([SystemMessage(summarizer_instructions),
                    HumanMessage(human_message_content)])

        return {
            "summary": result.text,
            "sources": state['sources'],
            "research_count": state['research_count'],
            "messages": state['messages']
        }


    def reflect_on_summary(state: ReflectState) -> QueryState:
        conversation = "".join([str(message.content) for message in state['messages']])

        fallback_query = f"Tell me more about the topic of this conversation: {conversation}"
        
        @tool
        def follow_up_query(query: str, gap: str):
            """This tool is used to generate a follow-up query to adress a knowledge gap.

            Args:
                query: Write a specific question to adress this gap.
                gap: Describe what information is missing or needs clarification.
            """
            return {
                "query": query,
                "gap": gap
            }
        
        model_with_tools = model.bind_tools([follow_up_query])

        human_content = f"Reflect on our existing knowledge: \n === \n {state['summary']}, \n === \n And now identify a knowledge gap and generate a follow-up web search query:"

        result = model_with_tools.invoke([SystemMessage(reflection_instructions + tool_calling_reflection_instructions),
                                HumanMessage( content=human_content)])

        if not result.tool_calls:
            query = fallback_query
        else:
            tool_data = result.tool_calls[0]["args"]
            query = tool_data.get('query', fallback_query)

            if query == "":
                query = fallback_query

        
        return {
            "messages": state['messages'],
            "research_count": state['research_count'],
            'query': query,
            'summary': state['summary']
        }
        
    def finalize_summary(state: ReflectState) -> FinalState:
        response = model.invoke([SystemMessage(content=finalize_instructions.format(summary=state['summary']))] + state['messages'])
        
        return {
            "response": str(response.content),
            "sources": state['sources'],
            "summary": state['summary']
        }

    def reflect_router(state: QueryState) -> Literal['finalize', 'web_search']:
        if state['research_count'] >= 2:
            return 'finalize'
        else:
            return 'web_search'

    tutor_graph = StateGraph(InputState, output_schema=FinalState)

    tutor_graph.add_node("generate_query", generate_query)
    tutor_graph.add_node("web_search", search_web)
    tutor_graph.add_node("summarize", summarize_search)
    tutor_graph.add_node('reflect', reflect_on_summary)
    tutor_graph.add_node('finalize', finalize_summary)

    tutor_graph.add_edge("__start__", "generate_query")
    tutor_graph.add_edge("generate_query", "web_search")
    tutor_graph.add_edge("web_search",'summarize')
    tutor_graph.add_edge("summarize", "reflect")
    tutor_graph.add_conditional_edges("reflect", reflect_router)
    tutor_graph.add_edge('finalize','__end__')

    tutor_graph = tutor_graph.compile(name='tutor')

    def topic(state: InputState) -> TopicState:
        return {
            'topic': model.invoke(
                    [SystemMessage(("You're a helpuful assistant whoose job is to summarize conversations in a single topic or theme. That will be in the format of a single sentence with an maximum of 5 words. Example:"
                    "User: What is the diameter of the sun?"
                    "Assistant: The diameter of the sun is approximately 1,392,000 kilometers (865,000 miles)."
                    "What is the topic of this conversation?"
                    "Sun's diameter"))] +
                    state['messages']
                ).text
        }

    def resume_topic(state: TopicState) -> TopicState:
        return {
            'topic': str(model.invoke(
                [SystemMessage("You're a cataloguer of conversations. Summarize the given topic with 5 words or less."),
                    HumanMessage(f"Topic: {state['topic']}")]
            ).text)
        }

    def short_enough(state: TopicState) -> Literal["__end__", "resume_topic"]:
        if type(state['topic']) == str and len(state['topic'].split()) <= 5:
            return "__end__"
        else:
            return 'resume_topic'



    topic_graph = StateGraph(InputState, output_schema=TopicState)

    topic_graph.add_node("topic", topic)
    topic_graph.add_node("resume_topic", resume_topic)


    topic_graph.add_edge("__start__", "topic")
    topic_graph.add_edge('topic','resume_topic')
    topic_graph.add_conditional_edges('resume_topic', short_enough)

    def decide(state: InputState) -> Literal["topic", "tutor"]:

        if state['mode'] == 'tutor':
            return 'tutor'
        
        elif state['mode'] == 'topic':
            return "topic"
        
        else:
            raise ValueError("There must be a mode to the graph")

    def topic_getter(state: TopicState) -> TopicState:
        return state

    def tutor_getter(state: FinalState) -> FinalState:
        return state


    builder = StateGraph(InputState, output_schema=OutputState)

    builder.add_conditional_edges("__start__", decide)

    builder.add_edge('topic','topic_getter')
    builder.add_edge('topic_getter','__end__')

    builder.add_edge('tutor', 'tutor_getter')
    builder.add_edge('tutor_getter', '__end__')

    builder.add_node('tutor', tutor_graph)
    builder.add_node('topic', topic_graph.compile(name="topic"))
    builder.add_node('topic_getter', topic_getter)
    builder.add_node('tutor_getter', tutor_getter)

    graph = builder.compile()
    
    return graph

@st.cache_resource
def load_model():
    return agent()