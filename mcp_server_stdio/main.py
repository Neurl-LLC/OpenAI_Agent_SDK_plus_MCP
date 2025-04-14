import asyncio
import os
from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio

async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to read the filesystem and answer questions based on those files.",
        mcp_servers=[mcp_server],
    )

    input_history = []

    while True:
        user_input = input("\nProvide your prompt (or type 'exit' to quit):")
        if user_input.lower() == "exit":
            print("Exiting chat.")
            break

        input_history.append(
            {
                "role": "user",
                "content": user_input
            }
        )
    
        result = await Runner.run(starting_agent=agent, input=input_history)
        
        print("Assistant:", result.final_output)
        input_history = result.to_input_list()
    
async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_folder")

    async with MCPServerStdio(
        name="Filesystem Server, via npx",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
        },
    ) as server:
        await run(server)


if __name__ == "__main__":
    asyncio.run(main())
