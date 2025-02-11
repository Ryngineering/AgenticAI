# Custom Tool

### Tool Registration

```
@tool
def get_text_length(text: str) -> int:
    """Returns the length of the text"""
    text = text.strip("'\n").strip('"')  # remove non printable characters
    return len(text)
```

@tool: This decorator registers the get_text_length function as a tool that can be used by the agent.

### Prompt Template

Prompt template copied from langsmith (hwchase17/react ) which also has place holders for input question and list of tools (in this case get_text_length ) that is then fed into the LLM which then generates a thought ( decision if to use a tool or final response )

### Thought and Agent Setup

```
thought = {"input": lambda x: x["input"]} | prompt | llm
agent = thought | ReActSingleInputOutputParser()
```

thought: A pipeline that takes input, processes it through the prompt and LLM, and generates a structured response.
agent: Extends the thought pipeline with the ReActSingleInputOutputParser to parse the LLM's output.

### Agent Invocation and Output Handling

```
agent_step: Union[AgentAction, AgentFinish] = agent.invoke(
    input={"input": "What is the text length of 'DOG' in characters ?"}
)
if isinstance(agent_step, AgentAction):
    tool = find_tool_with_name(tools, agent_step.tool)
    output = tool.invoke(input=agent_step.tool_input)
    print(f"{output=}")
```

agent.invoke: Invokes the agent with the input question.
agent_step: The result of the agent invocation, which can be an AgentAction or AgentFinish.
if isinstance(agent_step, AgentAction): Checks if the result is an AgentAction.
find_tool_with_name: Finds the tool specified in the AgentAction.
tool.invoke: Invokes the tool with the input provided by the AgentAction.
print(f"{output=}"): Prints the output of the tool invocation.
