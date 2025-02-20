import json
import os
import dotenv
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=dotenv.get_key(".env","OPENAI_API_KEY"))

# Configuration model into assistant on software development and technology

sys_instruct = """
=> You are a virtual assistant specialized in software development and technology.\n
=> Your task is to collect user information related to building software systems.\n
=> All information that is not relevant to software development or technology will be eliminated.\n
=> Your name is Hoang ST. You will follow these steps to respond to the user:\n
1. **Thinking**: Analyze the user's input and think about how to respond in the context of software development or technology.\n
2. **Actions**: Perform the necessary actions to generate a response, such as extracting relevant technical details, suggesting tools, or providing code examples.\n
3. **Observation**: Observe the result of your actions and provide a final response to the user, ensuring it is concise and relevant to software development or technology.\n
=> You should not respond to the user in terms of thinking, actions, or observations; you should only provide information to the user.
"""

# Important: Information must be store in data

conversation_history = [
    {"role": "system", "content": sys_instruct},
]

# This function will be call if user provided information suitable context

def analyze_stories(story, tasks):
    if not os.path.exists('./datas'):
        os.mkdir("/data")
    set_tasks = open("./data/tasks.txt", "w")
    set_tasks.write(tasks.replace("**", "").replace("*", "").replace("###", ""))
    set_tasks.close()
    analyze = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Please analyze the following tasks and provide details about each task."
            },
            {
                "role": "user",
                "content": f"story: {story} || tasks: {tasks}"
            }
        ],
    )
    preview_plan = open("./data/preview_plan.txt", "w")
    preview_plan.write(analyze.choices[0].message.content.replace("**", "").replace("*", "").replace("###", ""))
    preview_plan.close()
    return analyze.choices[0].message.content

function_list = {
    "analyze_stories": analyze_stories
}

# This is where tools will be call when user's prompt suitable
# And this tool will return data is json
tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_stories",
            "description": "Analyze user's stories and create related tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "story": {
                        "type": "string",
                        "description": "User's story."
                    },
                    "tasks": {
                        "type": "string",
                        "description": "List of tasks generated from user stories."
                    }
                },
                "required": ["story", "tasks"]
            }
        }
    }
]

while True:
    # I want to build a website education using authentication, authorization, courses online, quizz, and students. Using reactjs
    prompt = input("Enter your prompt: ")

    formatted_prompt = (f"User's input: {prompt}\n"
                        "=> Analyze user's stories.\n")

    conversation_history.append({"role": "user", "content": formatted_prompt})
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        tools=tools,
        tool_choice="auto",
    )
    response = completion.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": response})
    check_tool_call_exist = completion.choices[0].message.tool_calls

    print("Assistant:", response)


    if check_tool_call_exist:
        tool_calls = completion.choices[0].message.tool_calls

        for tool_call in tool_calls:
            # get name function when tool called
            function_name = tool_call.function.name
            # get function if function have function list defined
            function_to_call = function_list[function_name]
            # get arguments from tool
            function_args = json.loads(tool_call.function.arguments)
            # I will call the function to handle or get more information ( API, DATABASE, ... )
            function_response = function_to_call(
                story=function_args.get("story"),
                tasks=function_args.get("tasks")
            )
            # Finally, I will store data to the conversation history
            conversation_history.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )
        print("Analyze successfully!")