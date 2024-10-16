import json
import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile
from google.cloud import speech
from google.cloud import texttospeech
from google.oauth2 import service_account
import io
import requests
import subprocess
import os

# Load credentials from the secrets
credentials_info = st.secrets["general"]
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable if needed
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_info['private_key']

def run_app():
    st.title("Video Audio Correction Tool")
    
    uploaded_video = st.file_uploader("Choose a video file (mp4, avi, mov):", type=["mp4", "avi", "mov"])
    
    if uploaded_video:
        st.video(uploaded_video)
        
        if st.button("Start Processing"):
            handle_video_processing(uploaded_video)

def handle_video_processing(uploaded_video):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        video_file_path = temp_video.name
        temp_video.write(uploaded_video.read())

    st.info("Extracting audio from the video...")
    audio_file_path = extract_audio(video_file_path)
    st.success("Audio extraction completed.")

    st.info("Transcribing the audio...")
    transcription_result = transcribe_audio(audio_file_path)
    st.success("Audio transcription finished.")
    st.write(transcription_result)

    st.info("Correcting the transcription using GPT-4o...")
    corrected_transcription = refine_transcription(transcription_result)
    st.success("Transcription correction done.")
    st.write(corrected_transcription)

    st.info("Generating audio from corrected text...")
    corrected_audio_file = "corrected_audio.mp3"
    create_audio_from_text(corrected_transcription, corrected_audio_file)
    st.success("Audio generation complete.")

    st.info("Merging corrected audio with the video...")
    final_video_path = "final_video.mp4"

    try:
        combine_audio_and_video(video_file_path, corrected_audio_file, final_video_path)
        if os.path.exists(final_video_path):
            st.success("Video processing finished.")
            st.video(final_video_path)
        else:
            st.error("Final video was not created.")
    except Exception as e:
        st.error(f"An error occurred during video processing: {e}")


def extract_audio(video_path):
    """Extract audio from the video file and save as MP3."""
    video_clip = VideoFileClip(video_path)
    audio_file_path = video_path.replace(".mp4", ".mp3")
    video_clip.audio.write_audiofile(audio_file_path)
    return audio_file_path

def transcribe_audio(audio_file_path):
    client = speech.SpeechClient(credentials=credentials)

    with io.open(audio_file_path, "rb") as audio_file:
        audio_content = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    full_transcription = " ".join([result.alternatives[0].transcript for result in response.results])
    return full_transcription

def refine_transcription(transcription):
    azure_api_key = "22ec84421ec24230a3638d1b51e3a7dc"  # Consider using environment variables
    azure_api_url = "https://internshala.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"

    headers = {
        "Content-Type": "application/json",
        "api-key": azure_api_key
    }

    payload = {
        "messages": [{"role": "user", "content": transcription}],
        "max_tokens": 500
    }

    response = requests.post(azure_api_url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        refined_text = result["choices"][0]["message"]["content"].strip()
        return refined_text
    else:
        st.error(f"Error correcting transcription: {response.status_code} - {response.text}")
        return ""

def create_audio_from_text(text, output_audio_path):
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    input_text = texttospeech.SynthesisInput(text=text)

    voice_params = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-A"  # Update this to a valid voice name if necessary
    )

    audio_configuration = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(input=input_text, voice=voice_params, audio_config=audio_configuration)

    with open(output_audio_path, "wb") as audio_file:
        audio_file.write(response.audio_content)

def combine_audio_and_video(video_path, audio_path, output_video_path):
    command = f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -map 0:v:0 -map 1:a:0 -shortest {output_video_path}"
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    run_app()
