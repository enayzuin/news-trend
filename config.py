"""
Arquivo de configuração para as APIs utilizadas no projeto.
"""
import os

# Configuração da API OpenAI
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Configuração da NewsAPI
NEWSAPI_API_KEY = os.environ["NEWSAPI_API_KEY"]

# Configuração do WordPress
WORDPRESS_URL = os.environ["WORDPRESS_URL"]
WORDPRESS_USERNAME = os.environ["WORDPRESS_USERNAME"]
WORDPRESS_PASSWORD = os.environ["WORDPRESS_PASSWORD"]

# Configurações gerais
MAX_TRENDS = int(os.environ["MAX_TRENDS"])  # Número máximo de tendências a serem processadas
MAX_NEWS_PER_TREND = int(os.environ["MAX_NEWS_PER_TREND"])  # Número máximo de notícias por tendência
