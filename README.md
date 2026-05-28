# AI Query Tool

Implements an AI agent that processes user queries through OpenRouter's API (using Claude Haiku 4.5) with the ability to execute tools.

## Setup

1. Ensure you have `uv` installed locally.
2. Set the `OPENROUTER_API_KEY` environment variable with your OpenRouter API key.
3. Run `./your_program.sh` to execute your program, which is implemented in `app/main.py`.

### Key Components

#### Configuration
- **API_KEY**: Retrieved from the `OPENROUTER_API_KEY` environment variable
- **BASE_URL**: OpenRouter API endpoint (defaults to `https://openrouter.ai/api/v1`)

#### Available Tools

The application provides three tools that the AI model can invoke:

1. **Read Tool** - Read and return file contents
   - Parameter: `file_path` (string)
   - Returns the complete contents of the specified file

2. **Write Tool** - Write or overwrite file contents
   - Parameters: `file_path` (string), `content` (string)
   - Creates or updates files with the provided content

3. **Bash Tool** - Execute shell commands
   - Parameter: `command` (string)
   - Executes commands in the current working directory and returns output

#### Main Workflow

The `main()` function:
1. Parses command-line argument `-p` (the user's prompt/query)
2. Validates that `OPENROUTER_API_KEY` is set
3. Creates an OpenAI client configured for OpenRouter
4. Enters a loop that:
   - Sends the user message and conversation history to Claude Haiku
   - If the model calls tools, executes them and adds results to the conversation
   - If no tools are called, prints the model's response and exits

#### Usage

```bash
python app/main.py -p "Your query here"
```

**Example:**
```bash
python app/main.py -p "Read the file config.txt and tell me what's in it"
```

The AI will use the Read tool to access the file and provide you with its contents.
