# Install the assemblyai package by executing the command "pip install assemblyai"

import assemblyai as aai

aai.settings.api_key = "0b02856b28b544fb84c66d827e380ebf"

# audio_file = "./local_file.mp3"
audio_file = "Takehome/39472_N_Darner_Dr_2.m4a"
print(audio_file)

config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.universal)

transcript = aai.Transcriber(config=config).transcribe(audio_file)

if transcript.status == "error":
  raise RuntimeError(f"Transcription failed: {transcript.error}")

print(transcript.text)