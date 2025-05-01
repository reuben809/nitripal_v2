import streamlit as st
from transformers import pipeline
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.vectorstores import Qdrant
from langchain_text_splitters import CharacterTextSplitter
from langchain.schema.document import Document
from config import Settings
import os
import time
import functools

def safe_model_call(func):
    """Decorator for handling model API errors gracefully"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"Error calling model: {str(e)}")
            # Return a default value appropriate to the function
            if func.__name__ == "classify_food_image":
                return []
            elif func.__name__ == "generate_text":
                return "I'm sorry, I couldn't generate a response at this time. Please try again later."
            elif func.__name__ == "create_embeddings":
                return None
            else:
                return None
    return wrapper

@st.cache_resource
def get_huggingface_api_key():
    """Get HuggingFace API key from session state or env vars"""
    return st.session_state.get("apikey", os.environ.get("HUGGINGFACE_API_KEY", ""))

@st.cache_resource
def load_food_classification_model():
    """Load and cache the food classification model"""
    return pipeline("image-classification", model=Settings.IMAGE_MODEL)

@safe_model_call
def classify_food_image(image_data):
    """Classify food in an image using the HuggingFace model"""
    classifier = load_food_classification_model()
    results = classifier(image_data)
    return results

@st.cache_resource
def load_text_model():
    """Load and cache the text generation model"""
    api_key = get_huggingface_api_key()
    return HuggingFaceEndpoint(
        repo_id=Settings.TEXT_MODEL,
        max_length=1024,
        temperature=0.5,
        huggingfacehub_api_token=api_key
    )

@safe_model_call
def generate_text(prompt, max_length=1024, temperature=0.5):
    """Generate text using the HuggingFace model"""
    llm = load_text_model()
    result = llm(prompt, max_tokens=max_length, temperature=temperature)
    return result

@st.cache_resource
def load_embedding_model():
    """Load and cache the embedding model"""
    api_key = get_huggingface_api_key()
    return HuggingFaceInferenceAPIEmbeddings(
        api_key=api_key,
        model_name=Settings.EMBED_MODEL
    )

@safe_model_call
def create_embeddings(texts):
    """Create embeddings for a list of texts"""
    embeddings = load_embedding_model()
    return embeddings.embed_documents(texts)

def create_qdrant_from_text(text):
    """Create a Qdrant vectorstore from text chunks"""
    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=50, chunk_overlap=20)
    docs = [Document(page_content=x) for x in text_splitter.split_text(text)]
    
    # Get embeddings
    embeddings = load_embedding_model()
    
    # Create vectorstore
    return Qdrant.from_documents(
        docs,
        embeddings,
        location=":memory:",
        collection_name="user_documents",
    )
