from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv

from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)

from tools import *

from rag import get_retriever


load_dotenv()


class AIAgent:

    def __init__(self):

        self.llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0.5
        )

        self.messages = [
            SystemMessage(
                content=(
                    "You are a helpful AI Knowledge Assistant. "
                    "Answer questions accurately. "
                    "Use the provided tools whenever needed. "
                    "When the user asks about uploaded documents "
                    "or the knowledge base, use the document search tool."
                )
            )
        ]

        url_reader = create_url_reader(self.llm)

        retriever = get_retriever()

        document_search = create_document_search_tool(
            retriever
        )

        self.agent = create_agent(
            model=self.llm,
            tools=[
                search_tool,
                calculator,
                get_weather,
                date_time,
                url_reader,
                document_search
            ]
        )

    async def run(
        self,
        message: str,
        chat_history: list
    ) -> str:

        messages = [
            SystemMessage(
                content=(
                    "You are a helpful AI Knowledge Assistant. "
                    "Answer questions accurately and "
                    "use the provided tools whenever needed. "
                    "When answering questions about uploaded "
                    "documents, use the document search tool."
                )
            )
        ]

        for msg in chat_history:

            if msg["role"] == "user":

                messages.append(
                    HumanMessage(
                        content=msg["content"]
                    )
                )

            elif msg["role"] == "assistant":

                messages.append(
                    AIMessage(
                        content=msg["content"]
                    )
                )

        response = await self.agent.ainvoke(
            {
                "messages": messages
            }
        )

        return response["messages"][-1].content
