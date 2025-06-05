"""
Script principal para execução do pipeline completo de automação de conteúdo.

Este script realiza as seguintes etapas:
1. Obtém as tendências atuais do Google Trends
2. Busca notícias relacionadas a cada tendência
3. Reescreve o conteúdo das notícias usando a API da OpenAI
4. Gera uma imagem relevante para cada artigo
5. Publica os artigos reescritos com imagem no WordPress
"""

import os
import logging
import time
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# Importa os módulos do projeto
from config import (
    OPENAI_API_KEY, 
    NEWSAPI_API_KEY, 
    WORDPRESS_URL, 
    WORDPRESS_USERNAME, 
    WORDPRESS_PASSWORD,
    MAX_TRENDS,
    MAX_NEWS_PER_TREND
)
from trends_utils import get_top_trends_rss as get_top_trends
from news_utils import get_news_for_trend, NewsScraperClient
from openai_utils import rewrite_article_content
from wordpress_utils import publish_article_to_wordpress
from image_utils import generate_image_for_article

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_output_directory():
    """Cria diretório para armazenar os resultados."""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def save_article_to_file(title, content, output_dir, prefix="article"):
    """Salva o conteúdo de um artigo em um arquivo."""
    # Cria um nome de arquivo baseado no título
    safe_title = "".join(c if c.isalnum() else "_" for c in title)
    safe_title = safe_title[:50]  # Limita o tamanho
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}_{safe_title}.html"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"Artigo salvo em: {filepath}")
    return filepath

def fetch_article_content(url):
    """Obtém o conteúdo HTML de um artigo a partir da URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Obtendo conteúdo do artigo: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.text
    except Exception as e:
        logger.error(f"Erro ao obter conteúdo do artigo {url}: {str(e)}")
        return None

def extract_article_title_from_html(html_content):
    """Extrai o título do artigo a partir do HTML."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Tenta diferentes seletores comuns para títulos
        title_selectors = [
            'h1', 
            'h1.article-title', 
            'h1.entry-title', 
            'h1.post-title',
            'article h1',
            '.article-header h1',
            '.post-header h1'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.text.strip():
                return title_elem.text.strip()
        
        # Fallback para a tag title
        if soup.title:
            return soup.title.text.strip()
        
        return None
    except Exception as e:
        logger.error(f"Erro ao extrair título do HTML: {str(e)}")
        return None

def run_pipeline():
    """Executa o pipeline completo."""
    output_dir = create_output_directory()
    results = []
    
    try:
        # Etapa 1: Obter tendências do Google Trends
        logger.info("Obtendo tendências do Google Trends...")
        trends = get_top_trends(max_trends=MAX_TRENDS)
        
        if not trends:
            logger.error("Não foi possível obter tendências. Encerrando o pipeline.")
            return False
        
        logger.info(f"Tendências obtidas: {trends}")
        
        # Salva as tendências em um arquivo
        with open(os.path.join(output_dir, "trends.json"), "w", encoding="utf-8") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "trends": trends}, f, ensure_ascii=False, indent=2)
        
        # Etapa 2-5: Para cada tendência, buscar notícias, reescrever, gerar imagem e publicar
        for i, trend in enumerate(trends, 1):
            logger.info(f"Processando tendência {i}/{len(trends)}: '{trend}'")
            
            # Busca notícias relacionadas à tendência
            news_articles = get_news_for_trend(trend, api_key=NEWSAPI_API_KEY, max_news=MAX_NEWS_PER_TREND)
            
            if not news_articles:
                logger.warning(f"Nenhuma notícia encontrada para '{trend}'. Pulando para a próxima tendência.")
                continue
            
            logger.info(f"Encontradas {len(news_articles)} notícias para '{trend}'")
            
            # Processa cada notícia
            for j, article in enumerate(news_articles, 1):
                article_title = article.get('title', '')
                article_url = article.get('url', '')
                source_name = article.get('source', {}).get('name', 'Fonte desconhecida')
                
                if not article_url:
                    logger.warning(f"URL não encontrada para o artigo {j}. Pulando.")
                    continue
                
                logger.info(f"Processando artigo {j}/{len(news_articles)}: '{article_title}'")
                
                # Obtém o conteúdo HTML do artigo
                html_content = fetch_article_content(article_url)
                
                if not html_content:
                    logger.warning(f"Não foi possível obter o conteúdo do artigo. Pulando.")
                    continue
                
                # Verifica se o título está presente no HTML, caso contrário usa o título da API
                extracted_title = extract_article_title_from_html(html_content) or article_title
                
                # Reescreve o conteúdo usando a API da OpenAI
                try:
                    logger.info(f"Reescrevendo artigo: '{extracted_title}'")
                    rewritten_content = rewrite_article_content(
                        html_content, 
                        extracted_title, 
                        source_name, 
                        OPENAI_API_KEY
                    )
                    
                    if not rewritten_content:
                        logger.warning(f"Falha ao reescrever o artigo. Pulando.")
                        continue
                    
                    # Extrai o título do conteúdo reescrito
                    soup = BeautifulSoup(rewritten_content, 'html.parser')
                    h1_tag = soup.find('h1')
                    rewritten_title = h1_tag.text.strip() if h1_tag else f"Tendência: {trend} - {extracted_title}"
                    
                    # Salva o artigo reescrito em um arquivo
                    file_path = save_article_to_file(rewritten_title, rewritten_content, output_dir)
                    
                    # Gera uma imagem para o artigo
                    logger.info(f"Gerando imagem para o artigo: '{rewritten_title}'")
                    image_path = generate_image_for_article(
                        rewritten_title,
                        rewritten_content,
                        output_dir,
                        OPENAI_API_KEY
                    )
                    
                    # Publica o artigo no WordPress
                    if WORDPRESS_URL and WORDPRESS_USERNAME and WORDPRESS_PASSWORD:
                        logger.info(f"Publicando artigo no WordPress: '{rewritten_title}'")
                        
                        # Adiciona categorias e tags baseadas na tendência
                        categories = ["Tendências", "Notícias"]
                        tags = [trend] + trend.split()
                        
                        post_id = publish_article_to_wordpress(
                            rewritten_title,
                            rewritten_content,
                            WORDPRESS_URL,
                            WORDPRESS_USERNAME,
                            WORDPRESS_PASSWORD,
                            featured_image=image_path,  # Adiciona a imagem como destaque
                            categories=categories,
                            tags=tags
                        )
                        
                        if post_id:
                            logger.info(f"Artigo publicado com sucesso! ID: {post_id}")
                            results.append({
                                "trend": trend,
                                "title": rewritten_title,
                                "file_path": file_path,
                                "image_path": image_path,
                                "wordpress_id": post_id,
                                "status": "published"
                            })
                        else:
                            logger.warning(f"Falha ao publicar o artigo no WordPress.")
                            results.append({
                                "trend": trend,
                                "title": rewritten_title,
                                "file_path": file_path,
                                "image_path": image_path,
                                "status": "not_published"
                            })
                    else:
                        logger.info("Credenciais do WordPress não configuradas. Artigo não publicado.")
                        results.append({
                            "trend": trend,
                            "title": rewritten_title,
                            "file_path": file_path,
                            "image_path": image_path,
                            "status": "not_published_no_credentials"
                        })
                    
                    # Pausa para evitar sobrecarga nas APIs
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"Erro ao processar artigo '{article_title}': {str(e)}")
                    continue
            # Pausa entre tendências para evitar sobrecarga nas APIs
            time.sleep(5)
            # Adicione este código para remover os arquivos:
            if post_id and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Arquivo HTML removido: {file_path}")
                except Exception as e:
                    logger.warning(f"Não foi possível remover o arquivo HTML: {str(e)}")

            if post_id and image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    logger.info(f"Arquivo de imagem removido: {image_path}")
                except Exception as e:
                    logger.warning(f"Não foi possível remover o arquivo de imagem: {str(e)}")
        
        # Salva os resultados em um arquivo
        results_file = os.path.join(output_dir, "results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_processed": len(results),
                "results": results
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Pipeline concluído. Resultados salvos em: {results_file}")
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a execução do pipeline: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando pipeline de automação de conteúdo...")
    success = run_pipeline()
    
    if success:
        logger.info("Pipeline executado com sucesso!")
    else:
        logger.error("Falha na execução do pipeline.")