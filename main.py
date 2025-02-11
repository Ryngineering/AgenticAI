import os
from typing import Union
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.tools.render import render_text_description
from langchain_openai import ChatOpenAI
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.schema import AgentAction, AgentFinish
from langchain.agents.format_scratchpad import format_log_to_str

from callbacks import AgentCallbackHandler

load_dotenv()

""" 
Summary:
1. Creates a custom tool by using decorator @tool that returns the length of the input text which is used by the agent.
2. The code sets up an agent that uses a prompt template and an LLM to process input questions.
3. The agent generates a structured response, which is parsed to determine the next action.
4. If the action involves a tool, the tool is invoked, and the result is printed.
"""


# tool decorator is used to register the custom function as a tool
@tool
def get_text_length(text: str) -> int:
    """Returns the length of the text"""
    # strip because there llm sometimes adds non printable characters
    print(f"Text: {text=}")
    text = text.strip("'\n").strip('"')  # remove non printable characters
    return len(text)


def find_tool_with_name(tools: list[Tool], name: str) -> Tool:
    for tool in tools:
        if tool.name == name:
            return tool
    return ValueError(f"Tool with name {name} not found")


if __name__ == "__main__":
    print("Hello World!")
    # len = get_text_lenth("Hello World!")
    # Since the function is decorated we cannont call it directly but will need to use the .invoke method
    # len = get_text_length.invoke(input={"text": "Hello World!"})
    # print(len)


tools = [get_text_length]

PromptTemplate

# Copied this prompt from langsmith - hwchase17/react
template = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}

"""

prompt = PromptTemplate.from_template(template=template).partial(
    tools=render_text_description(tools),
    tool_names=", ".join([tool.name for tool in tools]),
)

llm = ChatOpenAI(
    temperature=0.0, stop=["\nObservation"], callbacks=[AgentCallbackHandler()]
)
intermediate_steps = []

# Langchain Expression that takes in a lamba function where 'x' is the input, it then passess this dictionary to the prompt
# the output of the prompt ( which is a react format prompt) is then passed to the openAI LLM model
# The output of the LLM model is then passed to the ReActSingleInputOutputParser. ReactSingleInputOutputParser expects the output from the
# LLM model to be in a specific format. ( Action: get_text_length\nAction Input: 'DOG' )
# If the output is in the expected format, the parser will return an AgentAction or AgentFinish object
thought = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["agent_scratchpad"]),
    }
    | prompt
    | llm
)

# print(thought)

agent = thought | ReActSingleInputOutputParser()

agent_step = ""
while not isinstance(agent_step, AgentFinish):
    #  invoke an agent
    agent_step: Union[AgentAction, AgentFinish] = agent.invoke(
        input={
            "input": "What is the text length of 'DOG' in characters ?",
            "agent_scratchpad": intermediate_steps,
        }
    )

    #  if the invocation response is a AgentAction object, which is an indication that the agent has a tool to use
    if isinstance(agent_step, AgentAction):
        tool = find_tool_with_name(tools, agent_step.tool)
        output = tool.func(str(agent_step.tool_input))
        print(f"{output=}")
        # store the intermediate steps which are appended to the prompt for the llm to understand the history.
        intermediate_steps.append((agent_step, str(output)))


# #  invoke an agent
# agent_step: Union[AgentAction, AgentFinish] = agent.invoke(
#     input={
#         "input": "What is the text length of 'DOG' in characters ?",
#         "agent_scratchpad": intermediate_steps,
#     }
# )

#  if the invocation response is a AgentAction object, which is an indication that the agent has a tool to use
if isinstance(agent_step, AgentFinish):
    print(agent_step.return_values)
