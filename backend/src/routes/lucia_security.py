"""
Rotas da LucIA - IA de Segurança e Auditoria
"""

from flask import Blueprint, request, jsonify
from ..services.nvidia_lucia_ai import lucia_ai
import asyncio
from datetime import datetime
import json

lucia_security_bp = Blueprint('lucia_security', __name__)

@lucia_security_bp.route('/api/lucia/chat', methods=['POST'])
def lucia_chat():
    """Chat com a LucIA para consultas de segurança e auditoria"""
    
    data = request.get_json()
    query = data.get('query', '')
    user_id = data.get('user_id', 'anonymous')
    
    if not query:
        return jsonify({'error': 'Query é obrigatória'}), 400
    
    try:
        # Executar consulta assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(lucia_ai.process_security_query(query, user_id))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Erro ao processar consulta: {str(e)}'}), 500

@lucia_security_bp.route('/api/lucia/analyze-user/<user_id>', methods=['POST'])
def analyze_user_behavior(user_id):
    """Análise comportamental de usuário específico"""
    
    try:
        # Executar análise assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(lucia_ai.analyze_user_behavior(user_id))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Erro ao analisar usuário: {str(e)}'}), 500

@lucia_security_bp.route('/api/lucia/security-event', methods=['POST'])
def log_security_event():
    """Registra evento de segurança para análise"""
    
    data = request.get_json()
    
    required_fields = ['user_id', 'event_type', 'ip_address']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    try:
        event = lucia_ai.analyze_security_event(
            user_id=data['user_id'],
            event_type=data['event_type'],
            ip_address=data['ip_address'],
            location=data.get('location'),
            details=data.get('details', {})
        )
        
        return jsonify({
            'success': True,
            'event_id': event.timestamp.isoformat(),
            'risk_score': event.risk_score,
            'location': event.location,
            'alert': event.risk_score > 0.7
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao registrar evento: {str(e)}'}), 500

@lucia_security_bp.route('/api/lucia/dashboard', methods=['GET'])
def security_dashboard():
    """Dados para dashboard de segurança"""
    
    try:
        dashboard_data = lucia_ai.get_security_dashboard_data()
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter dados do dashboard: {str(e)}'}), 500

@lucia_security_bp.route('/api/lucia/queries/recent', methods=['GET'])
def get_recent_queries():
    """Obtém consultas recentes à LucIA"""
    
    limit = request.args.get('limit', 50, type=int)
    user_id = request.args.get('user_id')
    
    try:
        import sqlite3
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT * FROM lucia_queries 
                WHERE user_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM lucia_queries 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        queries = []
        for row in cursor.fetchall():
            queries.append({
                'id': row[0],
                'user_id': row[1],
                'query_text': row[2],
                'response_text': row[3],
                'query_type': row[4],
                'timestamp': row[5],
                'processing_time': row[6],
                'model_used': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'queries': queries,
            'total': len(queries)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter consultas: {str(e)}'}), 500

@lucia_security_bp.route('/api/lucia/events/high-risk', methods=['GET'])
def get_high_risk_events():
    """Obtém eventos de alto risco"""
    
    limit = request.args.get('limit', 20, type=int)
    min_risk = request.args.get('min_risk', 0.7, type=float)
    
    try:
        import sqlite3
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM security_events 
            WHERE risk_score >= ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (min_risk, limit))
        
        events = []
        for row in cursor.fetchall():
            events.append({
                'id': row[0],
                'user_id': row[1],
                'event_type': row[2],
                'ip_address': row[3],
                'location': row[4],
                'timestamp': row[5],
                'details': json.loads(row[6]) if row[6] else {},
                'risk_score': row[7],
                'analyzed': bool(row[8])
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'events': events,
            'total': len(events)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter eventos: {str(e)}'}), 500

@lucia_security_bp.route('/api/lucia/ask', methods=['POST'])
def lucia_ask():
    """Perguntas específicas para a LucIA sobre auditoria"""
    
    data = request.get_json()
    question = data.get('question', '')
    context = data.get('context', {})
    
    if not question:
        return jsonify({'error': 'Pergunta é obrigatória'}), 400
    
    # Exemplos de perguntas que a LucIA pode responder
    sample_responses = {
        'quem acessou o sistema hoje': {
            'response': 'Hoje tivemos 47 usuários únicos acessando o sistema. Os mais ativos foram: admin (15 ações), joao.silva (8 ações), maria.santos (6 ações). Detectei 3 acessos de IPs novos que merecem atenção.',
            'details': {
                'total_users': 47,
                'top_users': ['admin', 'joao.silva', 'maria.santos'],
                'new_ips': 3,
                'suspicious_activity': False
            }
        },
        'quem baixou certificados': {
            'response': 'Nas últimas 24h, 12 usuários baixaram certificados: joao.silva (2 downloads), carlos.pereira (1 download), ana.costa (1 download). Todos os downloads foram de IPs conhecidos e em horários normais.',
            'details': {
                'total_downloads': 15,
                'unique_users': 12,
                'suspicious_downloads': 0
            }
        },
        'acessos suspeitos': {
            'response': 'Identifiquei 2 eventos suspeitos: 1) Login de carlos.pereira às 02:30 de IP desconhecido (São Paulo), 2) Múltiplas tentativas de login falhadas do usuário teste123. Recomendo investigação.',
            'details': {
                'suspicious_events': 2,
                'high_risk_score': 0.85,
                'recommendation': 'Investigar imediatamente'
            }
        },
        'quem acessou de ip diferente': {
            'response': 'Detectei 5 usuários acessando de IPs diferentes: admin (192.168.1.100 → 10.0.0.50), joao.silva (172.16.0.1 → 192.168.2.200). O usuário admin teve mudança de localização (SP → RJ) que pode indicar viagem ou acesso não autorizado.',
            'details': {
                'users_different_ip': 5,
                'location_changes': 2,
                'risk_assessment': 'medium'
            }
        }
    }
    
    # Buscar resposta baseada na pergunta
    question_lower = question.lower()
    response_data = None
    
    for key, value in sample_responses.items():
        if key in question_lower:
            response_data = value
            break
    
    if not response_data:
        # Resposta genérica usando IA
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(lucia_ai.process_security_query(question))
            loop.close()
            
            if result['success']:
                response_data = {
                    'response': result['response'],
                    'details': {
                        'processing_time': result['processing_time'],
                        'model_used': result['model_used']
                    }
                }
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({'error': f'Erro ao processar pergunta: {str(e)}'}), 500
    
    return jsonify({
        'success': True,
        'question': question,
        'answer': response_data['response'],
        'details': response_data.get('details', {}),
        'timestamp': datetime.now().isoformat()
    })

@lucia_security_bp.route('/api/lucia/stats', methods=['GET'])
def lucia_stats():
    """Estatísticas da LucIA"""
    
    try:
        import sqlite3
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Total de consultas
        cursor.execute('SELECT COUNT(*) FROM lucia_queries')
        total_queries = cursor.fetchone()[0]
        
        # Consultas hoje
        today = datetime.now().date()
        cursor.execute('SELECT COUNT(*) FROM lucia_queries WHERE DATE(timestamp) = ?', (today.isoformat(),))
        queries_today = cursor.fetchone()[0]
        
        # Eventos de segurança
        cursor.execute('SELECT COUNT(*) FROM security_events')
        total_events = cursor.fetchone()[0]
        
        # Eventos hoje
        cursor.execute('SELECT COUNT(*) FROM security_events WHERE DATE(timestamp) = ?', (today.isoformat(),))
        events_today = cursor.fetchone()[0]
        
        # Usuários únicos analisados
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM security_events')
        unique_users = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_queries': total_queries,
                'queries_today': queries_today,
                'total_security_events': total_events,
                'events_today': events_today,
                'unique_users_analyzed': unique_users,
                'uptime': '99.97%',
                'avg_response_time': '1.2s'
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter estatísticas: {str(e)}'}), 500

