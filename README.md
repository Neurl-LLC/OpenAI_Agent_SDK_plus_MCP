# Model Context Protocol (MCP) + OpenAI Agent SDK

This repository demonstrates how to leverage the Model Context Protocol (MCP) within the OpenAI Agent SDK to build context-aware applications. It includes three example implementations:

- **Local Agent**: Connects to a local MCP server using Standard Input and Output (STDIO).
- **Remote Agent**: Connects to a remote MCP server using Server-Sent Events (SSE).
- **Voice Agent**: Integrates with an MCP server to enable voice-based interactions.

The examples are organized into the following directories:
- `mcp_server_sse`: Contains the implementation for the SSE-based remote agent.
- `mcp_server_stdio`: Contains the implementation for the STDIO-based local agent.
- `mcp_voice_agent`: Contains the implementation for the voice-enabled agent.


## Local Agent

To run the `local agent` example, you only need to install the OpenAI Agent SDK:

```bash
pip install openai-agents
```

You don't need to install the MCP SDK separately, as it is already included as a dependency of the OpenAI Agent SDK.

Once the installation is complete, navigate to the `mcp_server_stdio` directory and run the `main.py` script:

```bash
python main.py
```

This would launch a `REPL` that would let you use the [Filesystem MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) to interact with the `sample_folder`


## Remote Agent

The installation for the remote agent example is the same. Although this example depends on `uvicorn` and `starlette` but these are already dependencies of the MCP SDK.

To run this example first run the MCP server which is in the `server.py` file.

```bash
python server.py
```

Then run the agent as well which is in the `main.py` file.

```bash
python main.py
```

Again this launches an `REPL` but instead of connecting to an MCP server via standard Input and Output it connects to the server running on local host via SSE.

## Voice Agent

The installation process for the voice Agent is a bit different you need to install the OpenAI Agent SDK with voice dependencies.

```bash
pip install 'openai-agents[voice]'
```

Then install sounddevice:

```bash
pip install sounddevice
```

With this you can now run the the `main.py` python script.

```bash
python main.py
```

This will launch a `REPL` with a voice-based interface, allowing you to interact with the MCP server using voice commands instead of text.

