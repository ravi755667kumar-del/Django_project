# ☕ Brew Haven

Brew Haven is a modern, AI-powered e-commerce web application for a tea and coffee shop. Built with Django, this platform goes beyond a simple storefront by integrating advanced Machine Learning (ML) recommendations and a Retrieval-Augmented Generation (RAG) AI Chatbot to provide a highly personalized customer experience.

## ✨ Key Features

*   **🤖 AI-Powered Chatbot (RAG):**
    *   An intelligent assistant built with **LangChain**, **ChromaDB**, and **Groq LLM**.
    *   Uses **FastEmbed (ONNX)** with the `bge-small-en-v1.5` model for lightning-fast, low-memory vector embeddings.
    *   Answers customer queries about the menu, prices, and store policies by retrieving information directly from a local knowledge base (PDF documents).
*   **🌦️ Contextual ML Recommendations:**
    *   Uses a **Random Forest Classification** model trained on global order history.
    *   Fetches real-time live weather data (temperature, humidity, weather category) and time of day.
    *   Dynamically recommends the best drinks and snacks for the exact current weather conditions (e.g., Hot Tea on a rainy day, Iced Coffee on a hot afternoon).
*   **🔒 Secure Authentication:**
    *   Passwordless **Email OTP** login and registration system.
    *   Secure session-based cart management.
*   **📱 Responsive UI/UX:**
    *   Mobile-friendly design with custom CSS.
    *   Interactive cart, order history, and floating chat UI.

## 🛠️ Technology Stack

*   **Backend:** Python, Django
*   **Database:** SQLite (Patched with `pysqlite3-binary` for ChromaDB compatibility)
*   **Machine Learning:** Scikit-learn, Pandas, Joblib
*   **AI/LLM:** LangChain, Groq API (`llama-3-8b-8192` or similar), FastEmbed
*   **Deployment:** Render (Gunicorn)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript

## 🚀 Getting Started (Local Development)

### 1. Prerequisites
Make sure you have Python 3.10+ installed on your machine.

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/Django_project.git
cd Django_project/tea
```

### 3. Create a Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Variables
Create a `.env` file in the root directory and add your API keys:
```env
# Example .env file
OPENAI_API_KEY=your_groq_api_key
WEATHER_API_KEY=your_weather_api_key
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 6. Setup the AI Models
Before running the server, download the FastEmbed model locally so the chatbot can run:
```bash
python download_model.py
```
*(This will download the embedding model into a persistent `fastembed_cache/` folder).*

### 7. Run the Server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser!

## ☁️ Deployment (Render)

This project is optimized for Render's Free Tier (512MB RAM, 0.1 vCPU). 

### Critical Render Configurations:
1.  **Environment Variables:** Make sure to add `HF_TOKEN` (if required) and your Groq/Weather API keys in the Render Dashboard.
2.  **Start Command:** To prevent the server from running Out of Memory (OOM) when loading heavy ML libraries, you **must** restrict Gunicorn to a single worker and use threads. Set your Start Command to:
    ```bash
    cd tea && gunicorn tea.wsgi:application --timeout 120 --workers 1 --threads 4
    ```
    *   `--timeout 120`: Prevents timeout crashes during the heavy initial import of pandas/scikit-learn.
    *   `--workers 1`: Prevents the 512MB RAM limit from being exceeded by duplicating the app.

## 📁 Project Structure

*   `shop/`: Main Django application (Models, Views, URLs).
*   `shop/recommendations/`: Machine Learning logic (`train_model.py`, `predict.py`, `dataset.py`, `weather.py`).
*   `shop/rag.py` & `shop/chat.py`: LLM, Vector Database, and Chatbot logic.
*   `documents/`: The PDF knowledge base the RAG model reads from.
*   `fastembed_cache/`: Local cache directory for the ONNX embedding model.
*   `chroma_db/`: Persistent local vector database storage.
