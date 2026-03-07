from openai import OpenAI
import json

# Initialize the client pointing to our local server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="",  # Key is required by library but ignored by our server
)


def print_stream(response):
    print("--- Streaming Response ---")
    content_parts = []
    tool_calls = {}
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            content_parts.append(delta.content)
            print(delta.content, end="", flush=True)
        elif delta.tool_calls:
            print(f"\n[Tool Call Chunk]: {delta.tool_calls}")
            for tool_call in delta.tool_calls:
                index = getattr(tool_call, "index", 0)
                current_tool_call = tool_calls.setdefault(
                    index,
                    {
                        "id": "",
                        "type": "function",
                        "function": {"name": "", "arguments": ""},
                    },
                )

                tool_call_id = getattr(tool_call, "id", None)
                if tool_call_id:
                    current_tool_call["id"] = tool_call_id

                function = getattr(tool_call, "function", None)
                if not function:
                    continue

                function_name = getattr(function, "name", None)
                if function_name:
                    current_tool_call["function"]["name"] = function_name

                function_arguments = getattr(function, "arguments", None)
                if function_arguments:
                    current_tool_call["function"]["arguments"] += function_arguments
    print("\n--- End of Stream ---\n")
    return "".join(content_parts), [
        tool_calls[index] for index in sorted(tool_calls.keys())
    ]


def run_tool(name, arguments):
    if name == "get_weather":
        location = arguments.get("location", "unknown")
        return {
            "location": location,
            "temperature_c": 22,
            "condition": "sunny",
        }
    raise ValueError(f"Unknown tool: {name}")


def test_chat():
    print("1. Testing Normal Chat (Streaming)...")
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-3B-Instruct",
        messages=[{"role": "user", "content": "Hello world"}],
        stream=True,
    )
    print_stream(response)


def test_tool_call():
    print("2. Testing Tool Call (Streaming)...")
    user_message = {"role": "user", "content": "What is the weather in Beijing?"}

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-3B-Instruct",
        messages=[user_message],
        tools=tools,
        stream=True,
    )

    _, tool_calls = print_stream(response)

    if not tool_calls:
        return

    tool_call = tool_calls[0]
    tool_call_id = tool_call["id"] or "call_local_0"
    tool_name = tool_call["function"]["name"]
    tool_arguments_payload = tool_call["function"].get("arguments", "")
    tool_arguments = (
        json.loads(tool_arguments_payload) if tool_arguments_payload else {}
    )
    tool_result = run_tool(tool_name, tool_arguments)
    tool_result_payload = json.dumps(tool_result, ensure_ascii=False)

    print(f"Tool Result: {tool_result_payload}")
    follow_up = client.chat.completions.create(
        model="Qwen/Qwen2.5-3B-Instruct",
        messages=[
            user_message,
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": tool_arguments_payload,
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_result_payload,
            },
        ],
        tools=tools,
        stream=True,
    )
    print_stream(follow_up)


if __name__ == "__main__":
    try:
        test_chat()
        test_tool_call()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the server is running! (uv run server.py)")
