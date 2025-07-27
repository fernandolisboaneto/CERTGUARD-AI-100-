"""
LucIA - Sistema de IA Jurídica Avançada com API NVIDIA
Análise comportamental, auditoria inteligente e assistência jurídica
"""

import requests
import json
import os
from datetime import datetime, timedelta
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass

@dataclass
class SecurityEvent:
    user_id: str
    event_type: str
    ip_address: str
    location: str
    timestamp: datetime
    details: Dict[str, Any]
    risk_score: float

class NvidiaLuciaAI:
    def __init__(self):
        # Configurações da API NVIDIA
        self.nvidia_configs = {
            'primary': {
                'api_key': 'nvapi-82_',  # Chave truncada por segurança
                'base_url': 'https://integrate.api.nvidia.com/v1',
                'model': 'meta/llama3-70b-instruct',
                'temperature': 0.5,
                'top_p': 1,
                'max_tokens': 1024,
                'stream': True
            },
            'secondary': {
                'api_key': 'nvapi-YdC',  # Chave truncada por segurança
                'base_url': 'https://integrate.api.nvidia.com/v1',
                'model': 'meta/llama-3.3-70b-instruct',
                'temperature': 0.2,
                'top_p': 0.7,
                'max_tokens': 1024,
                'stream': True
            }
        }
        
        # Base de conhecimento jurídico brasileiro
        self.legal_knowledge = {
            'tribunais': {
                'TJ-RJ': 'Tribunal de Justiça do Rio de Janeiro',
                'TJSP': 'Tribunal de Justiça de São Paulo',
                'TRF-2': 'Tribunal Regional Federal da 2ª Região',
                'PJe': 'Processo Judicial Eletrônico',
                'E-SAJ': 'Sistema de Automação da Justiça',
                'PROJUDI': 'Processo Judicial Digital'
            },
            'certificados': {
                'A1': 'Certificado digital armazenado em arquivo (.pfx/.p12)',
                'A3': 'Certificado digital em token/cartão inteligente',
                'ICP-Brasil': 'Infraestrutura de Chaves Públicas Brasileira'
            },
            'legislacao': {
                'LGPD': 'Lei Geral de Proteção de Dados',
                'CNJ': 'Conselho Nacional de Justiça',
                'CPC': 'Código de Processo Civil',
                'Marco Civil': 'Marco Civil da Internet'
            }
        }
        
        # Inicializar banco de dados para auditoria
        self.init_audit_database()
    
    def init_audit_database(self):
        """Inicializa banco de dados para auditoria e logs"""
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tabela de eventos de segurança
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                ip_address TEXT,
                location TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                risk_score REAL,
                analyzed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Tabela de consultas à LucIA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lucia_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                query_text TEXT NOT NULL,
                response_text TEXT,
                query_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                processing_time REAL,
                model_used TEXT
            )
        ''')
        
        # Tabela de análises comportamentais
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                findings TEXT,
                risk_level TEXT,
                recommendations TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def call_nvidia_api(self, prompt: str, config_key: str = 'primary') -> Dict[str, Any]:
        """Chama a API NVIDIA com o prompt fornecido"""
        config = self.nvidia_configs[config_key]
        
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': config['model'],
            'messages': [
                {
                    'role': 'system',
                    'content': self._get_system_prompt()
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': config['temperature'],
            'top_p': config['top_p'],
            'max_tokens': config['max_tokens'],
            'stream': config['stream']
        }
        
        try:
            response = requests.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'response': response.json(),
                    'model_used': config['model']
                }
            else:
                return {
                    'success': False,
                    'error': f'API Error: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}'
            }
    
    def _get_system_prompt(self) -> str:
        """Prompt do sistema para a LucIA"""
        return """Você é LucIA, uma assistente de IA especializada em direito brasileiro e segurança digital.

SUAS ESPECIALIDADES:
- Análise de segurança e auditoria de sistemas
- Direito digital e certificação digital (ICP-Brasil)
- Tribunais brasileiros (TJ-RJ, TJSP, TRF-2, PJe)
- LGPD e proteção de dados
- Análise comportamental de usuários
- Detecção de anomalias e fraudes

CONTEXTO DO SISTEMA:
- Sistema CertGuard AI de gestão de certificados digitais
- Usuários: advogados, empresas, órgãos públicos
- Funcionalidades: upload/download de certificados, automação de tribunais

SUAS FUNÇÕES:
1. ANÁLISE DE SEGURANÇA: Identificar acessos suspeitos, IPs diferentes, horários anômalos
2. AUDITORIA: Responder quem fez o quê, quando e onde no sistema
3. ASSISTÊNCIA JURÍDICA: Orientações sobre certificados digitais e tribunais
4. DETECÇÃO DE ANOMALIAS: Padrões de comportamento suspeitos

ESTILO DE RESPOSTA:
- Direto e profissional
- Use dados específicos quando disponível
- Destaque riscos de segurança
- Forneça recomendações práticas

Responda sempre em português brasileiro."""

    def analyze_security_event(self, user_id: str, event_type: str, ip_address: str, 
                             location: str = None, details: Dict = None) -> SecurityEvent:
        """Analisa evento de segurança e calcula score de risco"""
        
        # Calcular score de risco baseado em vários fatores
        risk_score = self._calculate_risk_score(user_id, event_type, ip_address, details)
        
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            location=location or self._get_location_from_ip(ip_address),
            timestamp=datetime.now(),
            details=details or {},
            risk_score=risk_score
        )
        
        # Salvar no banco de dados
        self._save_security_event(event)
        
        return event
    
    def _calculate_risk_score(self, user_id: str, event_type: str, ip_address: str, details: Dict) -> float:
        """Calcula score de risco de 0.0 a 1.0"""
        risk_score = 0.0
        
        # Fatores de risco
        risk_factors = {
            'login_failed': 0.3,
            'login_success_new_ip': 0.6,
            'login_success_new_location': 0.4,
            'multiple_failed_attempts': 0.8,
            'certificate_download': 0.2,
            'admin_action': 0.1,
            'unusual_hour': 0.3,
            'suspicious_user_agent': 0.5
        }
        
        # Score base por tipo de evento
        risk_score += risk_factors.get(event_type, 0.1)
        
        # Verificar histórico do usuário
        recent_events = self._get_recent_events(user_id, hours=24)
        
        # IP nunca usado antes
        if not self._ip_used_before(user_id, ip_address):
            risk_score += 0.4
        
        # Múltiplos IPs em pouco tempo
        unique_ips = len(set(event['ip_address'] for event in recent_events))
        if unique_ips > 3:
            risk_score += 0.3
        
        # Horário suspeito (madrugada)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 23:
            risk_score += 0.2
        
        # Múltiplas tentativas de login
        failed_logins = len([e for e in recent_events if e['event_type'] == 'login_failed'])
        if failed_logins > 3:
            risk_score += 0.4
        
        return min(risk_score, 1.0)  # Máximo 1.0
    
    def _get_location_from_ip(self, ip_address: str) -> str:
        """Simula obtenção de localização por IP"""
        # Em produção, usar serviço real de geolocalização
        ip_locations = {
            '192.168.1.1': 'São Paulo, SP',
            '10.0.0.1': 'Rio de Janeiro, RJ',
            '172.16.0.1': 'Brasília, DF',
            '127.0.0.1': 'Local'
        }
        return ip_locations.get(ip_address, 'Localização Desconhecida')
    
    def _save_security_event(self, event: SecurityEvent):
        """Salva evento de segurança no banco"""
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_events 
            (user_id, event_type, ip_address, location, timestamp, details, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.user_id,
            event.event_type,
            event.ip_address,
            event.location,
            event.timestamp.isoformat(),
            json.dumps(event.details),
            event.risk_score
        ))
        
        conn.commit()
        conn.close()
    
    def _get_recent_events(self, user_id: str, hours: int = 24) -> List[Dict]:
        """Obtém eventos recentes do usuário"""
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT * FROM security_events 
            WHERE user_id = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (user_id, since.isoformat()))
        
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
                'risk_score': row[7]
            })
        
        conn.close()
        return events
    
    def _ip_used_before(self, user_id: str, ip_address: str) -> bool:
        """Verifica se IP já foi usado pelo usuário"""
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM security_events 
            WHERE user_id = ? AND ip_address = ?
        ''', (user_id, ip_address))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    async def process_security_query(self, query: str, user_id: str = None) -> Dict[str, Any]:
        """Processa consulta de segurança usando IA"""
        
        # Enriquecer query com dados do sistema
        enriched_prompt = self._enrich_security_prompt(query, user_id)
        
        # Chamar API NVIDIA
        start_time = datetime.now()
        result = await self.call_nvidia_api(enriched_prompt, 'primary')
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if result['success']:
            response_text = result['response']['choices'][0]['message']['content']
            
            # Salvar consulta no banco
            self._save_lucia_query(user_id or 'system', query, response_text, 
                                 'security', processing_time, result['model_used'])
            
            return {
                'success': True,
                'response': response_text,
                'processing_time': processing_time,
                'model_used': result['model_used']
            }
        else:
            return result
    
    def _enrich_security_prompt(self, query: str, user_id: str = None) -> str:
        """Enriquece prompt com dados de contexto"""
        
        context_data = []
        
        if user_id:
            # Obter eventos recentes do usuário
            recent_events = self._get_recent_events(user_id, hours=168)  # 7 dias
            if recent_events:
                context_data.append(f"EVENTOS RECENTES DO USUÁRIO {user_id}:")
                for event in recent_events[:10]:  # Últimos 10 eventos
                    context_data.append(
                        f"- {event['timestamp']}: {event['event_type']} "
                        f"de {event['ip_address']} ({event['location']}) "
                        f"[Risco: {event['risk_score']:.2f}]"
                    )
        
        # Obter estatísticas gerais do sistema
        system_stats = self._get_system_statistics()
        context_data.append("ESTATÍSTICAS DO SISTEMA:")
        context_data.append(f"- Total de usuários ativos: {system_stats['active_users']}")
        context_data.append(f"- Eventos de segurança hoje: {system_stats['security_events_today']}")
        context_data.append(f"- Eventos de alto risco: {system_stats['high_risk_events']}")
        
        context = "\n".join(context_data)
        
        return f"""CONTEXTO DO SISTEMA:
{context}

CONSULTA DO USUÁRIO:
{query}

Analise a consulta considerando o contexto fornecido e responda de forma detalhada e profissional."""
    
    def _get_system_statistics(self) -> Dict[str, int]:
        """Obtém estatísticas do sistema para contexto"""
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        # Usuários únicos hoje
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM security_events 
            WHERE DATE(timestamp) = ?
        ''', (today.isoformat(),))
        active_users = cursor.fetchone()[0]
        
        # Eventos de segurança hoje
        cursor.execute('''
            SELECT COUNT(*) FROM security_events 
            WHERE DATE(timestamp) = ?
        ''', (today.isoformat(),))
        security_events_today = cursor.fetchone()[0]
        
        # Eventos de alto risco (score > 0.7)
        cursor.execute('''
            SELECT COUNT(*) FROM security_events 
            WHERE risk_score > 0.7 AND DATE(timestamp) = ?
        ''', (today.isoformat(),))
        high_risk_events = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'active_users': active_users,
            'security_events_today': security_events_today,
            'high_risk_events': high_risk_events
        }
    
    def _save_lucia_query(self, user_id: str, query: str, response: str, 
                         query_type: str, processing_time: float, model_used: str):
        """Salva consulta à LucIA no banco"""
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO lucia_queries 
            (user_id, query_text, response_text, query_type, processing_time, model_used)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, query, response, query_type, processing_time, model_used))
        
        conn.commit()
        conn.close()
    
    async def analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """Análise comportamental completa do usuário"""
        
        events = self._get_recent_events(user_id, hours=168)  # 7 dias
        
        if not events:
            return {
                'user_id': user_id,
                'analysis': 'Usuário sem atividade recente',
                'risk_level': 'low',
                'recommendations': ['Monitorar próximas atividades']
            }
        
        # Análise de padrões
        analysis_prompt = f"""
        Analise o comportamento do usuário {user_id} baseado nos seguintes eventos:
        
        {json.dumps(events[:20], indent=2)}
        
        Identifique:
        1. Padrões de acesso (horários, IPs, localizações)
        2. Comportamentos suspeitos ou anômalos
        3. Nível de risco (low, medium, high)
        4. Recomendações de segurança
        
        Responda em formato JSON com as chaves: analysis, risk_level, recommendations, patterns
        """
        
        result = await self.call_nvidia_api(analysis_prompt, 'secondary')
        
        if result['success']:
            try:
                # Tentar extrair JSON da resposta
                response_text = result['response']['choices'][0]['message']['content']
                
                # Salvar análise no banco
                self._save_behavior_analysis(user_id, response_text)
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'analysis': response_text,
                    'events_analyzed': len(events),
                    'model_used': result['model_used']
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Erro ao processar análise: {str(e)}'
                }
        else:
            return result
    
    def _save_behavior_analysis(self, user_id: str, analysis: str):
        """Salva análise comportamental no banco"""
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO behavior_analysis 
            (user_id, analysis_type, findings, risk_level, recommendations)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, 'behavioral', analysis, 'medium', 'Ver análise completa'))
        
        conn.commit()
        conn.close()
    
    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Dados para dashboard de segurança"""
        db_path = '/home/ubuntu/CERTGUARD-AI-100/backend/lucia_audit.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Eventos por tipo hoje
        today = datetime.now().date()
        cursor.execute('''
            SELECT event_type, COUNT(*) FROM security_events 
            WHERE DATE(timestamp) = ?
            GROUP BY event_type
        ''', (today.isoformat(),))
        events_by_type = dict(cursor.fetchall())
        
        # Top IPs com mais eventos
        cursor.execute('''
            SELECT ip_address, COUNT(*) as count FROM security_events 
            WHERE DATE(timestamp) = ?
            GROUP BY ip_address
            ORDER BY count DESC
            LIMIT 10
        ''', (today.isoformat(),))
        top_ips = cursor.fetchall()
        
        # Eventos de alto risco
        cursor.execute('''
            SELECT * FROM security_events 
            WHERE risk_score > 0.7 AND DATE(timestamp) = ?
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (today.isoformat(),))
        high_risk_events = cursor.fetchall()
        
        conn.close()
        
        return {
            'events_by_type': events_by_type,
            'top_ips': top_ips,
            'high_risk_events': high_risk_events,
            'total_events_today': sum(events_by_type.values()),
            'high_risk_count': len(high_risk_events)
        }

# Instância global da LucIA
lucia_ai = NvidiaLuciaAI()

