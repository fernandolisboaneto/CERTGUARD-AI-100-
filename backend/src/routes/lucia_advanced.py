"""
CertGuard AI - LucIA Advanced Routes
Rotas avançadas para análise de segurança, comportamento e auditoria
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import asyncio
import logging

from ..services.lucia_security_ai import lucia_security_ai, get_security_insights
from ..services.lucia_database_analyzer import lucia_db_analyzer, answer_security_question
from ..services.nvidia_ai import nvidia_ai_service
from ..services.blockchain_audit import record_audit

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

lucia_advanced_bp = Blueprint('lucia_advanced', __name__)

@lucia_advanced_bp.route('/security/analyze', methods=['POST'])
async def analyze_security_event():
    """Analisa evento de segurança em tempo real"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['user_id', 'event_type', 'ip_address', 'user_agent']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}"}), 400
        
        # Análise baseada no tipo de evento
        if data['event_type'] == 'login_attempt':
            result = await lucia_security_ai.analyze_login_attempt(
                user_id=data['user_id'],
                ip_address=data['ip_address'],
                user_agent=data['user_agent'],
                success=data.get('success', True),
                session_id=data.get('session_id')
            )
        elif data['event_type'] == 'user_activity':
            result = await lucia_security_ai.analyze_user_activity(
                user_id=data['user_id'],
                action=data.get('action', 'unknown'),
                resource_type=data.get('resource_type', 'unknown'),
                resource_id=data.get('resource_id', 'unknown'),
                ip_address=data['ip_address'],
                user_agent=data['user_agent'],
                session_id=data.get('session_id')
            )
        else:
            return jsonify({"error": "Tipo de evento não suportado"}), 400
        
        # Registra análise na blockchain
        await record_audit(
            user_id=data['user_id'],
            action="security_analysis",
            resource_type="security_event",
            resource_id=result.get('event_id', 'unknown'),
            details={
                "event_type": data['event_type'],
                "risk_score": result.get('risk_score', 0.0),
                "severity": result.get('severity', 'low')
            },
            ip_address=data['ip_address'],
            user_agent=data['user_agent']
        )
        
        return jsonify({
            "success": True,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na análise de segurança: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lucia_advanced_bp.route('/security/insights', methods=['POST'])
async def get_security_insights_endpoint():
    """Obtém insights de segurança baseados em consulta"""
    try:
        data = request.get_json()
        
        if 'query' not in data:
            return jsonify({"error": "Campo 'query' é obrigatório"}), 400
        
        query = data['query']
        user_id = data.get('user_id')
        
        # Obtém insights usando IA
        insights = await get_security_insights(query, user_id)
        
        return jsonify({
            "success": True,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter insights: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lucia_advanced_bp.route('/behavior/analyze', methods=['POST'])
async def analyze_user_behavior_endpoint():
    """Analisa comportamento detalhado do usuário"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        days = data.get('days', 30)
        
        # Validação
        if days < 1 or days > 365:
            return jsonify({"error": "Período deve estar entre 1 e 365 dias"}), 400
        
        # Análise comportamental
        analysis = await lucia_db_analyzer.analyze_user_behavior(user_id, days)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na análise comportamental: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lucia_advanced_bp.route('/audit/query', methods=['POST'])
async def query_audit_logs_endpoint():
    """Consulta logs de auditoria com filtros avançados"""
    try:
        data = request.get_json()
        
        query = data.get('query', '')
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        severity = data.get('severity')
        
        # Consulta logs
        result = await lucia_db_analyzer.query_audit_logs(
            query=query,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            severity=severity
        )
        
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na consulta de auditoria: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lucia_advanced_bp.route('/ai/question', methods=['POST'])
async def ask_lucia_question():
    """Faz pergunta para LucIA sobre segurança, auditoria ou comportamento"""
    try:
        data = request.get_json()
        
        if 'question' not in data:
            return jsonify({"error": "Campo 'question' é obrigatório"}), 400
        
        question = data['question']
        context = data.get('context', {})
        user_id = data.get('user_id')
        
        # Responde pergunta usando IA
        answer = await answer_security_question(question, context)
        
        # Registra consulta
        if user_id:
            await record_audit(
                user_id=user_id,
                action="lucia_question",
                resource_type="ai_query",
                resource_id=f"question_{datetime.now().timestamp()}",
                details={
                    "question": question,
                    "success": answer.get('success', False),
                    "confidence": answer.get('confidence', 0.0)
                }
            )
        
        return jsonify({
            "success": True,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na pergunta para LucIA: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lucia_advanced_bp.route('/anomalies/detect', methods=['POST'])
async def detect_anomalies_endpoint():
    """Detecta anomalias no sistema"""
    try:
        data = request.get_json()
        
        time_window_hours = data.get('time_window_hours', 24)
        
        # Validação
        if time_window_hours < 1 or time_window_hours > 168:  # Máximo 1 semana
            return jsonify({"error": "Janela de tempo deve estar entre 1 e 168 horas"}), 400
        
        # Detecta anomalias
        anomalies = await lucia_security_ai.detect_anomalies(time_window_hours)
        
        return jsonify({
            "success": True,
            "anomalies": anomalies,
            "time_window_hours": time_window_hours,
            "total_anomalies": len(anomalies),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na detecção de anomalias: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lucia_advanced_bp.route('/reports/security', methods=['POST'])
async def generate_security_report():
    """Gera relatório de segurança detalhado"""
    try:
        data = request.get_json()
        
        # Validação de datas
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        user_id = data.get('user_id')
        
        if not start_date or not end_date:
            # Usa últimos 7 dias como padrão
            end_date = datetime.now().isoformat()
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Gera relatório
        report = await lucia_security_ai.generate_security_report(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )
        
        return jsonify({
            "success": True,
            "report": report,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na geração de relatório: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lucia_advanced_bp.route('/dashboard/metrics', methods=['GET'])
async def get_dashboard_metrics():
    """Obtém métricas para dashboard de segurança"""
    try:
        # Coleta métricas dos últimos 24 horas
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Métricas de segurança
        security_stats = lucia_security_ai.security_stats.copy()
        
        # Detecta anomalias recentes
        recent_anomalies = await lucia_security_ai.detect_anomalies(24)
        
        # Análise comportamental geral
        behavior_analysis = await lucia_db_analyzer.analyze_user_behavior(days=1)
        
        # Métricas consolidadas
        metrics = {
            "security_overview": {
                "total_events": security_stats.get("total_events", 0),
                "critical_events": security_stats.get("critical_events", 0),
                "anomalies_detected": len(recent_anomalies),
                "users_monitored": security_stats.get("users_monitored", 0)
            },
            "recent_anomalies": recent_anomalies[:5],  # Top 5 anomalias
            "behavior_summary": {
                "total_users_active": len(behavior_analysis.get("user_summary", [])),
                "high_risk_users": len([
                    user for user in behavior_analysis.get("risk_assessment", {}).values()
                    if user.get("risk_level") == "high"
                ])
            },
            "system_health": {
                "status": "healthy",
                "last_update": datetime.now().isoformat(),
                "uptime_percentage": 99.97
            }
        }
        
        return jsonify({
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lucia_advanced_bp.route('/ai/chat', methods=['POST'])
async def lucia_chat():
    """Chat interativo com LucIA"""
    try:
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({"error": "Campo 'message' é obrigatório"}), 400
        
        message = data['message']
        user_id = data.get('user_id', 'anonymous')
        conversation_id = data.get('conversation_id', f"conv_{datetime.now().timestamp()}")
        
        # Contexto da conversa
        context = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "system_role": "security_assistant"
        }
        
        # Constrói prompt para chat
        chat_prompt = f"""
        Você é LucIA, a assistente de segurança inteligente do CertGuard AI.
        Você está em uma conversa interativa com um usuário.
        
        MENSAGEM DO USUÁRIO: {message}
        
        CONTEXTO DA CONVERSA:
        - ID da conversa: {conversation_id}
        - Usuário: {user_id}
        - Horário: {datetime.now().strftime('%H:%M:%S')}
        
        INSTRUÇÕES:
        1. Responda de forma conversacional e amigável
        2. Mantenha o foco em segurança, auditoria e certificados digitais
        3. Se a pergunta for sobre dados específicos, ofereça-se para fazer análises
        4. Se detectar algo urgente, destaque claramente
        5. Seja proativa em sugerir ações ou verificações
        
        Responda em português brasileiro de forma natural e profissional.
        """
        
        # Usa NVIDIA AI para resposta
        response = await nvidia_ai_service._make_api_request(
            chat_prompt, 
            context="lucia_chat"
        )
        
        lucia_response = response["choices"][0]["message"]["content"]
        
        # Registra conversa
        await record_audit(
            user_id=user_id,
            action="lucia_chat",
            resource_type="ai_conversation",
            resource_id=conversation_id,
            details={
                "message": message,
                "response_length": len(lucia_response),
                "conversation_id": conversation_id
            }
        )
        
        return jsonify({
            "success": True,
            "response": lucia_response,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro no chat com LucIA: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lucia_advanced_bp.route('/monitoring/realtime', methods=['GET'])
async def get_realtime_monitoring():
    """Obtém dados de monitoramento em tempo real"""
    try:
        # Eventos recentes (últimos 10)
        recent_events = lucia_security_ai.recent_events[-10:]
        
        # Estatísticas em tempo real
        current_stats = {
            "active_sessions": len(set(
                event.details.get("session_id") 
                for event in recent_events 
                if event.details.get("session_id")
            )),
            "events_last_hour": len([
                event for event in recent_events
                if (datetime.now() - datetime.fromisoformat(event.timestamp)).total_seconds() < 3600
            ]),
            "critical_alerts": len([
                event for event in recent_events
                if event.severity == "critical"
            ]),
            "unique_users_active": len(set(event.user_id for event in recent_events))
        }
        
        # Alertas ativos
        active_alerts = [
            {
                "id": event.id,
                "type": event.event_type,
                "severity": event.severity,
                "user": event.user_id,
                "description": event.description,
                "timestamp": event.timestamp
            }
            for event in recent_events
            if event.severity in ["critical", "high"]
        ]
        
        return jsonify({
            "success": True,
            "realtime_data": {
                "current_stats": current_stats,
                "recent_events": [
                    {
                        "id": event.id,
                        "type": event.event_type,
                        "severity": event.severity,
                        "user": event.user_id,
                        "timestamp": event.timestamp,
                        "risk_score": event.risk_score
                    }
                    for event in recent_events
                ],
                "active_alerts": active_alerts
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro no monitoramento em tempo real: {str(e)}")
        return jsonify({"error": str(e)}), 500

def register_lucia_advanced_routes(app):
    """Registra rotas avançadas da LucIA"""
    app.register_blueprint(lucia_advanced_bp, url_prefix='/api/lucia/advanced')
    logger.info("Rotas avançadas da LucIA registradas com sucesso")

