# video-audio-correction

This is a **Python** and **Streamlit** web application that processes video files to correct their audio content. The tool extracts the audio from a video, transcribes it, refines the transcription using GPT-4o, generates corrected audio from the refined transcription, and merges the corrected audio back into the video.

## Features
- Upload video files (supports `mp4`, `avi`, `mov` formats)
- Extract audio from the uploaded video
- Transcribe audio using **Google Cloud Speech-to-Text API**
- Refine transcription using **GPT-4o** via Azure API
- Generate audio from corrected transcription using **Google Cloud Text-to-Speech API**
- Merge corrected audio back into the video

## Technologies Used
- **Python**
- **Streamlit** for creating the web interface
- **MoviePy** for video and audio manipulation
- **Google Cloud Speech-to-Text** for transcribing audio
- **Google Cloud Text-to-Speech** for generating audio
- **Azure GPT-4o** for refining transcription text

## Installation

1. Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Set up a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Add your Google Cloud and Azure API credentials to **Streamlit secrets**:

    In `.streamlit/secrets.toml`, add:

    ```bash
    [general]
    private_key = "YOUR_PRIVATE_KEY"
    client_email = "YOUR_CLIENT_EMAIL"
    project_id = "YOUR_PROJECT_ID"
    ```
   
    Replace the `YOUR_PRIVATE_KEY`, `YOUR_CLIENT_EMAIL`, and `YOUR_PROJECT_ID` with your Google Cloud credentials.

    Additionally, set your Azure GPT-4o API key and endpoint in the code itself (ideally use environment variables).

## How to Run

To run the Streamlit app locally, use:

```bash
streamlit run app.py
'''

## Environment Variables

For the app to work properly, you need to configure the following environment variables:

- GOOGLE_APPLICATION_CREDENTIALS: Path to your Google Cloud credentials file or use the private key setup in the Streamlit secrets.
- AZURE_API_KEY: Your Azure OpenAI API key for GPT-4o.
- AZURE_API_URL: Your Azure OpenAI GPT-4o API endpoint URL
