"""
Script para testar o funcionamento do pipeline com valores simulados.
"""

import os
import logging
import json
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_pipeline():
    """Executa um teste do pipeline com valores simulados."""
    logger.info("Iniciando teste do pipeline com valores simulados...")
    
    # Cria diretório de saída para os testes
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Simula tendências do Google Trends
    mock_trends = [
        "Copa do Brasil",
        "Eleições 2024",
        "Inteligência Artificial",
        "Olimpíadas",
        "Pandemia"
    ]
    
    # Salva as tendências simuladas
    with open(os.path.join(output_dir, "mock_trends.json"), "w", encoding="utf-8") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "trends": mock_trends}, f, ensure_ascii=False, indent=2)
    
    # Simula artigos de notícias
    mock_articles = [
        {
            "trend": "Copa do Brasil",
            "title": "Flamengo vence e avança para as quartas de final da Copa do Brasil",
            "content": "<article><h1>Flamengo vence e avança para as quartas de final da Copa do Brasil</h1><p>Em jogo emocionante, o Flamengo venceu o Athletico-PR por 2 a 1 e garantiu vaga nas quartas de final da Copa do Brasil.</p><p>Os gols foram marcados por Pedro e Arrascaeta, enquanto Pablo descontou para o Athletico.</p><p>Com o resultado, o Flamengo aguarda o sorteio para conhecer seu próximo adversário na competição.</p></article>",
            "status": "published",
            "wordpress_id": "12345"
        },
        {
            "trend": "Inteligência Artificial",
            "title": "Nova ferramenta de IA promete revolucionar diagnósticos médicos",
            "content": "<article><h1>Nova ferramenta de IA promete revolucionar diagnósticos médicos</h1><p>Pesquisadores brasileiros desenvolveram uma nova ferramenta de inteligência artificial capaz de identificar doenças raras com precisão superior a 95%.</p><p>O sistema utiliza aprendizado profundo para analisar exames de imagem e identificar padrões imperceptíveis ao olho humano.</p><p>Especialistas acreditam que a tecnologia pode reduzir significativamente o tempo de diagnóstico e melhorar o tratamento de pacientes.</p></article>",
            "status": "published",
            "wordpress_id": "12346"
        }
    ]
    
    # Salva os artigos simulados
    for i, article in enumerate(mock_articles):
        filename = f"mock_article_{i+1}.html"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(article["content"])
        
        article["file_path"] = filepath
    
    # Salva os resultados simulados
    results_file = os.path.join(output_dir, "mock_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_processed": len(mock_articles),
            "results": mock_articles
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Teste concluído. Resultados salvos em: {results_file}")
    return output_dir, results_file

if __name__ == "__main__":
    output_dir, results_file = test_pipeline()
    print(f"Teste concluído com sucesso!")
    print(f"Diretório de saída: {output_dir}")
    print(f"Arquivo de resultados: {results_file}")
