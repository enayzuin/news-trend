# Automação de Conteúdo com Google Trends e OpenAI

Este projeto implementa um pipeline automatizado que:

1. Consulta as tendências atuais do Google Trends
2. Busca notícias relacionadas a essas tendências
3. Reescreve o conteúdo das notícias usando a API da OpenAI
4. Publica os artigos reescritos no WordPress

## Requisitos

- Python 3.6+
- Chave de API da OpenAI
- Chave de API da NewsAPI (opcional, há fallback para scraping)
- Acesso a um site WordPress com XML-RPC habilitado

## Instalação

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/seu-usuario/projeto-trends.git
cd projeto-trends
pip install pytrends requests python-wordpress-xmlrpc openai beautifulsoup4
```

## Configuração

Edite o arquivo `config.py` e insira suas credenciais:

```python
# Configuração da API OpenAI
OPENAI_API_KEY = "sua_chave_api_openai"

# Configuração da NewsAPI
NEWSAPI_API_KEY = "sua_chave_api_newsapi"

# Configuração do WordPress
WORDPRESS_URL = "https://seu-site-wordpress.com/xmlrpc.php"
WORDPRESS_USERNAME = "seu_usuario"
WORDPRESS_PASSWORD = "sua_senha"

# Configurações gerais
MAX_TRENDS = 5  # Número máximo de tendências a serem processadas
MAX_NEWS_PER_TREND = 3  # Número máximo de notícias por tendência
```

## Estrutura do Projeto

- `config.py`: Configurações e chaves de API
- `trends_utils.py`: Módulo para obtenção de tendências do Google Trends
- `news_utils.py`: Módulo para busca de notícias relacionadas às tendências
- `openai_utils.py`: Módulo para reescrita de conteúdo usando a API da OpenAI
- `wordpress_utils.py`: Módulo para publicação de conteúdo no WordPress
- `main.py`: Script principal que executa o pipeline completo
- `test.py`: Script para testar o funcionamento com valores simulados

## Uso

### Executar o Pipeline Completo

```bash
python main.py
```

Este comando executará o pipeline completo:
1. Obterá as tendências atuais do Google Trends
2. Buscará notícias relacionadas a cada tendência
3. Reescreverá o conteúdo das notícias usando a API da OpenAI
4. Publicará os artigos reescritos no WordPress

### Testar com Valores Simulados

```bash
python test.py
```

Este comando executará um teste do pipeline com valores simulados, sem fazer chamadas reais às APIs.

## Personalização

### Modificar o Prompt de Reescrita

Para personalizar como a OpenAI reescreve o conteúdo, edite o método `_create_rewrite_prompt` no arquivo `openai_utils.py`.

### Alterar o Número de Tendências

Modifique as constantes `MAX_TRENDS` e `MAX_NEWS_PER_TREND` no arquivo `config.py` para controlar quantas tendências e notícias são processadas.

### Usar Outra API de Notícias

O sistema está configurado para usar a NewsAPI, mas inclui um fallback para scraping do Google News. Para usar outra API, modifique o arquivo `news_utils.py`.

## Logs e Resultados

- Os logs são salvos em `pipeline.log`
- Os artigos reescritos são salvos no diretório `output/`
- Um resumo dos resultados é salvo em `output/results.json`

## Limitações

- A API da OpenAI tem custos associados ao uso
- O scraping de notícias pode ser afetado por mudanças nos sites de origem
- A publicação no WordPress requer que o XML-RPC esteja habilitado no site

## Solução de Problemas

### Erro de Autenticação na OpenAI

Verifique se a chave de API da OpenAI está correta e tem saldo disponível.

### Erro de Conexão com o WordPress

Certifique-se de que:
- A URL do XML-RPC está correta (geralmente termina com `/xmlrpc.php`)
- O usuário tem permissões para publicar posts
- O XML-RPC está habilitado no WordPress

### Nenhuma Tendência Encontrada

Verifique sua conexão com a internet e tente novamente. O Google Trends pode ter limitações de taxa de requisição.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.
#   n e w s - t r e n d  
 