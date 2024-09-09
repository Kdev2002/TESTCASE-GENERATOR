import time
import streamlit as st
import cloudinary
import cloudinary.uploader
from groq import Groq
from PIL import Image
import io
import logging

# Set up logging
logging.basicConfig(
    filename='app.log', 
    filemode='w', 
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Cloudinary Configuration
cloudinary.config(
  cloud_name='xxxxx',  # Your Cloudinary Cloud Name
  api_key='xxxxxxxxxxxxxxxx',  # Your Cloudinary API Key
  api_secret='xxxxxxxxxxxxxxxxxxxxxxx'  # Your Cloudinary API Secret
)

# Initialize Groq client
client = Groq(api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")  # Your Groq API Key

def upload_image_to_cloudinary(image_file):
    """
    Uploads image to Cloudinary and returns the image URL.
    Includes logging for errors.
    """
    try:
        upload_result = cloudinary.uploader.upload(image_file)
        logging.info(f"Image uploaded successfully: {upload_result['url']}")
        return upload_result['url']
    except Exception as e:
        logging.error(f"Error uploading image to Cloudinary: {e}")
        return None

def generate_testing_instructions(app_name, image_urls):
    """
    Creates the testing instruction message content and sends it to Groq's LLaVA model.
    Includes multi-shot prompting for more reliable outputs.
    """
    # Prepare the prompt with a multi-shot example
    message_content = f"Analyze each image carefully and generate detailed testing instructions for the features of the app: {app_name}. For each image, please follow the example below and describe the visual elements, extract key features, and provide testing instructions as follows:  "

    # Adding two examples of features based on images
    message_content += (
        "### Example 1: Login Page Feature "
        "Image URL: https://assets.justinmind.com/wp-content/uploads/2020/01/mangools-login-form.png "
        "1. *Description*: This is the login page where users enter their credentials. "
        "2. *Pre-conditions*: The user must have an account or create one. "
        "3. *Testing Steps*: "
        "   - Step 1: Open the login page. "
        "   - Step 2: Enter a valid email and password. "
        "   - Step 3: Click the login button. "
        "4. *Expected Result*: The user is logged in and redirected to the dashboard.  "
        
        "### Example 2: Settings Page Feature "
        "Image URL: https://i.pinimg.com/736x/ac/b2/34/acb2344dc9d0266b0226d7c53cbeb963.jpg "
        "1. *Description*: This is the settings page where users can adjust account settings. "
        "2. *Pre-conditions*: The user must be logged into their account. "
        "3. *Testing Steps*: "
        "   - Step 1: Navigate to the settings page. "
        "   - Step 2: Change the notification settings. "
        "   - Step 3: Save the changes. "
        "4. *Expected Result*: The settings are saved and reflected in the account. "
    )

    # Add the actual features and images provided by the user
    for i, url in enumerate(image_urls):
        message_content += f"### Feature {i + 1}: "
        message_content += (
            "1. *Description*: Describe the main purpose of this feature based on the image. "
            "2. *Pre-conditions*: What conditions must be met before testing this feature? "
            "3. *Testing Steps*: Provide step-by-step instructions to test this feature. "
            "4. *Expected Result*: Describe the expected outcome after testing.  "
        )

    # Check for token limit
    if len(message_content) > 20000:
        st.warning("Message too large to process.")
        logging.warning("Message content exceeds the token limit.")
        return "Message too large to process."

    # Retry mechanism for API request
    for attempt in range(3):
        try:
            completion = client.chat.completions.create(
                model="llava-v1.5-7b-4096-preview",
                messages=[
                    {"role": "user", "content": message_content}
                ],
                temperature=1,  # Lower temperature for more deterministic output
                max_tokens=4024,
                top_p=1,
                stream=False,
                stop=None
            )
            results = [choice.message.content for choice in completion.choices]
            logging.info("Successfully generated testing instructions.")
            return " ".join(results)
        except Exception as e:
            logging.error(f"Error communicating with Groq API: {e}")
            if "rate limit" in str(e).lower():
                wait_time = 120
                st.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                logging.warning("Rate limit exceeded. Retrying...")
                time.sleep(wait_time)
            else:
                st.error(f"Error generating instructions: {e}")
                return None

# Streamlit frontend
st.title('App Testing Instructions Generator')

# User input for app name
app_name = st.text_input('App or Website Name', placeholder='Enter the name of the app or website')

# File uploader for screenshots
uploaded_files = st.file_uploader("Upload Screenshots of Features", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"{len(uploaded_files)} file(s) uploaded.")

if st.button('Generate Testing Instructions'):
    if uploaded_files and app_name:
        st.write("Processing your request...")
        logging.info(f"App name: {app_name}")
        logging.info(f"Number of files uploaded: {len(uploaded_files)}")

        # Process each uploaded image
        image_urls = []
        for image_file in uploaded_files:
            image = Image.open(image_file)

            # Convert the image to RGB mode if it's in RGBA
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            # Optionally, you can compress the image before uploading
            compressed_image = io.BytesIO()
            image.save(compressed_image, format="JPEG", quality=75)  # Compress image to JPEG with 75% quality
            compressed_image.seek(0)
            
            # Upload image to Cloudinary and get URL
            image_url = upload_image_to_cloudinary(compressed_image)
            if image_url:
                image_urls.append(image_url)

        if image_urls:
            try:
                # Generate testing instructions using Groq API
                instructions = generate_testing_instructions(app_name, image_urls)
                if instructions:
                    st.success("Testing instructions generated successfully.")
                    st.text_area("Generated Testing Instructions", value=instructions, height=300)
            except Exception as e:
                logging.error(f"Error generating instructions: {e}")
                st.error(f"Error generating instructions: {e}")
    else:
        logging.warning("No files uploaded or app name missing.")
        st.error("Please upload screenshots and enter the app or website name to proceed.")
