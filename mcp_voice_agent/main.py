import asyncio
import numpy as np
import sounddevice as sd

from agents.voice import StreamedAudioInput, VoicePipeline

from .workflow import VoiceAgentWorkflow

CHUNK_LENGTH_S = 0.05  # 50ms
SAMPLE_RATE = 24000
FORMAT = np.int16
CHANNELS = 1


class RealtimeCLIApp:
    def __init__(self, workflow: VoiceAgentWorkflow):
        self.should_send_audio = asyncio.Event()
        self.pipeline = VoicePipeline(
            workflow=workflow,
            stt_model="gpt-4o-transcribe",
            tts_model="gpt-4o-mini-tts",
        )
        self._audio_input = StreamedAudioInput()
        self.audio_player = sd.OutputStream(
            samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=FORMAT
        )

    def _on_transcription(self, transcription: str):
        print(f"Transcription: {transcription}")

    @classmethod
    async def create(cls) -> "RealtimeCLIApp":
        # Use a static callback because self is not available yet.
        workflow = await VoiceAgentWorkflow.create(on_start=cls._on_transcription_static)
        return cls(workflow)

    @staticmethod
    def _on_transcription_static(transcription: str):
        print(f"Transcription: {transcription}")

    async def start_voice_pipeline(self):
        try:
            self.audio_player.start()
            self.result = await self.pipeline.run(self._audio_input)

            async for event in self.result.stream():
                if event.type == "voice_stream_event_audio":
                    self.audio_player.write(event.data)
                elif event.type == "voice_stream_event_lifecycle":
                    print(f"Lifecycle event: {event.event}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.audio_player.close()

    async def send_mic_audio(self):
        stream = sd.InputStream(channels=CHANNELS, samplerate=SAMPLE_RATE, dtype="int16")
        stream.start()
        read_size = int(SAMPLE_RATE * 0.02)

        try:
            while True:
                if stream.read_available < read_size:
                    await asyncio.sleep(0)
                    continue

                # Wait for the flag that recording is active
                await self.should_send_audio.wait()
                data, _ = stream.read(read_size)
                await self._audio_input.add_audio(data)
                await asyncio.sleep(0)
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop()
            stream.close()

    async def run(self):
        print("Press 'K' to start/stop recording, 'Q' to quit.")
        # Start pipeline and microphone audio tasks as background tasks.
        asyncio.create_task(self.start_voice_pipeline())
        asyncio.create_task(self.send_mic_audio())

        while True:
            cmd = await asyncio.to_thread(input)  # Non-blocking input in a separate thread.
            cmd = cmd.strip().lower()
            if cmd == "q":
                break
            elif cmd == "k":
                if self.should_send_audio.is_set():
                    self.should_send_audio.clear()
                    print("Recording stopped.")
                else:
                    self.should_send_audio.set()
                    print("Recording started.")


async def async_main():
    app = await RealtimeCLIApp.create()
    await app.run()


if __name__ == "__main__":
    asyncio.run(async_main())
