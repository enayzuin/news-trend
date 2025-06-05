"""
Módulo para busca de notícias relacionadas às tendências.
"""

import requests
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsAPIClient:
    """Cliente para interagir com a NewsAPI."""
    
    def __init__(self, api_key):
        """
        Inicializa o cliente da NewsAPI.
        
        Args:
            api_key (str): Chave de API para a NewsAPI
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        logger.info("Cliente da NewsAPI inicializado")
    
    def search_news(self, query, language='pt', sort_by='relevancy', page_size=5, page=1):
        """
        Busca notícias relacionadas a uma consulta.
        
        Args:
            query (str): Termo de busca
            language (str): Idioma das notícias (padrão: 'pt' para português)
            sort_by (str): Critério de ordenação (relevancy, popularity, publishedAt)
            page_size (int): Número de resultados por página
            page (int): Número da página
            
        Returns:
            dict: Resultados da busca
        """
        try:
            # Calcula a data de uma semana atrás para limitar os resultados
            today = (datetime.now()).strftime('%Y-%m-%d')
            
            endpoint = f"{self.base_url}/everything"
            params = {
                'q': query,
                'language': language,
                'sortBy': sort_by,
                'pageSize': page_size,
                'page': page,
                'from': today,
                'apiKey': self.api_key
            }
            
            logger.info(f"Buscando notícias para '{query}'")
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Encontradas {data.get('totalResults', 0)} notícias para '{query}'")
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à NewsAPI: {str(e)}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Erro ao buscar notícias para '{query}': {str(e)}")
            return {"status": "error", "message": str(e)}

class NewsScraperClient:
    """Cliente alternativo para busca de notícias usando web scraping."""
    
    def __init__(self):
        """Inicializa o cliente de scraping de notícias."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logger.info("Cliente de scraping de notícias inicializado")
    
    def search_google_news(self, query, num_results=5):
        """
        Busca notícias no Google News.
        
        Args:
            query (str): Termo de busca
            num_results (int): Número máximo de resultados
            
        Returns:
            list: Lista de notícias encontradas
        """
        try:
            # Formata a consulta para URL
            query = query.replace(' ', '+')
            url = f"https://news.google.com/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
            
            logger.info(f"Buscando notícias no Google News para '{query}'")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('article')
            
            results = []
            for i, article in enumerate(articles[:num_results]):
                try:
                    title_element = article.select_one('h3 a, h4 a')
                    if not title_element:
                        continue
                        
                    title = title_element.text
                    
                    # Extrai o link da notícia
                    article_url = title_element.get('href', '')
                    if article_url.startswith('./'):
                        article_url = f"https://news.google.com{article_url[1:]}"
                    
                    # Tenta extrair a fonte e data
                    source_time = article.select_one('time')
                    source = source_time.parent.text.split('·')[0].strip() if source_time else "Fonte desconhecida"
                    published_at = source_time.get('datetime', '') if source_time else ""
                    
                    results.append({
                        'title': title,
                        'url': article_url,
                        'source': {
                            'name': source
                        },
                        'publishedAt': published_at,
                        'content': None  # Será preenchido posteriormente se necessário
                    })
                except Exception as e:
                    logger.warning(f"Erro ao processar artigo: {str(e)}")
                    continue
            
            logger.info(f"Encontradas {len(results)} notícias no Google News para '{query}'")
            return {"articles": results, "status": "ok", "totalResults": len(results)}
        except Exception as e:
            logger.error(f"Erro ao buscar notícias no Google News para '{query}': {str(e)}")
            return {"articles": [], "status": "error", "message": str(e), "totalResults": 0}
    
    def fetch_article_content(self, url):
        """
        Obtém o conteúdo de um artigo a partir da URL.
        
        Args:
            url (str): URL do artigo
            
        Returns:
            str: Conteúdo HTML do artigo
        """
        try:
            logger.info(f"Obtendo conteúdo do artigo: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            logger.error(f"Erro ao obter conteúdo do artigo {url}: {str(e)}")
            return None

def get_news_for_trend(trend, api_key=None, max_news=3):
    """
    Função auxiliar para obter notícias relacionadas a uma tendência.
    
    Args:
        trend (str): Tendência para buscar notícias
        api_key (str): Chave de API para a NewsAPI (opcional)
        max_news (int): Número máximo de notícias a retornar
        
    Returns:
        list: Lista de notícias relacionadas à tendência
    """
    # Tenta primeiro com a NewsAPI se a chave for fornecida
    if api_key:
        client = NewsAPIClient(api_key)
        results = client.search_news(trend, page_size=max_news)
        
        if results.get("status") == "ok" and results.get("totalResults", 0) > 0:
            return results.get("articles", [])
    
    # Caso contrário, ou se não encontrar resultados, usa o scraper alternativo
    scraper = NewsScraperClient()
    results = scraper.search_google_news(trend, num_results=max_news)
    
    return results.get("articles", [])

if __name__ == "__main__":
    # Teste da funcionalidade
    from config import NEWSAPI_API_KEY
    
    trend = "Copa do Brasil"
    news = get_news_for_trend(trend, api_key=NEWSAPI_API_KEY)
    
    print(f"Notícias para '{trend}':")
    for i, article in enumerate(news, 1):
        print(f"{i}. {article['title']} ({article['source']['name']})")
        print(f"   URL: {article['url']}")
        print(f"   Data: {article['publishedAt']}")
        print("")
