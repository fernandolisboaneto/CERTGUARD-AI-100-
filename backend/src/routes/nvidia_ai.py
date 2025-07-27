"""
CertGuard AI - Rotas para API NVIDIA
Endpoints para integração com serviços de IA da NVIDIA
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import asyncio
import json
from datetime import datetime
import logging

from ..services.nvidia_ai import (
    nvidia_ai_service,
    analyze_document,
    generate_petition,
    analyze_jurisprudence,
    predict_case,
    analyze_contract
)
from ..services.blockchain_audit import record_audit

# Configuração de logging
logger = logging.getLogger(__name__)

# Blueprint para rotas da NVIDIA AI
nvidia_ai_bp = Blueprint('nvidia_ai', __name__, url_prefix='/api/nvidia-ai')

@nvidia_ai_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Verifica saúde da API NVIDIA"""
    try:
        # Executa health check assíncrono
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(nvidia_ai_service.health_check())
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@nvidia_ai_bp.route('/analyze-document', methods=['POST'])
@cross_origin()
def analyze_document_endpoint():
    """Analisa documento jurídico usando IA da NVIDIA"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        if not data or 'document_text' not in data:
            return jsonify({
                "status": "error",
                "message": "Campo 'document_text' é obrigatório"
            }), 400
        
        document_text = data['document_text']
        document_type = data.get('document_type', 'generic')
        user_id = data.get('user_id', 'anonymous')
        
        # Validação de tamanho
        if len(document_text) > 50000:
            return jsonify({
                "status": "error",
                "message": "Documento muito grande. Máximo 50.000 caracteres."
            }), 400
        
        # Executa análise assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            analyze_document(document_text, document_type)
        )
        loop.close()
        
        # Registra auditoria
        if result.get("success"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                record_audit(
                    user_id=user_id,
                    action="document_analysis",
                    resource_type="document",
                    resource_id=f"doc_{datetime.now().timestamp()}",
                    details={
                        "document_type": document_type,
                        "document_length": len(document_text),
                        "model_used": result.get("model_used"),
                        "confidence": result.get("confidence")
                    }
                )
            )
            loop.close()
        
        return jsonify({
            "status": "success" if result.get("success") else "error",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200 if result.get("success") else 500
        
    except Exception as e:
        logger.error(f"Erro na análise de documento: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@nvidia_ai_bp.route('/generate-petition', methods=['POST'])
@cross_origin()
def generate_petition_endpoint():
    """Gera petição jurídica usando IA da NVIDIA"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        if not data or 'case_details' not in data:
            return jsonify({
                "status": "error",
                "message": "Campo 'case_details' é obrigatório"
            }), 400
        
        case_details = data['case_details']
        user_id = data.get('user_id', 'anonymous')
        
        # Validação de campos obrigatórios
        required_fields = ['type', 'plaintiff', 'defendant', 'facts']
        for field in required_fields:
            if field not in case_details:
                return jsonify({
                    "status": "error",
                    "message": f"Campo '{field}' é obrigatório em case_details"
                }), 400
        
        # Executa geração assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            generate_petition(case_details)
        )
        loop.close()
        
        # Registra auditoria
        if result.get("success"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                record_audit(
                    user_id=user_id,
                    action="petition_generation",
                    resource_type="petition",
                    resource_id=f"petition_{datetime.now().timestamp()}",
                    details={
                        "case_type": case_details.get("type"),
                        "plaintiff": case_details.get("plaintiff"),
                        "defendant": case_details.get("defendant"),
                        "model_used": result.get("model_used"),
                        "confidence": result.get("confidence")
                    }
                )
            )
            loop.close()
        
        return jsonify({
            "status": "success" if result.get("success") else "error",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200 if result.get("success") else 500
        
    except Exception as e:
        logger.error(f"Erro na geração de petição: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@nvidia_ai_bp.route('/analyze-jurisprudence', methods=['POST'])
@cross_origin()
def analyze_jurisprudence_endpoint():
    """Analisa jurisprudência usando IA da NVIDIA"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        if not data or 'query' not in data:
            return jsonify({
                "status": "error",
                "message": "Campo 'query' é obrigatório"
            }), 400
        
        query = data['query']
        court = data.get('court', 'all')
        user_id = data.get('user_id', 'anonymous')
        
        # Validação de tamanho
        if len(query) > 1000:
            return jsonify({
                "status": "error",
                "message": "Consulta muito longa. Máximo 1.000 caracteres."
            }), 400
        
        # Executa análise assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            analyze_jurisprudence(query, court)
        )
        loop.close()
        
        # Registra auditoria
        if result.get("success"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                record_audit(
                    user_id=user_id,
                    action="jurisprudence_analysis",
                    resource_type="jurisprudence",
                    resource_id=f"juris_{datetime.now().timestamp()}",
                    details={
                        "query": query,
                        "court": court,
                        "model_used": result.get("model_used"),
                        "confidence": result.get("confidence")
                    }
                )
            )
            loop.close()
        
        return jsonify({
            "status": "success" if result.get("success") else "error",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200 if result.get("success") else 500
        
    except Exception as e:
        logger.error(f"Erro na análise jurisprudencial: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@nvidia_ai_bp.route('/predict-case', methods=['POST'])
@cross_origin()
def predict_case_endpoint():
    """Prediz resultado de caso usando IA da NVIDIA"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        if not data or 'case_data' not in data:
            return jsonify({
                "status": "error",
                "message": "Campo 'case_data' é obrigatório"
            }), 400
        
        case_data = data['case_data']
        user_id = data.get('user_id', 'anonymous')
        
        # Executa predição assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            predict_case(case_data)
        )
        loop.close()
        
        # Registra auditoria
        if result.get("success"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                record_audit(
                    user_id=user_id,
                    action="case_prediction",
                    resource_type="prediction",
                    resource_id=f"pred_{datetime.now().timestamp()}",
                    details={
                        "case_type": case_data.get("type"),
                        "model_used": result.get("model_used"),
                        "confidence": result.get("confidence")
                    }
                )
            )
            loop.close()
        
        return jsonify({
            "status": "success" if result.get("success") else "error",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200 if result.get("success") else 500
        
    except Exception as e:
        logger.error(f"Erro na predição de caso: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@nvidia_ai_bp.route('/analyze-contract', methods=['POST'])
@cross_origin()
def analyze_contract_endpoint():
    """Analisa contrato usando IA da NVIDIA"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        if not data or 'contract_text' not in data:
            return jsonify({
                "status": "error",
                "message": "Campo 'contract_text' é obrigatório"
            }), 400
        
        contract_text = data['contract_text']
        user_id = data.get('user_id', 'anonymous')
        
        # Validação de tamanho
        if len(contract_text) > 100000:
            return jsonify({
                "status": "error",
                "message": "Contrato muito grande. Máximo 100.000 caracteres."
            }), 400
        
        # Executa análise assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            analyze_contract(contract_text)
        )
        loop.close()
        
        # Registra auditoria
        if result.get("success"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                record_audit(
                    user_id=user_id,
                    action="contract_analysis",
                    resource_type="contract",
                    resource_id=f"contract_{datetime.now().timestamp()}",
                    details={
                        "contract_length": len(contract_text),
                        "model_used": result.get("model_used"),
                        "confidence": result.get("confidence")
                    }
                )
            )
            loop.close()
        
        return jsonify({
            "status": "success" if result.get("success") else "error",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200 if result.get("success") else 500
        
    except Exception as e:
        logger.error(f"Erro na análise contratual: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@nvidia_ai_bp.route('/switch-model', methods=['POST'])
@cross_origin()
def switch_model_endpoint():
    """Alterna entre modelos de IA da NVIDIA"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        if not data or 'config_number' not in data:
            return jsonify({
                "status": "error",
                "message": "Campo 'config_number' é obrigatório (1 ou 2)"
            }), 400
        
        config_number = data['config_number']
        user_id = data.get('user_id', 'anonymous')
        
        if config_number not in [1, 2]:
            return jsonify({
                "status": "error",
                "message": "config_number deve ser 1 ou 2"
            }), 400
        
        # Executa troca assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            nvidia_ai_service.switch_api_config(config_number)
        )
        loop.close()
        
        # Registra auditoria
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            record_audit(
                user_id=user_id,
                action="model_switch",
                resource_type="ai_model",
                resource_id=f"config_{config_number}",
                details={
                    "new_config": config_number,
                    "new_model": nvidia_ai_service.active_config["model"]
                }
            )
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "config_number": config_number,
                "active_model": nvidia_ai_service.active_config["model"],
                "message": f"Modelo alterado para configuração {config_number}"
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na troca de modelo: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@nvidia_ai_bp.route('/usage-stats', methods=['GET'])
@cross_origin()
def usage_stats_endpoint():
    """Retorna estatísticas de uso da API NVIDIA"""
    try:
        stats = nvidia_ai_service.get_usage_statistics()
        
        return jsonify({
            "status": "success",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@nvidia_ai_bp.route('/clear-cache', methods=['POST'])
@cross_origin()
def clear_cache_endpoint():
    """Limpa cache de respostas da API NVIDIA"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        
        nvidia_ai_service.clear_cache()
        
        # Registra auditoria
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            record_audit(
                user_id=user_id,
                action="cache_clear",
                resource_type="ai_cache",
                resource_id="nvidia_cache",
                details={"action": "cache_cleared"}
            )
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": {"message": "Cache limpo com sucesso"},
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@nvidia_ai_bp.route('/batch-analyze', methods=['POST'])
@cross_origin()
def batch_analyze_endpoint():
    """Analisa múltiplos documentos em lote"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        if not data or 'documents' not in data:
            return jsonify({
                "status": "error",
                "message": "Campo 'documents' é obrigatório"
            }), 400
        
        documents = data['documents']
        user_id = data.get('user_id', 'anonymous')
        
        if not isinstance(documents, list) or len(documents) == 0:
            return jsonify({
                "status": "error",
                "message": "Campo 'documents' deve ser uma lista não vazia"
            }), 400
        
        if len(documents) > 10:
            return jsonify({
                "status": "error",
                "message": "Máximo 10 documentos por lote"
            }), 400
        
        # Processa documentos em lote
        results = []
        
        for i, doc in enumerate(documents):
            if 'text' not in doc:
                results.append({
                    "index": i,
                    "success": False,
                    "error": "Campo 'text' obrigatório"
                })
                continue
            
            try:
                # Executa análise assíncrona
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    analyze_document(doc['text'], doc.get('type', 'generic'))
                )
                loop.close()
                
                results.append({
                    "index": i,
                    "success": result.get("success", False),
                    "data": result
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        # Registra auditoria do lote
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            record_audit(
                user_id=user_id,
                action="batch_analysis",
                resource_type="document_batch",
                resource_id=f"batch_{datetime.now().timestamp()}",
                details={
                    "total_documents": len(documents),
                    "successful_analyses": sum(1 for r in results if r["success"]),
                    "failed_analyses": sum(1 for r in results if not r["success"])
                }
            )
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "results": results,
                "summary": {
                    "total": len(documents),
                    "successful": sum(1 for r in results if r["success"]),
                    "failed": sum(1 for r in results if not r["success"])
                }
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na análise em lote: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Registra blueprint
def register_nvidia_ai_routes(app):
    """Registra rotas da NVIDIA AI na aplicação Flask"""
    app.register_blueprint(nvidia_ai_bp)

