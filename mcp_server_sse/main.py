import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerSse


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
    async with MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    ) as server:
        await run(server)

if __name__ == "__main__":
    asyncio.run(main())
