"""
API Flask para expor o pipeline de automação de conteúdo.

Este script cria um servidor Flask que expõe o pipeline de automação de conteúdo
através do endpoint /trend-news.
"""

import os
import sys
import json
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, request, Response

# Adiciona o diretório atual ao path para importar os módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa o pipeline principal
from main import run_pipeline

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cria a aplicação Flask
app = Flask(__name__)

# Variável global para armazenar o status da execução
pipeline_status = {
    "is_running": False,
    "last_run": None,
    "last_status": None,
    "results": None
}

def run_pipeline_async():
    """Executa o pipeline em uma thread separada."""
    global pipeline_status
    
    try:
        pipeline_status["is_running"] = True
        pipeline_status["last_run"] = datetime.now().isoformat()
        
        # Executa o pipeline
        success = run_pipeline()
        
        # Atualiza o status
        pipeline_status["is_running"] = False
        pipeline_status["last_status"] = "success" if success else "error"
        
        # Carrega os resultados do arquivo
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        results_file = os.path.join(output_dir, "results.json")
        
        if os.path.exists(results_file):
            with open(results_file, "r", encoding="utf-8") as f:
                pipeline_status["results"] = json.load(f)
        
        logger.info(f"Pipeline concluído com status: {pipeline_status['last_status']}")
        
    except Exception as e:
        pipeline_status["is_running"] = False
        pipeline_status["last_status"] = "error"
        logger.error(f"Erro durante a execução do pipeline: {str(e)}")

@app.route('/trend-news', methods=['POST'])
def trigger_pipeline():
    """Endpoint para acionar o pipeline de automação de conteúdo."""
    global pipeline_status
    
    # Verifica se o pipeline já está em execução
    if pipeline_status["is_running"]:
        return jsonify({
            "status": "error",
            "message": "Pipeline já está em execução",
            "started_at": pipeline_status["last_run"]
        }), 409
    
    # Inicia o pipeline em uma thread separada
    thread = threading.Thread(target=run_pipeline_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "status": "started",
        "message": "Pipeline iniciado com sucesso",
        "started_at": pipeline_status["last_run"]
    }), 202

@app.route('/trend-news/status', methods=['GET'])
def get_pipeline_status():
    """Endpoint para verificar o status do pipeline."""
    global pipeline_status
    
    return jsonify({
        "is_running": pipeline_status["is_running"],
        "last_run": pipeline_status["last_run"],
        "last_status": pipeline_status["last_status"]
    })

@app.route('/trend-news/results', methods=['GET'])
def get_pipeline_results():
    """Endpoint para obter os resultados do último pipeline executado."""
    global pipeline_status
    
    if not pipeline_status["results"]:
        return jsonify({
            "status": "error",
            "message": "Nenhum resultado disponível"
        }), 404
    
    return jsonify(pipeline_status["results"])

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar a saúde da API."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    # Define a porta (padrão: 8000)
    port = int(os.environ.get("PORT", 8000))
    
    # Inicia o servidor Flask
    logger.info(f"Iniciando servidor Flask na porta {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)