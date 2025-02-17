import os
from dotenv import find_dotenv, load_dotenv
import google.generativeai as genai
import streamlit as st
import logging

# Set up logging
logging.basicConfig(filename="hemanbot.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logging.info("HeManBot started successfully.")

# Load environment variables
load_dotenv(find_dotenv())

# Configure Gemini API with the API key from environment variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Streamlit app
st.title("HeManBot 🦸‍♂️")
st.header("Your Friendly, Wholesome, and Hilarious Tweet Bot")

# Step 1: Describe Your Tweet
st.subheader("1. Describe Your Tweet")
description = st.text_area(
    "Enter your tweet description or content:",
    height=100,
    placeholder="e.g., Feeling proud after cleaning my room.",
    help="Write a short description or paste an existing tweet to generate new ones."
)

# Step 2: Select Your Vibe
st.subheader("2. Select Your Vibe")
voice_options = st.multiselect(
    label="Choose the vibe of your tweet:",
    options=["Wholesome", "Funny", "Motivational", "Relatable", "Playful"],
    default=["Wholesome"],  # Default selection
    help="Select one or more vibes for your tweet."
)

# Step 3: Customize Your Tweet
st.subheader("3. Customize Your Tweet")

# Use columns for better layout
col1, col2 = st.columns(2)

with col1:
    # Slider for tweet length
    tweet_length = st.slider(
        "Max Tweet Length",
        min_value=50,
        max_value=280,
        value=280,
        help="Set the maximum character limit for your tweet."
    )

with col2:
    # Language selection (Hindi, English, Japanese)
    language = st.selectbox(
        "Choose the language for your tweet:",
        options=["English", "Hindi", "Japanese"],
        index=0,  # Default to English
        help="Select the language for your tweet."
    )

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-pro")

# Function to generate a tweet
def generate_tweet(description, vibe, max_length, language):
    """Generate a tweet based on the description, selected vibe, max length, and language."""
    prompt = f"""You are HeManBot, a friendly and wholesome Twitter bot. Write a tweet in {language} based on the following description: {description}.
    The vibe of the tweet should be: {vibe}.
    - Use simple and easy-to-understand language that everyone can relate to.
    - Avoid inappropriate content, offensive language, or anything that could make anyone uncomfortable.
    - Keep it lighthearted, funny, and positive.
    - Add 1-2 relevant emojis and 1-2 hashtags at the end.
    - Ensure the tweet is under {max_length} characters.
    - Ensure the content is safe, family-friendly, and appropriate for all audiences.
    Example: "When you finally finish a task you've been avoiding: 'I deserve a medal 🏅 and a nap 😴.' #AdultingWin #SmallVictories"
    """
    try:
        response = model.generate_content(prompt)
        if response.candidates and response.candidates[0].finish_reason == 1:  # Check if response is valid
            tweet = response.text
            if len(tweet) <= max_length:
                return tweet
            else:
                return "Oops! The tweet is too long. Try a shorter description or a different vibe."
        else:
            return "Sorry, I couldn't generate a tweet. The input might have triggered a safety filter. Please try rephrasing or using a different description."
    except Exception as e:
        logging.error(f"Error generating tweet: {e}")
        return f"An error occurred: {e}"

# Function to save tweets to a file
def save_tweets_to_file(tweet_one, tweet_two, filename="generated_tweets.txt"):
    """Save generated tweets to a file with UTF-8 encoding."""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"Tweet 1: {tweet_one}\n")
            f.write(f"Tweet 2: {tweet_two}\n")
        st.success(f"Tweets saved to '{filename}'!")
    except Exception as e:
        st.error(f"An error occurred while saving the tweets: {e}")

# Generate tweets on button click
if st.button("Generate Tweet") or st.button("Retry"):
    if not description:
        st.warning("Please enter a description for your tweet!")
    elif not voice_options:
        st.warning("Please select at least one vibe!")
    else:
        with st.spinner("HeManBot is crafting your tweet... 🦸‍♂️"):
            # Generate the first tweet
            st.session_state.tweet_one = generate_tweet(description, ", ".join(voice_options), tweet_length, language)
            st.success("**Tweet 1:**")
            st.write(st.session_state.tweet_one)

            st.divider()

            # Generate the second tweet
            st.session_state.tweet_two = generate_tweet(description, ", ".join(voice_options), tweet_length, language)
            st.success("**Tweet 2:**")
            st.write(st.session_state.tweet_two)

# Save tweets to a file
if st.button("Save Tweets"):
    if "tweet_one" in st.session_state and "tweet_two" in st.session_state:  # Check if tweets were generated
        save_tweets_to_file(st.session_state.tweet_one, st.session_state.tweet_two)
    else:
        st.warning("No tweets generated yet. Please generate tweets first!")