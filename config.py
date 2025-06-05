"""
Arquivo de configuração para as APIs utilizadas no projeto.
"""

import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuração da NewsAPI
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")

# Configuração do WordPress
WORDPRESS_URL = os.getenv("WORDPRESS_URL")
WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD")

# Configurações gerais
MAX_TRENDS = int(os.getenv("MAX_TRENDS", 5))  # Número máximo de tendências a serem processadas
MAX_NEWS_PER_TREND = int(os.getenv("MAX_NEWS_PER_TREND", 3))  # Número máximo de notícias por tendência
