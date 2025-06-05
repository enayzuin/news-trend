"""
Módulo para geração e obtenção de imagens para os artigos.
"""

import os
import logging
import requests
import json
import base64
import time
from io import BytesIO
from PIL import Image
from urllib.parse import quote_plus

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageGenerator:
    """Cliente para gerar ou obter imagens para os artigos."""
    
    def __init__(self, openai_api_key):
        """
        Inicializa o cliente de geração de imagens.
        
        Args:
            openai_api_key (str): Chave de API para a OpenAI
        """
        self.openai_api_key = openai_api_key
        self.headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        logger.info("Cliente de geração de imagens inicializado")
    
    def generate_image_with_openai(self, prompt, output_dir, size="1024x1024", quality="standard"):
        """
        Gera uma imagem usando a API DALL-E da OpenAI.
        
        Args:
            prompt (str): Descrição da imagem a ser gerada
            output_dir (str): Diretório para salvar a imagem
            size (str): Tamanho da imagem (1024x1024, 1024x1792, 1792x1024)
            quality (str): Qualidade da imagem (standard, hd)
            
        Returns:
            str: Caminho para a imagem gerada ou None em caso de erro
        """
        try:
            logger.info(f"Gerando imagem com DALL-E para: '{prompt}'")
            
            # Prepara a requisição para a API DALL-E
            url = "https://api.openai.com/v1/images/generations"
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": size,
                "quality": quality,
                "response_format": "url"
            }
            
            # Faz a requisição para a API
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            # Processa a resposta
            result = response.json()
            image_url = result["data"][0]["url"]
            
            # Baixa a imagem
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Salva a imagem
            safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30])
            timestamp = int(time.time())
            image_path = os.path.join(output_dir, f"image_{timestamp}_{safe_prompt}.png")
            
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            logger.info(f"Imagem gerada e salva em: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar imagem com DALL-E: {str(e)}")
            return self.search_image_alternative(prompt, output_dir)
    
    def search_image_alternative(self, query, output_dir):
        """
        Busca uma imagem alternativa usando APIs gratuitas quando a geração com DALL-E falha.
        
        Args:
            query (str): Termo de busca para a imagem
            output_dir (str): Diretório para salvar a imagem
            
        Returns:
            str: Caminho para a imagem obtida ou None em caso de erro
        """
        try:
            # Tenta primeiro com a API do Unsplash
            logger.info(f"Buscando imagem alternativa para: '{query}'")
            
            # Formata a consulta para URL
            encoded_query = quote_plus(query)
            
            # Tenta com a API do Unsplash (sem chave, limitado)
            url = f"https://source.unsplash.com/1600x900/?{encoded_query}"
            
            response = requests.get(url, allow_redirects=True)
            if response.status_code == 200:
                # Salva a imagem
                safe_query = "".join(c if c.isalnum() else "_" for c in query[:30])
                timestamp = int(time.time())
                image_path = os.path.join(output_dir, f"image_{timestamp}_{safe_query}.jpg")
                
                with open(image_path, "wb") as f:
                    f.write(response.content)
                
                logger.info(f"Imagem alternativa obtida e salva em: {image_path}")
                return image_path
            
            logger.warning(f"Não foi possível obter imagem alternativa para: '{query}'")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar imagem alternativa: {str(e)}")
            return None
    
    def create_image_prompt(self, title, content=None):
        """
        Cria um prompt para geração de imagem baseado no título e conteúdo do artigo.
        
        Args:
            title (str): Título do artigo
            content (str, optional): Conteúdo do artigo
            
        Returns:
            str: Prompt formatado para geração de imagem
        """
        # Base do prompt
        prompt = f"Crie uma imagem fotorrealista e profissional para ilustrar uma notícia com o título: '{title}'. "
        
        # Adiciona instruções específicas
        prompt += "A imagem deve ser adequada para um site de notícias, com estilo jornalístico, "
        prompt += "alta qualidade visual, sem texto ou marcas d'água. "
        
        # Adiciona contexto baseado no conteúdo, se disponível
        if content:
            # Extrai algumas palavras-chave do conteúdo
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()
            
            # Limita o tamanho para não sobrecarregar o prompt
            if len(text_content) > 200:
                text_content = text_content[:200]
            
            prompt += f"Contexto adicional do artigo: {text_content}"
        
        return prompt

def generate_image_for_article(title, content, output_dir, openai_api_key):
    """
    Função auxiliar para gerar uma imagem para um artigo.
    
    Args:
        title (str): Título do artigo
        content (str): Conteúdo HTML do artigo
        output_dir (str): Diretório para salvar a imagem
        openai_api_key (str): Chave de API para a OpenAI
        
    Returns:
        str: Caminho para a imagem gerada ou None em caso de erro
    """
    generator = ImageGenerator(openai_api_key)
    prompt = generator.create_image_prompt(title, content)
    return generator.generate_image_with_openai(prompt, output_dir)

if __name__ == "__main__":
    # Teste da funcionalidade
    from config import OPENAI_API_KEY
    
    # Cria diretório de saída para os testes
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Exemplo de título e conteúdo
    test_title = "Brasil vence Argentina em jogo decisivo da Copa América"
    test_content = """
    <article>
        <h2>Brasil vence Argentina em jogo decisivo da Copa América</h2>
        <p>Em partida realizada ontem no Maracanã, a seleção brasileira venceu a Argentina por 2 a 1.</p>
        <p>Os gols foram marcados por Neymar e Vinicius Jr., enquanto Messi descontou para os argentinos.</p>
        <p>Com essa vitória, o Brasil se classifica para a próxima fase da competição.</p>
    </article>
    """
    
    # Gera uma imagem para o artigo
    image_path = generate_image_for_article(test_title, test_content, output_dir, OPENAI_API_KEY)
    
    if image_path:
        print(f"Imagem gerada com sucesso: {image_path}")
    else:
        print("Não foi possível gerar a imagem.")