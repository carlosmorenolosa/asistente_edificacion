# Intelligent Technical Assistant for Construction Chatbot

This repository contains the source code for an intelligent technical assistant chatbot. The chatbot is designed to help users with queries related to construction and building documentation, providing answers based on a specialized knowledge base.

## Functionality

The application is built using Streamlit and provides a web-based interface for users to interact with the chatbot. Key functionalities include:

*   **Natural Language Queries:** Users can ask questions in natural language.
*   **AI-Powered Responses:** Utilizes Google Generative AI (specifically the Gemini 2.0 Flash model for response generation and text-embedding-004 for query understanding) to process queries and generate relevant answers.
*   **Vector Database Integration:** Leverages Pinecone as a vector database to store and efficiently retrieve information from a specialized corpus of construction and building documentation (indexed under "documentacion-edificacion").
*   **Source Attribution:** Displays the source documents from which the information is retrieved, along with a relevance score for each snippet, allowing users to verify the information.
*   **Interactive UI:** Features a user-friendly interface with conversation history, example queries, and visual feedback elements.

## Technologies Used

*   **Python:** The core programming language.
*   **Streamlit:** For building the interactive web application interface.
*   **Google Generative AI:** For large language model capabilities (text generation and embeddings).
*   **Pinecone:** As the vector database for efficient similarity search in the document corpus.

## File Structure

*   `interfaz_chatbot_edificacion.py`: The main Python script containing the Streamlit application logic for the chatbot interface.
*   `requirements.txt`: Lists the necessary Python dependencies for the project. Ensure these are installed before running the application.
*   `caeys_logo_3.png`: Image file for the Caeys logo, used in the application.
*   `README.md`: This file, providing an overview of the project.

## Setup and Running the Application

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Keys:**
    This application requires API keys for Google Generative AI and Pinecone. These should be stored as Streamlit secrets. Create a file `.streamlit/secrets.toml` with the following structure:
    ```toml
    [general]
    genai_api_key = "YOUR_GOOGLE_AI_API_KEY"
    pinecone_api_key = "YOUR_PINECONE_API_KEY"
    ```
    Replace `"YOUR_GOOGLE_AI_API_KEY"` and `"YOUR_PINECONE_API_KEY"` with your actual API keys.

5.  **Ensure Pinecone Index:**
    Make sure you have a Pinecone index named `documentacion-edificacion` populated with your vectorized construction documents. The embedding model used for populating the index should match the one used in the application (`models/text-embedding-004`).

6.  **Run the Streamlit Application:**
    ```bash
    streamlit run interfaz_chatbot_edificacion.py
    ```
    The application should open in your web browser.

## Purpose of the Assistant

This Intelligent Technical Assistant is a specialized tool for professionals in the construction and civil engineering sectors. Its primary goal is to provide quick and accurate answers to technical queries by referencing a dedicated database of norms, technical specifications, and other relevant documentation for building and construction projects. It aims to streamline the process of finding specific information within a vast amount of technical literature.

## Developer

Developed by:

<p align="center">
  <img src="caeys_logo_3.png" alt="Caeys.es Logo" width="200"/>
</p>

## Disclaimer

The information provided by this chatbot is based on the content of its indexed documentation. While it strives for accuracy, users should always cross-reference critical information with original source documents or consult with qualified professionals before making decisions based solely on the assistant's responses. The developers are not liable for any inaccuracies or omissions in the provided information.
