"""
Конфигурация приложения.
"""
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
