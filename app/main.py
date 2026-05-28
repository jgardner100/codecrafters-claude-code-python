import argparse
import json
import os
import sys

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")

READ_TOOL = {
    "type": "function",
    "function": {
        "name": "Read",
        "description": "Read and return the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read",
                }
            },
            "required": ["file_path"],
        },
    },
}

WRITE_TOOL = {
    "type": "function",
    "function": {
        "name": "Write",
        "description": "Write content to a file",
        "parameters": {
            "type": "object",
            "required": ["file_path", "content"],
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path of the file to write to",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file",
                },
            },
        },
    },
}

TOOLS = [READ_TOOL, WRITE_TOOL]


def execute_read_tool(arguments: str) -> str:
    parsed_args = json.loads(arguments or "{}")
    file_path = parsed_args["file_path"]

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def execute_write_tool(arguments: str) -> str:
    parsed_args = json.loads(arguments or "{}")
    file_path = parsed_args["file_path"]
    content = parsed_args["content"]

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Wrote {len(content)} bytes to {file_path}"


def execute_tool(tool_call) -> str:
    if tool_call.type != "function":
        raise RuntimeError(f"unsupported tool call type: {tool_call.type}")

    function_name = tool_call.function.name
    if function_name == "Read":
        return execute_read_tool(tool_call.function.arguments)
    if function_name == "Write":
        return execute_write_tool(tool_call.function.arguments)

    raise RuntimeError(f"unsupported tool call: {function_name}")


def assistant_message_to_dict(message) -> dict:
    result = {
        "role": "assistant",
        "content": message.content,
    }

    tool_calls = message.tool_calls or []
    if tool_calls:
        result["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in tool_calls
        ]

    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    messages = [{"role": "user", "content": args.p}]

    while True:
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=TOOLS,
        )

        if not chat.choices:
            raise RuntimeError("no choices in response")

        message = chat.choices[0].message
        messages.append(assistant_message_to_dict(message))

        tool_calls = message.tool_calls or []
        if not tool_calls:
            print(message.content or "")
            return

        for tool_call in tool_calls:
            result = execute_tool(tool_call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )


if __name__ == "__main__":
    main()
