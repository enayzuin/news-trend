"""
Módulo para reescrita de conteúdo de notícias usando a API da OpenAI.
"""

import openai
import logging
import re
from bs4 import BeautifulSoup

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAIClient:
    """Cliente para interagir com a API da OpenAI."""
    
    def __init__(self, api_key):
        """
        Inicializa o cliente da OpenAI.
        
        Args:
            api_key (str): Chave de API para a OpenAI
        """
        openai.api_key = api_key
        logger.info("Cliente da OpenAI inicializado")
    
    def rewrite_article(self, html_content, title, source_name):
        """
        Reescreve o conteúdo de um artigo usando a API da OpenAI.
        
        Args:
            html_content (str): Conteúdo HTML do artigo original
            title (str): Título do artigo
            source_name (str): Nome da fonte original
            
        Returns:
            str: Conteúdo HTML reescrito
        """
        try:
            # Extrai o texto do HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove elementos indesejados (anúncios, barras laterais, etc.)
            for elem in soup.select('aside, nav, footer, header, .ads, .advertisement, .sidebar, script, style, iframe'):
                elem.decompose()
            
            # Extrai o conteúdo principal
            main_content = soup.select_one('article, main, .content, .article-content, .post-content')
            if main_content:
                text_content = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback para o body se não encontrar o conteúdo principal
                text_content = soup.body.get_text(separator='\n', strip=True)
            
            # Limita o tamanho do texto para evitar custos excessivos
            text_content = text_content[:4000]
            
            # Cria o prompt para a API da OpenAI
            prompt = self._create_rewrite_prompt(text_content, title, source_name)
            
            logger.info(f"Enviando solicitação para reescrever artigo: '{title}'")
            
            # Faz a chamada para a API da OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em reescrever conteúdo de notícias em formato HTML, mantendo a essência da informação mas alterando a forma de apresentação."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extrai o conteúdo HTML reescrito
            rewritten_html = response.choices[0].message.content.strip()
            
            # Garante que o resultado é HTML válido
            if not rewritten_html.startswith('<'):
                # Se não começar com tag HTML, envolve em tags básicas
                rewritten_html = f"""<!DOCTYPE html>
                                            <html lang="pt-BR">
                                            <head>
                                                <meta charset="UTF-8">
                                                <meta name="description" content="{title}">
                                                <title>{title}</title>
                                            </head>
                                            <body>    
                                                    {rewritten_html}
                                            </body>
                                            </html>"""
            
            # Garante que o resultado está dentro de uma tag article
            if not rewritten_html.startswith('<article'):
                rewritten_html = f"<article>\n{rewritten_html}\n</article>"
            
            logger.info(f"Artigo reescrito com sucesso: '{title}'")
            return rewritten_html
            
        except Exception as e:
            logger.error(f"Erro ao reescrever artigo '{title}': {str(e)}")
            # Retorna um HTML básico em caso de erro
            return f"<article><h1>{title}</h1><p>Não foi possível reescrever este artigo.</p></article>"
    
    def _create_rewrite_prompt(self, text_content, title, source_name):
        """
        Cria o prompt para reescrita do artigo.
        
        Args:
            text_content (str): Conteúdo textual do artigo
            title (str): Título do artigo
            source_name (str): Nome da fonte original
            
        Returns:
            str: Prompt formatado
        """
        return f"""
Reescreva o seguinte conteúdo de notícia em formato HTML, mantendo as informações essenciais, 
mas alterando a estrutura textual e removendo qualquer menção específica à fonte original ({source_name}).
O principal objetivo é estruturar esse HTML para que o SEO do post alcance seu máximo potencial.

Título original: {title}

Conteúdo original:
{text_content}

Instruções específicas:
1. Mantenha a essência da notícia e os fatos principais
2. Altere a estrutura dos parágrafos e a forma de apresentação
3. Remova qualquer menção à fonte original, repórteres, ou elementos específicos do portal
4. Modifique ligeiramente o título, mantendo o tema principal
5. Use tags HTML apropriadas (h1, h2, p, etc.) para estruturar o conteúdo
6. A estrutura do título deve seguir exatamente este padrão:
   - Uma única tag <h2> para o subtítulo
   - Não repetir o título em nenhum outro lugar do conteúdo
7. No html evite inserir várias quebras de linha seguidas sem conteúdo.
8. Inclua pelo menos 3 parágrafos no corpo da notícia
9. Retorne APENAS o código HTML, sem explicações adicionais

O formato de saída deve ser HTML válido, começando com tags HTML apropriadas.
"""

def rewrite_article_content(html_content, title, source_name, api_key):
    """
    Função auxiliar para reescrever o conteúdo de um artigo.
    
    Args:
        html_content (str): Conteúdo HTML do artigo original
        title (str): Título do artigo
        source_name (str): Nome da fonte original
        api_key (str): Chave de API para a OpenAI
        
    Returns:
        str: Conteúdo HTML reescrito
    """
    client = OpenAIClient(api_key)
    return client.rewrite_article(html_content, title, source_name)

if __name__ == "__main__":
    # Teste da funcionalidade
    from config import OPENAI_API_KEY
    
    # Exemplo de HTML simples para teste
    test_html = """
    <article>
        <h1>Brasil vence Argentina em jogo decisivo</h1>
        <p>Em partida realizada ontem no Maracanã, a seleção brasileira venceu a Argentina por 2 a 1.</p>
        <p>Os gols foram marcados por Neymar e Vinicius Jr., enquanto Messi descontou para os argentinos.</p>
        <p>Com essa vitória, o Brasil se classifica para a próxima fase da competição.</p>
        <p>Reportagem de João Silva para o Jornal Esportivo.</p>
    </article>
    """
    
    rewritten = rewrite_article_content(
        test_html, 
        "Brasil vence Argentina em jogo decisivo", 
        "Jornal Esportivo",
        OPENAI_API_KEY
    )
    
    print("Conteúdo reescrito:")
    print(rewritten)
