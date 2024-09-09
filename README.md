
# Test Case Generator using LLaVA Model with Multi-Shot Prompting

This is a web application that generates detailed testing instructions for various features of an app or website based on uploaded screenshots and text input. The application uses **Cloudinary** to upload and store screenshots and **Groq's LLaVA model** to process both text and image inputs, generating structured test cases.

## Overview

This application allows users to upload screenshots of different features (such as login pages, settings, etc.) along with text input (app or website name), and in response, it generates detailed test cases for each feature.

### Key Features:
- **Image and Text Processing**: The app analyzes screenshots of features and generates corresponding test cases using text and images as input.
- **Multi-shot Prompting**: The prompt includes examples of structured test cases (such as a login page or settings page), helping the model generate consistent and accurate outputs.
- **Cloudinary Integration**: Screenshots are uploaded to Cloudinary in real time, and the image URLs are passed to the Groq API.
- **Streamlit Frontend**: A user-friendly web interface where users can easily upload screenshots and input text.

## Prompting Strategy

We implemented **multi-shot prompting** to improve the quality of the generated test cases. By providing examples of test cases within the prompt, the model learns how to structure its output based on the images and text provided.

### Example of the Prompt:
The model is prompted with:
- A description of a feature (e.g., Login Page).
- Pre-conditions required before testing (e.g., the user must have an account).
- Step-by-step testing instructions.
- Expected outcomes after the test.

This structure guides the LLaVA model to generate consistent outputs for each feature based on the uploaded screenshots.

## Setup Instructions

### Prerequisites:
- **Python**: 3.7 or higher
- **API Keys**: 
  - A Cloudinary API key for image uploading.
  - A Groq API key to access the LLaVA model.

### How to Run:

1. **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install Dependencies**:
    Install the required Python libraries by running:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up API Keys**:
   - Add your Cloudinary API keys:
     ```python
     cloudinary.config(
       cloud_name='your_cloud_name',
       api_key='your_api_key',
       api_secret='your_api_secret'
     )
     ```
   - Add your Groq API key:
     ```python
     client = Groq(api_key="your_groq_api_key")
     ```

4. **Run the Application**:
    ```bash
    streamlit run app.py
    ```

The app will open in your default web browser, allowing you to upload screenshots and provide text inputs.

## Dependencies

- **Streamlit**: For the web interface
- **Cloudinary**: For uploading and hosting images
- **PIL (Pillow)**: For image processing
- **Groq API (httpx)**: For interacting with the LLaVA model

## License

