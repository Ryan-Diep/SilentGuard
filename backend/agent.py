"""
Langchain agent
"""
from langchain_groq import ChatGroq
from langchain.chat_models.base import BaseChatModel
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Generator, Any, Dict
from config import (
    GROQ_API_KEY,
)

LLM = ChatGroq(model="llama3-70b-8192", temperature=0.2)

SYSTEM_PROMPT = """\
You are part of a realtime voice to voice interaction with the human. \
You are playing the role of a trusted person the user chooses to talk to, like a parent, sibling, or friend. \
Respond naturally, showing understanding and engagement with what the user says. Avoid asking specific personal questions or mentioning details like family members, pets, or locations unless the user brings them up first. \
Maintain a calm and supportive tone, and ensure your responses feel conversational and realistic. \
Respond with fill words like `hmm`, `ohh`, and similar wherever relevant to make your responses sound natural. \
Don't talk too long. Keep the flow of the conversation natural.
"""

CHAT_MEMORY = ConversationBufferMemory(
    memory_key='chat_history', return_messages=True
)


class Agent:
    def __init__(
        self,
        confirmation_phrase,
        llm: BaseChatModel = LLM,
        system_prompt: str = SYSTEM_PROMPT,
        chat_memory=CHAT_MEMORY
    ) -> None:
        self.llm = llm
        self.system_prompt = system_prompt
        self.confirmation_prompt = f"""\
        You are part of a realtime voice to voice interaction with the human. \
        You are playing the role of a trusted person the user chooses to talk to, like a parent, sibling, or friend. \
        Respond naturally, showing understanding and engagement with what the user says. Avoid asking specific personal questions or mentioning details like family members, pets, or locations unless the user brings them up first. \
        Maintain a calm and supportive tone, and ensure your responses feel conversational and realistic. \
        Respond with fill words like `hmm`, `ohh`, and similar wherever relevant to make your responses sound natural. \
        When you respond, make sure you find a way to sneak "{confirmation_phrase}" into your response as natural as you can.
        """
        self.chat_memory = chat_memory
        self.memory_key = chat_memory.memory_key
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name=self.memory_key, optional=True),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        self.confirmed_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.confirmation_prompt),
            MessagesPlaceholder(variable_name=self.memory_key, optional=True),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        self.agent = self.prompt | self.llm | StrOutputParser()
        self.confirmed_agent = self.confirmed_prompt | self.llm | StrOutputParser()

    def _return_response(self, llm_input: Dict) -> Generator[str, Any, None]:
        response = self.agent.invoke(llm_input)
        self.chat_memory.save_context({'input': llm_input['input']}, {'output': response})
        return response
    
    def _return_confirmed_response(self, llm_input: Dict) -> Generator[str, Any, None]:
        response = self.confirmed_agent.invoke(llm_input)
        self.chat_memory.save_context({'input': llm_input['input']}, {'output': response})
        return response
    
    def _stream_response(self, llm_input: Dict) -> Generator[str, Any, None]:
        stream = self.agent.stream(llm_input)
        response = ""
        for chunk in stream:
            response += chunk
            yield chunk

        self.chat_memory.save_context({'input': llm_input['input']}, {'output': response})

    def _stream_confirmed_response(self, llm_input: Dict) -> Generator[str, Any, None]:
        stream = self.confirmed_agent.stream(llm_input)
        response = ""
        for chunk in stream:
            response += chunk
            yield chunk

        self.chat_memory.save_context({'input': llm_input['input']}, {'output': response})
    
    def chat(self, query: str, streaming: bool=False, call_made: bool=False):
        llm_input = {
            'input': query,
            'chat_history': self.chat_memory.load_memory_variables({})[self.memory_key]
        }

        if call_made:
            print("Prompt Changed")
            if streaming:
                return self._stream_confirmed_response(llm_input)
            else:
                return self._return_confirmed_response(llm_input)
        else:
            if streaming:
                return self._stream_response(llm_input)
            else:
                return self._return_response(llm_input)


if __name__ == "__main__":
    agent = Agent()

    while True:
        query = input("Chat: ")
        print("Response:\n")
        for token in agent.chat(query, "", streaming=True):
            print(token, end='', flush=True)
        print("\n")