# API para Sistema de Auditoria - CertGuard AI

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Any

from ..services.audit_analyzer import AuditAnalyzer, SecurityEvent
from ..services.nvidia_lucia_ai import LuciaAI

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')
logger = logging.getLogger(__name__)

# Inicializar analisador de auditoria
analyzer = AuditAnalyzer()
lucia_ai = LuciaAI()

@audit_bp.route('/events', methods=['POST'])
def log_security_event():
    """Registrar evento de segurança"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['user_id', 'event_type', 'ip_address']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Criar evento
        event = SecurityEvent(
            user_id=data['user_id'],
            event_type=data['event_type'],
            ip_address=data['ip_address'],
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            details=data.get('details', {}),
            risk_score=data.get('risk_score', 0.0),
            anomaly_detected=data.get('anomaly_detected', False)
        )
        
        # Registrar evento
        event_id = analyzer.log_security_event(event)
        
        # Atualizar perfil comportamental do usuário
        analyzer.update_user_behavior_profile(event.user_id)
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'message': 'Evento registrado com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao registrar evento: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/events', methods=['GET'])
def get_security_events():
    """Obter eventos de segurança"""
    try:
        # Parâmetros de filtro
        user_id = request.args.get('user_id')
        event_type = request.args.get('event_type')
        ip_address = request.args.get('ip_address')
        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 100))
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Construir query
        query = '''
            SELECT id, user_id, event_type, ip_address, timestamp, 
                   details, risk_score, anomaly_detected
            FROM security_events 
            WHERE timestamp > ?
        '''
        params = [start_date]
        
        if user_id:
            query += ' AND user_id = ?'
            params.append(user_id)
        
        if event_type:
            query += ' AND event_type = ?'
            params.append(event_type)
        
        if ip_address:
            query += ' AND ip_address = ?'
            params.append(ip_address)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        # Executar query
        import sqlite3
        conn = sqlite3.connect(analyzer.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        events = []
        for row in cursor.fetchall():
            events.append({
                'id': row[0],
                'user_id': row[1],
                'event_type': row[2],
                'ip_address': row[3],
                'timestamp': row[4],
                'details': json.loads(row[5]),
                'risk_score': row[6],
                'anomaly_detected': bool(row[7])
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'events': events,
            'total': len(events)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter eventos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/report', methods=['GET'])
def generate_security_report():
    """Gerar relatório de segurança"""
    try:
        days = int(request.args.get('days', 7))
        report = analyzer.generate_security_report(days)
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/user/<user_id>/timeline', methods=['GET'])
def get_user_timeline(user_id):
    """Obter timeline de atividades do usuário"""
    try:
        days = int(request.args.get('days', 30))
        timeline = analyzer.get_user_activity_timeline(user_id, days)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'timeline': timeline
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter timeline: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/user/<user_id>/profile', methods=['GET'])
def get_user_behavior_profile(user_id):
    """Obter perfil comportamental do usuário"""
    try:
        profile = analyzer.get_user_behavior_profile(user_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Perfil não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': {
                'user_id': profile.user_id,
                'typical_login_times': profile.typical_login_times,
                'typical_locations': profile.typical_locations,
                'typical_actions': profile.typical_actions,
                'last_updated': profile.last_updated.isoformat(),
                'risk_level': profile.risk_level
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter perfil: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/ip/<ip_address>/analysis', methods=['GET'])
def analyze_ip_behavior(ip_address):
    """Analisar comportamento de um IP"""
    try:
        days = int(request.args.get('days', 7))
        analysis = analyzer.analyze_ip_behavior(ip_address, days)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Erro ao analisar IP: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/alerts', methods=['GET'])
def get_security_alerts():
    """Obter alertas de segurança"""
    try:
        severity = request.args.get('severity')
        alerts = analyzer.get_active_alerts(severity)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total': len(alerts)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_security_alert(alert_id):
    """Resolver alerta de segurança"""
    try:
        data = request.get_json()
        resolved_by = data.get('resolved_by', 'system')
        notes = data.get('notes', '')
        
        analyzer.resolve_alert(alert_id, resolved_by, notes)
        
        return jsonify({
            'success': True,
            'message': 'Alerta resolvido com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao resolver alerta: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/lucia/query', methods=['POST'])
def lucia_security_query():
    """Consulta à LucIA sobre segurança e auditoria"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query é obrigatória'}), 400
        
        # Obter contexto de segurança
        security_context = get_security_context()
        
        # Fazer consulta à LucIA
        response = lucia_ai.analyze_security_query(query, security_context)
        
        # Registrar consulta como evento
        event = SecurityEvent(
            user_id=data.get('user_id', 'anonymous'),
            event_type='lucia_query',
            ip_address=request.remote_addr,
            timestamp=datetime.now(),
            details={
                'query': query,
                'response_length': len(response),
                'context_size': len(str(security_context))
            }
        )
        analyzer.log_security_event(event)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na consulta LucIA: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/lucia/insights', methods=['GET'])
def lucia_security_insights():
    """Obter insights de segurança da LucIA"""
    try:
        days = int(request.args.get('days', 7))
        
        # Gerar relatório de segurança
        report = analyzer.generate_security_report(days)
        
        # Obter alertas ativos
        alerts = analyzer.get_active_alerts()
        
        # Solicitar insights à LucIA
        insights = lucia_ai.generate_security_insights(report, alerts)
        
        return jsonify({
            'success': True,
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar insights: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@audit_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Obter estatísticas para dashboard"""
    try:
        days = int(request.args.get('days', 7))
        
        # Relatório básico
        report = analyzer.generate_security_report(days)
        
        # Alertas por severidade
        alerts = analyzer.get_active_alerts()
        alerts_by_severity = {}
        for alert in alerts:
            severity = alert['severity']
            alerts_by_severity[severity] = alerts_by_severity.get(severity, 0) + 1
        
        # Eventos das últimas 24 horas
        start_24h = datetime.now() - timedelta(hours=24)
        
        import sqlite3
        conn = sqlite3.connect(analyzer.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM security_events 
            WHERE timestamp > ?
        ''', (start_24h,))
        events_24h = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM security_events 
            WHERE timestamp > ? AND anomaly_detected = 1
        ''', (start_24h,))
        anomalies_24h = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_events': report['statistics']['total_events'],
                'anomalies_detected': report['statistics']['anomalies_detected'],
                'unique_users': report['statistics']['unique_users'],
                'unique_ips': report['statistics']['unique_ips'],
                'anomaly_rate': report['statistics']['anomaly_rate'],
                'events_24h': events_24h,
                'anomalies_24h': anomalies_24h,
                'active_alerts': len(alerts),
                'alerts_by_severity': alerts_by_severity,
                'period_days': days
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

def get_security_context() -> Dict[str, Any]:
    """Obter contexto de segurança para LucIA"""
    try:
        # Relatório dos últimos 7 dias
        report = analyzer.generate_security_report(7)
        
        # Alertas ativos
        alerts = analyzer.get_active_alerts()
        
        # Top IPs suspeitos
        suspicious_ips = report.get('suspicious_ips', [])
        
        # Usuários com anomalias
        users_with_anomalies = report.get('users_with_anomalies', [])
        
        return {
            'report_summary': {
                'total_events': report['statistics']['total_events'],
                'anomalies': report['statistics']['anomalies_detected'],
                'anomaly_rate': report['statistics']['anomaly_rate']
            },
            'active_alerts_count': len(alerts),
            'suspicious_ips_count': len(suspicious_ips),
            'users_with_anomalies_count': len(users_with_anomalies),
            'events_by_type': report.get('events_by_type', {}),
            'alerts_by_severity': report.get('alerts_by_severity', {})
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter contexto: {str(e)}")
        return {}

# Endpoints para simulação de dados (desenvolvimento)
@audit_bp.route('/simulate/events', methods=['POST'])
def simulate_security_events():
    """Simular eventos de segurança para testes"""
    try:
        data = request.get_json()
        count = data.get('count', 10)
        
        import random
        from datetime import datetime, timedelta
        
        event_types = ['login_success', 'login_failed', 'certificate_download', 
                      'admin_action', 'data_export', 'unauthorized_access']
        
        users = ['admin', 'user123', 'joao.silva', 'maria.santos', 'carlos.pereira']
        ips = ['192.168.1.100', '192.168.1.101', '10.0.0.1', '203.0.113.1', '198.51.100.1']
        
        events_created = 0
        
        for i in range(count):
            # Gerar evento aleatório
            event = SecurityEvent(
                user_id=random.choice(users),
                event_type=random.choice(event_types),
                ip_address=random.choice(ips),
                timestamp=datetime.now() - timedelta(
                    hours=random.randint(0, 168),  # Últimas 7 dias
                    minutes=random.randint(0, 59)
                ),
                details={
                    'user_agent': f'Chrome/{random.randint(90, 100)}.0',
                    'session_id': f'sess_{random.randint(1000, 9999)}',
                    'action': f'action_{random.randint(1, 100)}'
                },
                risk_score=random.uniform(0, 10),
                anomaly_detected=random.choice([True, False]) if random.random() < 0.2 else False
            )
            
            analyzer.log_security_event(event)
            events_created += 1
        
        return jsonify({
            'success': True,
            'message': f'{events_created} eventos simulados criados'
        })
        
    except Exception as e:
        logger.error(f"Erro ao simular eventos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

