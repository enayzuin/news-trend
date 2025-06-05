"""
Módulo para obtenção de tendências do Google Trends via Feed RSS.
"""

import feedparser
import logging
import html

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleTrendsRSS:
    """Cliente para obter tendências do Google Trends via Feed RSS."""
    
    def __init__(self, rss_url="https://trends.google.com/trending/rss?geo=BR"):
        """
        Inicializa o cliente RSS do Google Trends.
        
        Args:
            rss_url (str): URL do feed RSS do Google Trends.
        """
        self.rss_url = rss_url
        logger.info(f"Cliente RSS do Google Trends inicializado com URL: {self.rss_url}")
    
    def get_trending_topics(self, max_trends=5):
        """
        Obtém os tópicos em tendência do feed RSS.
        
        Args:
            max_trends (int): Número máximo de tendências a retornar.
            
        Returns:
            list: Lista de tópicos em tendência.
        """
        try:
            logger.info(f"Obtendo tendências do feed RSS: {self.rss_url}")
            
            # Faz o parse do feed RSS
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                logger.warning(f"Erro ao parsear o feed RSS: {feed.bozo_exception}")
                # Tenta continuar mesmo com erro, pode ser um erro não crítico
            
            trends = []
            if feed.entries:
                for entry in feed.entries:
                    # O título da entrada geralmente contém a tendência
                    title = entry.get('title')
                    if title:
                        # Decodifica entidades HTML, se houver
                        decoded_title = html.unescape(title)
                        trends.append(decoded_title)
                        if len(trends) >= max_trends:
                            break
            
            if not trends:
                 logger.warning("Nenhuma tendência encontrada no feed RSS.")
                 return []
                 
            logger.info(f"Obtidas {len(trends)} tendências via RSS: {trends}")
            return trends
            
        except Exception as e:
            logger.error(f"Erro ao obter tendências via RSS: {str(e)}")
            return []

def get_top_trends_rss(max_trends=5):
    """
    Função auxiliar para obter as principais tendências via RSS.
    
    Args:
        max_trends (int): Número máximo de tendências a retornar.
        
    Returns:
        list: Lista de tópicos em tendência.
    """
    client = GoogleTrendsRSS()
    return client.get_trending_topics(max_trends=max_trends)

if __name__ == "__main__":
    # Teste da funcionalidade
    trends = get_top_trends_rss()
    if trends:
        print(f"Top {len(trends)} tendências (via RSS):")
        for i, trend in enumerate(trends, 1):
            print(f"{i}. {trend}")
    else:
        print("Não foi possível obter tendências via RSS.")
