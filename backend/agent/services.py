import os
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from ..homeassistant.functions import tools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def ollama_chat_completion(system_message, user_message, model_name="llama3.2", previous_context=None):
    llm = ChatOllama(model=model_name, temperature=0).bind_tools(tools)

    # messages = [
    #     SystemMessage(content=f'{system_message}\n\nPrevious context: {previous_context}'),
    #     HumanMessage(content=user_message)
    # ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        # MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    # response = await llm.ainvoke(messages)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    try:
        response = await agent_executor.ainvoke({
            "input": user_message
            # "chat_history": previous_context if previous_context else []
        })
        
        logger.info(f"Agent execution response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error in agent execution: {str(e)}", exc_info=True)
        raise

    # return response

