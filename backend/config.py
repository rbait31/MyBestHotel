"""
Конфигурация приложения.
"""
import os
from pathlib import Path

# Загрузить .env из корня проекта (родитель backend/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
