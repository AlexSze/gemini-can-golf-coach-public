import os
import time
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

MEDIA_FOLDER = 'MEDIA'

def __init__():
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)

    load_dotenv()  ## load all the environment variables
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to the media folder and return the file path."""
    file_path = os.path.join(MEDIA_FOLDER, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.read())
    return file_path

def get_insights(video_path):
    """Extract insights from the video using Gemini Flash."""
    st.write(f"Processing video: {video_path}")

    st.write(f"Uploading file...")
    video_file = genai.upload_file(path=video_path)
    st.write(f"Completed upload: {video_file.uri}")

    while video_file.state.name == "PROCESSING":
        st.write('Waiting for video to be processed.')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)
    
    with open("prompt.txt", 'r') as file:
        prompt = file.read()

    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    st.write("Making LLM inference request...")

    if prompt:
        response = model.generate_content([prompt, video_file],
                                    request_options={"timeout": 600})
    else:
        response = "There are no prompt"
    st.write(f'Video processing complete')
    st.subheader("Insights")
    st.write(response.text)
    genai.delete_file(video_file.name)


def app():
    st.title("Gemini Can Golf Coach")

    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        st.video(file_path)
        get_insights(file_path)
        if os.path.exists(file_path):  ## Optional: Removing uploaded files from the temporary location
            os.remove(file_path)

__init__()
app()