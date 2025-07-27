"""
CertGuard AI - Rotas para Blockchain de Auditoria
Endpoints para sistema de auditoria imutável
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import asyncio
import json
from datetime import datetime, timedelta
import logging

from ..services.blockchain_audit import (
    blockchain_audit_service,
    record_audit,
    get_audit_trail,
    verify_integrity,
    generate_report
)

# Configuração de logging
logger = logging.getLogger(__name__)

# Blueprint para rotas de blockchain
blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/api/blockchain')

@blockchain_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Verifica saúde do sistema blockchain"""
    try:
        stats = blockchain_audit_service.get_blockchain_statistics()
        
        # Verifica integridade
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        integrity = loop.run_until_complete(verify_integrity())
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "blockchain_status": "healthy" if integrity["valid"] else "corrupted",
                "statistics": stats,
                "integrity_check": integrity
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no health check blockchain: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/record', methods=['POST'])
@cross_origin()
def record_audit_event():
    """Registra evento de auditoria na blockchain"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        required_fields = ['user_id', 'action', 'resource_type', 'resource_id', 'details']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Campo '{field}' é obrigatório"
                }), 400
        
        # Extrai dados
        user_id = data['user_id']
        action = data['action']
        resource_type = data['resource_type']
        resource_id = data['resource_id']
        details = data['details']
        
        # Dados opcionais
        certificate_used = data.get('certificate_used')
        ip_address = data.get('ip_address', request.remote_addr)
        user_agent = data.get('user_agent', request.headers.get('User-Agent'))
        session_id = data.get('session_id')
        
        # Registra evento assíncrono
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        record_id = loop.run_until_complete(
            record_audit(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                certificate_used=certificate_used,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id
            )
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "record_id": record_id,
                "message": "Evento registrado na blockchain",
                "blockchain_stats": blockchain_audit_service.get_blockchain_statistics()
            },
            "timestamp": datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Erro ao registrar evento: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/audit-trail', methods=['GET'])
@cross_origin()
def get_audit_trail_endpoint():
    """Recupera trilha de auditoria com filtros"""
    try:
        # Parâmetros de consulta
        user_id = request.args.get('user_id')
        resource_type = request.args.get('resource_type')
        resource_id = request.args.get('resource_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        # Validação de limite
        if limit > 1000:
            return jsonify({
                "status": "error",
                "message": "Limite máximo é 1000 registros"
            }), 400
        
        # Monta filtros
        filters = {}
        if user_id:
            filters['user_id'] = user_id
        if resource_type:
            filters['resource_type'] = resource_type
        if resource_id:
            filters['resource_id'] = resource_id
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        filters['limit'] = limit
        
        # Executa consulta assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        records = loop.run_until_complete(get_audit_trail(filters))
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "records": records,
                "total_returned": len(records),
                "filters_applied": filters
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao recuperar trilha: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/verify-integrity', methods=['GET'])
@cross_origin()
def verify_blockchain_integrity():
    """Verifica integridade da blockchain"""
    try:
        # Executa verificação assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(verify_integrity())
        loop.close()
        
        # Registra verificação de integridade
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            record_audit(
                user_id="system",
                action="integrity_verification",
                resource_type="blockchain",
                resource_id="main_chain",
                details={
                    "verification_result": result["valid"],
                    "total_blocks": blockchain_audit_service.stats["total_blocks"],
                    "verification_timestamp": datetime.now().isoformat()
                }
            )
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na verificação de integridade: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/statistics', methods=['GET'])
@cross_origin()
def get_blockchain_statistics():
    """Retorna estatísticas da blockchain"""
    try:
        stats = blockchain_audit_service.get_blockchain_statistics()
        
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

@blockchain_bp.route('/compliance-report', methods=['POST'])
@cross_origin()
def generate_compliance_report():
    """Gera relatório de conformidade"""
    try:
        data = request.get_json()
        
        # Validação de entrada
        if not data or 'start_date' not in data or 'end_date' not in data:
            return jsonify({
                "status": "error",
                "message": "Campos 'start_date' e 'end_date' são obrigatórios"
            }), 400
        
        start_date = data['start_date']
        end_date = data['end_date']
        user_id = data.get('user_id', 'anonymous')
        
        # Validação de datas
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            if start_dt >= end_dt:
                return jsonify({
                    "status": "error",
                    "message": "Data de início deve ser anterior à data de fim"
                }), 400
                
            # Limite de 1 ano
            if (end_dt - start_dt).days > 365:
                return jsonify({
                    "status": "error",
                    "message": "Período máximo é de 1 ano"
                }), 400
                
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Formato de data inválido. Use ISO 8601"
            }), 400
        
        # Gera relatório assíncrono
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(
            generate_report(start_date, end_date)
        )
        loop.close()
        
        # Registra geração de relatório
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            record_audit(
                user_id=user_id,
                action="compliance_report_generation",
                resource_type="report",
                resource_id=f"report_{datetime.now().timestamp()}",
                details={
                    "report_period": f"{start_date} to {end_date}",
                    "total_activities": report["summary"]["total_activities"],
                    "users_active": report["summary"]["users_active"]
                }
            )
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": report,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na geração de relatório: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/certificate-history/<certificate_id>', methods=['GET'])
@cross_origin()
def get_certificate_history(certificate_id):
    """Recupera histórico de uso de certificado"""
    try:
        # Executa consulta assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        history = loop.run_until_complete(
            blockchain_audit_service.get_certificate_usage_history(certificate_id)
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "certificate_id": certificate_id,
                "usage_history": history,
                "total_uses": len(history)
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico de certificado: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/user-activity/<user_id>', methods=['GET'])
@cross_origin()
def get_user_activity_summary(user_id):
    """Gera resumo de atividade do usuário"""
    try:
        # Parâmetros opcionais
        days = int(request.args.get('days', 30))
        
        if days > 365:
            return jsonify({
                "status": "error",
                "message": "Período máximo é de 365 dias"
            }), 400
        
        # Executa consulta assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        summary = loop.run_until_complete(
            blockchain_audit_service.get_user_activity_summary(user_id, days)
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": summary,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter resumo de atividade: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/force-block-creation', methods=['POST'])
@cross_origin()
def force_block_creation():
    """Força criação de novo bloco com registros pendentes"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'system')
        
        # Verifica se há registros pendentes
        if not blockchain_audit_service.pending_records:
            return jsonify({
                "status": "error",
                "message": "Não há registros pendentes para criar bloco"
            }), 400
        
        pending_count = len(blockchain_audit_service.pending_records)
        
        # Força criação de bloco
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            blockchain_audit_service._create_new_block()
        )
        loop.close()
        
        # Registra criação forçada
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            record_audit(
                user_id=user_id,
                action="force_block_creation",
                resource_type="blockchain",
                resource_id="main_chain",
                details={
                    "records_in_block": pending_count,
                    "new_block_index": len(blockchain_audit_service.blockchain) - 1
                }
            )
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "message": "Bloco criado com sucesso",
                "records_processed": pending_count,
                "new_block_index": len(blockchain_audit_service.blockchain) - 1,
                "blockchain_stats": blockchain_audit_service.get_blockchain_statistics()
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na criação forçada de bloco: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/export-blockchain', methods=['GET'])
@cross_origin()
def export_blockchain():
    """Exporta blockchain completa"""
    try:
        # Parâmetros de exportação
        format_type = request.args.get('format', 'json')
        include_pending = request.args.get('include_pending', 'false').lower() == 'true'
        
        if format_type not in ['json', 'csv']:
            return jsonify({
                "status": "error",
                "message": "Formato deve ser 'json' ou 'csv'"
            }), 400
        
        # Coleta dados da blockchain
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_blocks": len(blockchain_audit_service.blockchain),
                "total_records": blockchain_audit_service.stats["total_records"],
                "include_pending": include_pending,
                "format": format_type
            },
            "blockchain": []
        }
        
        # Adiciona blocos
        for block in blockchain_audit_service.blockchain:
            block_data = {
                "index": block.index,
                "timestamp": block.timestamp,
                "hash": block.hash,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
                "records": [record.to_dict() for record in block.data]
            }
            export_data["blockchain"].append(block_data)
        
        # Adiciona registros pendentes se solicitado
        if include_pending and blockchain_audit_service.pending_records:
            export_data["pending_records"] = [
                record.to_dict() for record in blockchain_audit_service.pending_records
            ]
        
        # Registra exportação
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            record_audit(
                user_id="system",
                action="blockchain_export",
                resource_type="blockchain",
                resource_id="main_chain",
                details={
                    "export_format": format_type,
                    "include_pending": include_pending,
                    "total_blocks_exported": len(blockchain_audit_service.blockchain)
                }
            )
        )
        loop.close()
        
        return jsonify({
            "status": "success",
            "data": export_data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na exportação: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/search-records', methods=['POST'])
@cross_origin()
def search_records():
    """Busca registros por critérios avançados"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Corpo da requisição é obrigatório"
            }), 400
        
        # Critérios de busca
        search_criteria = {
            "user_id": data.get('user_id'),
            "action": data.get('action'),
            "resource_type": data.get('resource_type'),
            "resource_id": data.get('resource_id'),
            "start_date": data.get('start_date'),
            "end_date": data.get('end_date'),
            "limit": min(int(data.get('limit', 100)), 1000)
        }
        
        # Remove critérios vazios
        search_criteria = {k: v for k, v in search_criteria.items() if v is not None}
        
        # Executa busca
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(get_audit_trail(search_criteria))
        loop.close()
        
        # Busca adicional por texto nos detalhes (se especificado)
        search_text = data.get('search_text')
        if search_text:
            search_text_lower = search_text.lower()
            filtered_results = []
            
            for record in results:
                details_str = json.dumps(record.get('details', {})).lower()
                if search_text_lower in details_str:
                    filtered_results.append(record)
            
            results = filtered_results
        
        return jsonify({
            "status": "success",
            "data": {
                "records": results,
                "total_found": len(results),
                "search_criteria": search_criteria,
                "search_text": search_text
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na busca de registros: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Registra blueprint
def register_blockchain_routes(app):
    """Registra rotas de blockchain na aplicação Flask"""
    app.register_blueprint(blockchain_bp)

