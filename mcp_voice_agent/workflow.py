import os

from agents import Agent, Runner, TResponseInputItem
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper
from agents.mcp import MCPServerStdio


class VoiceAgentWorkflow(VoiceWorkflowBase):
    def __init__(self, agent: Agent, on_start):
        self._input_history: list[TResponseInputItem] = []
        self._current_agent = agent
        self._on_start = on_start

    async def run(self, transcription: str):
        self._on_start(transcription)
        # Add the transcription to the input history
        self._input_history.append({"role": "user", "content": transcription})

        # Run the agent (this returns a streaming result)
        result = Runner.run_streamed(self._current_agent, self._input_history)

        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            yield chunk

        print("Assistant:", result.final_output)
        # Update input history and agent state from result
        self._input_history = result.to_input_list()
        self._current_agent = result.last_agent

    @classmethod
    async def create(cls, on_start):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        samples_dir = os.path.join(current_dir, "sample_folder")

        # Instead of using an async context manager (which would close the server immediately),
        # we create the server and keep it open during the application lifetime.
        server = MCPServerStdio(
            name="Filesystem Server, via npx",
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
            },
        )
        # Explicitly connect the server
        await server.connect()

        spanish_agent = Agent(
            name="Spanish",
            handoff_description="A spanish speaking agent.",
            instructions=prompt_with_handoff_instructions(
                "You're speaking to a human, so be polite and concise. Speak in Spanish."
            ),
            model="gpt-4o-mini",
        )

        assistant_agent = Agent(
            name="Assistant",
            instructions=prompt_with_handoff_instructions(
                "You're speaking to a human, so be polite and concise. If the user speaks in Spanish, handoff to the spanish agent."
            ),
            model="gpt-4o-mini",
            handoffs=[spanish_agent],
            mcp_servers=[server],
        )

        return cls(agent=assistant_agent, on_start=on_start)
