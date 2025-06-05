"""
Módulo estendido para interação com o WordPress via XML-RPC, incluindo suporte para imagens.
"""

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPosts
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.compat import xmlrpc_client
import logging
from datetime import datetime
import os
import mimetypes

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WordPressClient:
    """Cliente para interagir com o WordPress via XML-RPC."""
    
    def __init__(self, url, username, password):
        """
        Inicializa o cliente do WordPress.
        
        Args:
            url (str): URL do endpoint XML-RPC do WordPress
            username (str): Nome de usuário do WordPress
            password (str): Senha do WordPress
        """
        self.client = Client(url, username, password)
        logger.info("Cliente do WordPress inicializado")
        
        # Verifica a conexão
        try:
            user_info = self.client.call(GetUserInfo())
            logger.info(f"Conectado ao WordPress como: {user_info.display_name}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao WordPress: {str(e)}")
            raise
    
    def upload_image(self, image_path):
        """
        Faz upload de uma imagem para a biblioteca de mídia do WordPress.
        
        Args:
            image_path (str): Caminho para o arquivo de imagem
            
        Returns:
            dict: Dados da imagem enviada, incluindo URL
        """
        try:
            # Determina o tipo MIME da imagem
            filename = os.path.basename(image_path)
            mimetype = mimetypes.guess_type(filename)[0]
            if not mimetype:
                mimetype = 'image/jpeg'  # Fallback para JPEG
            
            # Prepara os dados para upload
            with open(image_path, 'rb') as img:
                data = {
                    'name': filename,
                    'type': mimetype,
                    'bits': xmlrpc_client.Binary(img.read()),
                    'overwrite': True
                }
            
            logger.info(f"Enviando imagem para o WordPress: {filename}")
            response = self.client.call(UploadFile(data))
            
            logger.info(f"Imagem enviada com sucesso. URL: {response['url']}")
            return response
        except Exception as e:
            logger.error(f"Erro ao enviar imagem para o WordPress: {str(e)}")
            return None
    
    def publish_post(self, title, content, featured_image=None, categories=None, tags=None, status='publish'):
        """
        Publica um novo post no WordPress.
        
        Args:
            title (str): Título do post
            content (str): Conteúdo HTML do post
            featured_image (str, optional): Caminho para a imagem destacada
            categories (list): Lista de categorias (opcional)
            tags (list): Lista de tags (opcional)
            status (str): Status do post (draft, publish, private, etc.)
            
        Returns:
            str: ID do post publicado
        """
        try:
            post = WordPressPost()
            post.title = title
            content = content.replace('\r\n', '\n').replace('\r', '\n').replace('\n','')
            post.content = content.replace('```html','').replace('```','')
            post.post_status = status
            
            if categories:
                post.terms_names = {'category': categories}
            
            if tags:
                if not post.terms_names:
                    post.terms_names = {}
                post.terms_names['post_tag'] = tags
            
            # Adiciona data e hora atual
            post.date = datetime.now()
            
            # Publica o post
            logger.info(f"Publicando post: '{title}'")
            post_id = self.client.call(NewPost(post))
            
            # Se houver imagem destacada, faz o upload e a associa ao post
            if featured_image and os.path.exists(featured_image):
                try:
                    # Faz upload da imagem
                    attachment = self.upload_image(featured_image)
                    if attachment:
                        # Adiciona a imagem como imagem destacada do post
                        from wordpress_xmlrpc.methods import posts
                        self.client.call(posts.EditPost(post_id, {
                            'post_thumbnail': attachment['id']
                        }))
                        logger.info(f"Imagem destacada adicionada ao post ID: {post_id}")
                except Exception as e:
                    logger.error(f"Erro ao adicionar imagem destacada: {str(e)}")
            
            logger.info(f"Post publicado com sucesso. ID: {post_id}")
            return post_id
        except Exception as e:
            logger.error(f"Erro ao publicar post '{title}': {str(e)}")
            raise
    
    def get_recent_posts(self, num_posts=5):
        """
        Obtém os posts mais recentes do WordPress.
        
        Args:
            num_posts (int): Número de posts a retornar
            
        Returns:
            list: Lista de posts recentes
        """
        try:
            logger.info(f"Obtendo {num_posts} posts recentes")
            posts = self.client.call(GetPosts({'number': num_posts}))
            
            logger.info(f"Obtidos {len(posts)} posts recentes")
            return posts
        except Exception as e:
            logger.error(f"Erro ao obter posts recentes: {str(e)}")
            return []

def publish_article_to_wordpress(title, content, url, username, password, featured_image=None, categories=None, tags=None):
    """
    Função auxiliar para publicar um artigo no WordPress.
    
    Args:
        title (str): Título do artigo
        content (str): Conteúdo HTML do artigo
        url (str): URL do endpoint XML-RPC do WordPress
        username (str): Nome de usuário do WordPress
        password (str): Senha do WordPress
        featured_image (str, optional): Caminho para a imagem destacada
        categories (list): Lista de categorias (opcional)
        tags (list): Lista de tags (opcional)
        
    Returns:
        str: ID do post publicado ou None em caso de erro
    """
    try:
        client = WordPressClient(url, username, password)
        post_id = client.publish_post(title, content, featured_image, categories, tags)
        return post_id
    except Exception as e:
        logger.error(f"Erro ao publicar artigo no WordPress: {str(e)}")
        return None

if __name__ == "__main__":
    # Teste da funcionalidade
    from config import WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD
    
    # Exemplo de conteúdo para teste
    test_title = "Artigo de Teste via API com Imagem"
    test_content = """
    <h1>Este é um artigo de teste</h1>
    <p>Este artigo foi publicado automaticamente via API XML-RPC do WordPress.</p>
    <p>Ele serve como um teste para verificar a funcionalidade de publicação com imagem destacada.</p>
    """
    
    # Caminho para uma imagem de teste (substitua pelo caminho real)
    test_image = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "test_image.jpg")
    
    try:
        post_id = publish_article_to_wordpress(
            test_title,
            test_content,
            WORDPRESS_URL,
            WORDPRESS_USERNAME,
            WORDPRESS_PASSWORD,
            featured_image=test_image,
            categories=["Teste", "API"],
            tags=["teste", "automatizado", "python", "imagem"]
        )
        
        if post_id:
            print(f"Artigo publicado com sucesso! ID: {post_id}")
        else:
            print("Falha ao publicar o artigo.")
    except Exception as e:
        print(f"Erro durante o teste: {str(e)}")