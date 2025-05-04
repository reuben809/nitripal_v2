import streamlit as st
from transformers import pipeline, AutoModelForSequenceClassification
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.vectorstores import Qdrant
from langchain_text_splitters import CharacterTextSplitter
from langchain.schema.document import Document
from config import Settings
import functools
import torch


# Security decorator for model calls
def safe_model_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"Model error: {str(e)}")
            return [] if func.__name__ == "classify_food_image" else ""

    return wrapper


# Quantized model loader
@st.cache_resource(ttl=3600)
def load_quantized_model():
    return AutoModelForSequenceClassification.from_pretrained(
        Settings.IMAGE_MODEL,
        device_map="auto",
        load_in_8bit=True,
        torch_dtype=torch.float16
    )


@st.cache_resource
def get_embeddings():
    return HuggingFaceInferenceAPIEmbeddings(
        api_key=Settings.HUGGINGFACE_API_KEY,
        model_name=Settings.EMBED_MODEL
    )


@safe_model_call
def classify_food_image(image_data):
    model = load_quantized_model()
    classifier = pipeline("image-classification", model=model)
    return classifier(image_data)


@st.cache_resource
def get_text_model():
    return HuggingFaceEndpoint(
        repo_id=Settings.TEXT_MODEL,
        temperature=0.7,
        max_length=1024,
        huggingfacehub_api_token=Settings.HUGGINGFACE_API_KEY,
        model_kwargs={"device_map": "auto"}
    )


@safe_model_call
def generate_text(prompt, _llm=None):
    llm = _llm or get_text_model()
    return llm(prompt)


def create_qdrant_from_text(text):
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = [Document(page_content=x) for x in text_splitter.split_text(text)]

    vectorstore = Qdrant.from_documents(
        docs,
        get_embeddings(),
        location=":memory:",
        collection_name="user_health_data"
    )
    return vectorstore