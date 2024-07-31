import streamlit as st
from PIL import Image
from openai import OpenAI
import io
import base64
import requests

api_key = st.secrets["openai_api_key"]

print(api_key)

openai_client = OpenAI(api_key=api_key)

prompt = "I am providing you with the input form screenshot, you just need to provide me with the label and its values in the input boxed in the json format."


def extract_metadata(image_bytes):
    print("Extracting metadata...")

    # Getting the base64 string
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    requests_url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
    }

    response = requests.post(
        requests_url,
        headers=headers,
        json=payload,
    )

    response = response.json()
    response_choices = response.get("choices", [])
    response_message = (
        response_choices[0].get("message", {}) if response_choices else {}
    )
    response_content = response_message.get("content", {})
    return response if "error" in response.keys() else {"metadata": response_content}


st.title("Form Metadata Extractor")

uploaded_file = st.file_uploader(
    "Choose an image...",
    type=["jpg", "jpeg", "png"],
)

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.")

    # Extract metadata from the image
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=image.format)
    image_bytes = image_bytes.getvalue()

    st.write("Extracting metadata...")
    metadata = extract_metadata(image_bytes)

    st.write("Metadata:")
    st.json(metadata)
