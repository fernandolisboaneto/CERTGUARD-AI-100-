"""
CertGuard AI - LucIA Database Analyzer
Sistema avançado de análise de banco de dados, comportamento e auditoria
"""

import os
import json
import asyncio
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import re
from collections import defaultdict, Counter
import numpy as np
from dataclasses import dataclass

from .nvidia_ai import nvidia_ai_service
from .blockchain_audit import blockchain_audit_service
from .lucia_security_ai import lucia_security_ai

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseQuery:
    """Consulta ao banco de dados"""
    id: str
    timestamp: str
    user_id: str
    query_type: str
    sql_query: str
    results_count: int
    execution_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class BehaviorPattern:
    """Padrão comportamental detectado"""
    pattern_id: str
    user_id: str
    pattern_type: str
    description: str
    frequency: int
    confidence: float
    first_seen: str
    last_seen: str
    risk_level: str

class LucIADatabaseAnalyzer:
    """Analisador avançado de banco de dados e comportamento"""
    
    def __init__(self, db_path: str = "/tmp/certguard.db"):
        self.db_path = db_path
        self.query_history: List[DatabaseQuery] = []
        self.behavior_patterns: List[BehaviorPattern] = []
        
        # Configurações de análise
        self.analysis_config = {
            "max_query_history": 10000,
            "behavior_analysis_window_days": 30,
            "anomaly_threshold": 2.5,  # desvios padrão
            "min_pattern_frequency": 3,
            "confidence_threshold": 0.7
        }
        
        # Métricas de performance
        self.performance_metrics = {
            "total_queries": 0,
            "avg_query_time": 0.0,
            "slow_queries": 0,
            "failed_queries": 0,
            "unique_users": set(),
            "peak_usage_hour": 0
        }
        
        # Cache de análises
        self.analysis_cache = {}
        
        # Inicializar banco de dados
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados com dados de exemplo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criar tabelas se não existirem
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    email TEXT,
                    full_name TEXT,
                    role TEXT,
                    organization_id INTEGER,
                    created_at TEXT,
                    last_login TEXT,
                    login_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS certificates (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    certificate_type TEXT,
                    serial_number TEXT,
                    subject_name TEXT,
                    issuer_name TEXT,
                    valid_from TEXT,
                    valid_until TEXT,
                    status TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    cnpj TEXT,
                    type TEXT,
                    status TEXT,
                    created_at TEXT,
                    user_count INTEGER DEFAULT 0,
                    certificate_count INTEGER DEFAULT 0
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    action TEXT,
                    resource_type TEXT,
                    resource_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TEXT,
                    success BOOLEAN,
                    session_id TEXT,
                    response_time REAL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    event_type TEXT,
                    description TEXT,
                    details TEXT,
                    severity TEXT,
                    timestamp TEXT,
                    ip_address TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Inserir dados de exemplo se as tabelas estiverem vazias
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self._insert_sample_data(cursor)
            
            conn.commit()
            conn.close()
            
            logger.info("Banco de dados inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
    
    def _insert_sample_data(self, cursor):
        """Insere dados de exemplo no banco"""
        
        # Organizações
        organizations = [
            (1, "Advocacia Silva & Associados", "12.345.678/0001-90", "law_firm", "active", "2023-01-15T10:00:00", 15, 25),
            (2, "Tribunal de Justiça RJ", "98.765.432/0001-10", "court", "active", "2022-06-01T09:00:00", 150, 200),
            (3, "Cartório Central", "11.222.333/0001-44", "notary", "active", "2023-03-20T14:30:00", 8, 12),
            (4, "Ministério Público", "55.666.777/0001-88", "prosecutor", "active", "2022-01-01T08:00:00", 80, 120)
        ]
        
        cursor.executemany("""
            INSERT INTO organizations (id, name, cnpj, type, status, created_at, user_count, certificate_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, organizations)
        
        # Usuários
        users = [
            (1, "admin", "admin@certguard.ai", "Administrador Sistema", "superadmin", 1, "2023-01-15T10:00:00", "2024-01-27T08:30:00", 1247, "active"),
            (2, "joao.silva", "joao@silva.adv.br", "João Silva", "lawyer", 1, "2023-02-01T09:00:00", "2024-01-27T07:45:00", 892, "active"),
            (3, "maria.santos", "maria@tjrj.jus.br", "Maria Santos", "judge", 2, "2023-01-20T11:00:00", "2024-01-26T16:20:00", 654, "active"),
            (4, "carlos.oliveira", "carlos@mp.rj.gov.br", "Carlos Oliveira", "prosecutor", 4, "2023-03-10T14:00:00", "2024-01-27T09:15:00", 423, "active"),
            (5, "ana.costa", "ana@cartorio.com.br", "Ana Costa", "notary", 3, "2023-04-05T16:00:00", "2024-01-25T13:40:00", 234, "active"),
            (6, "pedro.hacker", "pedro@suspicious.com", "Pedro Hacker", "user", 1, "2024-01-20T02:30:00", "2024-01-27T03:15:00", 15, "suspended")
        ]
        
        cursor.executemany("""
            INSERT INTO users (id, username, email, full_name, role, organization_id, created_at, last_login, login_count, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, users)
        
        # Certificados
        certificates = [
            (1, 1, "A3", "1234567890ABCDEF", "CN=Admin CertGuard", "CN=AC CertGuard", "2023-01-01T00:00:00", "2026-01-01T00:00:00", "active", 156, "2023-01-15T10:00:00"),
            (2, 2, "A1", "2345678901BCDEFG", "CN=João Silva:12345678901", "CN=AC Serasa", "2023-02-01T00:00:00", "2024-02-01T00:00:00", "active", 89, "2023-02-01T09:00:00"),
            (3, 3, "A3", "3456789012CDEFGH", "CN=Maria Santos:98765432100", "CN=AC TJRJ", "2023-01-20T00:00:00", "2026-01-20T00:00:00", "active", 234, "2023-01-20T11:00:00"),
            (4, 4, "A3", "4567890123DEFGHI", "CN=Carlos Oliveira:11122233344", "CN=AC MPRJ", "2023-03-10T00:00:00", "2026-03-10T00:00:00", "active", 67, "2023-03-10T14:00:00"),
            (5, 5, "A1", "5678901234EFGHIJ", "CN=Ana Costa:55566677788", "CN=AC Cartório", "2023-04-05T00:00:00", "2024-04-05T00:00:00", "active", 45, "2023-04-05T16:00:00"),
            (6, 6, "A1", "6789012345FGHIJK", "CN=Pedro Hacker:99988877766", "CN=AC Suspeita", "2024-01-20T00:00:00", "2025-01-20T00:00:00", "revoked", 8, "2024-01-20T02:30:00")
        ]
        
        cursor.executemany("""
            INSERT INTO certificates (id, user_id, certificate_type, serial_number, subject_name, issuer_name, valid_from, valid_until, status, usage_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, certificates)
        
        # Logs de acesso (últimos 7 dias)
        base_time = datetime.now() - timedelta(days=7)
        access_logs = []
        
        for day in range(7):
            current_day = base_time + timedelta(days=day)
            
            # Simula atividade normal durante o dia
            for hour in range(8, 18):  # Horário comercial
                for _ in range(np.random.poisson(5)):  # Média de 5 acessos por hora
                    user_id = np.random.choice([1, 2, 3, 4, 5], p=[0.3, 0.25, 0.2, 0.15, 0.1])
                    timestamp = current_day.replace(hour=hour, minute=np.random.randint(0, 60))
                    
                    actions = ["login", "view_certificate", "download_document", "sign_document", "logout"]
                    action = np.random.choice(actions, p=[0.1, 0.3, 0.2, 0.3, 0.1])
                    
                    access_logs.append((
                        len(access_logs) + 1,
                        user_id,
                        action,
                        "certificate" if "certificate" in action else "document",
                        f"cert_{np.random.randint(1, 6)}",
                        f"192.168.1.{np.random.randint(100, 200)}",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        timestamp.isoformat(),
                        True,
                        f"session_{np.random.randint(1000, 9999)}",
                        np.random.uniform(0.1, 2.0)
                    ))
            
            # Simula atividade suspeita do usuário 6
            if day >= 5:  # Últimos 2 dias
                for _ in range(np.random.randint(3, 8)):
                    timestamp = current_day.replace(
                        hour=np.random.randint(2, 5),  # Madrugada
                        minute=np.random.randint(0, 60)
                    )
                    
                    access_logs.append((
                        len(access_logs) + 1,
                        6,  # Pedro Hacker
                        "failed_login",
                        "authentication",
                        "login_attempt",
                        f"10.0.0.{np.random.randint(1, 50)}",  # IP suspeito
                        "curl/7.68.0",  # User agent suspeito
                        timestamp.isoformat(),
                        False,
                        f"session_{np.random.randint(1000, 9999)}",
                        np.random.uniform(5.0, 15.0)  # Tempo alto
                    ))
        
        cursor.executemany("""
            INSERT INTO access_logs (id, user_id, action, resource_type, resource_id, ip_address, user_agent, timestamp, success, session_id, response_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, access_logs)
        
        # Eventos de auditoria
        audit_events = [
            (1, 1, "system_config", "Configuração de sistema alterada", '{"setting": "max_login_attempts", "old_value": 3, "new_value": 5}', "medium", "2024-01-25T10:30:00", "192.168.1.100", True),
            (2, 6, "suspicious_activity", "Múltiplas tentativas de login falhadas", '{"attempts": 15, "time_window": "1 hour", "ips": ["10.0.0.15", "10.0.0.23"]}', "high", "2024-01-26T03:45:00", "10.0.0.15", False),
            (3, 2, "certificate_usage", "Certificado usado fora do horário normal", '{"certificate_id": 2, "time": "23:45", "action": "sign_document"}', "low", "2024-01-26T23:45:00", "192.168.1.150", True),
            (4, 6, "security_violation", "Tentativa de acesso com certificado revogado", '{"certificate_id": 6, "status": "revoked", "attempted_action": "sign_document"}', "critical", "2024-01-27T02:15:00", "10.0.0.30", False),
            (5, 3, "data_export", "Exportação de dados sensíveis", '{"exported_records": 1500, "data_type": "user_certificates", "format": "CSV"}', "medium", "2024-01-27T14:20:00", "192.168.1.120", True)
        ]
        
        cursor.executemany("""
            INSERT INTO audit_events (id, user_id, event_type, description, details, severity, timestamp, ip_address, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, audit_events)
    
    async def analyze_user_behavior(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Analisa comportamento detalhado do usuário"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Query base para análise comportamental
            if user_id:
                where_clause = "WHERE al.user_id = ? AND al.timestamp >= ?"
                params = [user_id, (datetime.now() - timedelta(days=days)).isoformat()]
            else:
                where_clause = "WHERE al.timestamp >= ?"
                params = [(datetime.now() - timedelta(days=days)).isoformat()]
            
            # Análise de atividades
            activity_query = f"""
                SELECT 
                    u.username,
                    u.full_name,
                    u.role,
                    o.name as organization,
                    COUNT(*) as total_activities,
                    COUNT(DISTINCT DATE(al.timestamp)) as active_days,
                    AVG(al.response_time) as avg_response_time,
                    COUNT(CASE WHEN al.success = 0 THEN 1 END) as failed_attempts,
                    COUNT(DISTINCT al.ip_address) as unique_ips,
                    COUNT(DISTINCT al.session_id) as unique_sessions,
                    MIN(al.timestamp) as first_activity,
                    MAX(al.timestamp) as last_activity
                FROM access_logs al
                JOIN users u ON al.user_id = u.id
                JOIN organizations o ON u.organization_id = o.id
                {where_clause}
                GROUP BY al.user_id, u.username, u.full_name, u.role, o.name
                ORDER BY total_activities DESC
            """
            
            df_activity = pd.read_sql_query(activity_query, conn, params=params)
            
            # Análise de padrões temporais
            temporal_query = f"""
                SELECT 
                    al.user_id,
                    u.username,
                    strftime('%H', al.timestamp) as hour,
                    strftime('%w', al.timestamp) as day_of_week,
                    COUNT(*) as activity_count
                FROM access_logs al
                JOIN users u ON al.user_id = u.id
                {where_clause}
                GROUP BY al.user_id, u.username, hour, day_of_week
            """
            
            df_temporal = pd.read_sql_query(temporal_query, conn, params=params)
            
            # Análise de ações
            action_query = f"""
                SELECT 
                    al.user_id,
                    u.username,
                    al.action,
                    COUNT(*) as count,
                    AVG(al.response_time) as avg_time,
                    COUNT(CASE WHEN al.success = 0 THEN 1 END) as failures
                FROM access_logs al
                JOIN users u ON al.user_id = u.id
                {where_clause}
                GROUP BY al.user_id, u.username, al.action
                ORDER BY count DESC
            """
            
            df_actions = pd.read_sql_query(action_query, conn, params=params)
            
            # Análise de IPs
            ip_query = f"""
                SELECT 
                    al.user_id,
                    u.username,
                    al.ip_address,
                    COUNT(*) as usage_count,
                    MIN(al.timestamp) as first_seen,
                    MAX(al.timestamp) as last_seen,
                    COUNT(CASE WHEN al.success = 0 THEN 1 END) as failed_attempts
                FROM access_logs al
                JOIN users u ON al.user_id = u.id
                {where_clause}
                GROUP BY al.user_id, u.username, al.ip_address
                ORDER BY usage_count DESC
            """
            
            df_ips = pd.read_sql_query(ip_query, conn, params=params)
            
            conn.close()
            
            # Processa dados para análise
            analysis_result = {
                "analysis_period": {
                    "days": days,
                    "start_date": (datetime.now() - timedelta(days=days)).isoformat(),
                    "end_date": datetime.now().isoformat()
                },
                "user_summary": df_activity.to_dict('records'),
                "temporal_patterns": self._analyze_temporal_patterns(df_temporal),
                "action_patterns": self._analyze_action_patterns(df_actions),
                "ip_analysis": self._analyze_ip_patterns(df_ips),
                "anomalies": await self._detect_behavioral_anomalies(df_activity, df_temporal, df_actions),
                "risk_assessment": self._assess_user_risks(df_activity, df_ips, df_actions)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Erro na análise comportamental: {str(e)}")
            return {"error": str(e)}
    
    async def query_audit_logs(self, 
                             query: str,
                             user_id: str = None,
                             start_date: str = None,
                             end_date: str = None,
                             severity: str = None) -> Dict[str, Any]:
        """Consulta logs de auditoria com filtros avançados"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Constrói query dinâmica
            base_query = """
                SELECT 
                    ae.id,
                    ae.user_id,
                    u.username,
                    u.full_name,
                    u.role,
                    o.name as organization,
                    ae.event_type,
                    ae.description,
                    ae.details,
                    ae.severity,
                    ae.timestamp,
                    ae.ip_address,
                    ae.resolved
                FROM audit_events ae
                JOIN users u ON ae.user_id = u.id
                JOIN organizations o ON u.organization_id = o.id
                WHERE 1=1
            """
            
            params = []
            
            if user_id:
                base_query += " AND ae.user_id = ?"
                params.append(user_id)
            
            if start_date:
                base_query += " AND ae.timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                base_query += " AND ae.timestamp <= ?"
                params.append(end_date)
            
            if severity:
                base_query += " AND ae.severity = ?"
                params.append(severity)
            
            # Busca textual
            if query:
                base_query += " AND (ae.description LIKE ? OR ae.details LIKE ? OR u.username LIKE ?)"
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
            
            base_query += " ORDER BY ae.timestamp DESC LIMIT 1000"
            
            df_audit = pd.read_sql_query(base_query, conn, params=params)
            
            # Análise estatística dos resultados
            if not df_audit.empty:
                severity_counts = df_audit['severity'].value_counts().to_dict()
                event_type_counts = df_audit['event_type'].value_counts().to_dict()
                user_counts = df_audit['username'].value_counts().to_dict()
                
                # Análise temporal
                df_audit['timestamp'] = pd.to_datetime(df_audit['timestamp'])
                df_audit['hour'] = df_audit['timestamp'].dt.hour
                df_audit['day_of_week'] = df_audit['timestamp'].dt.day_name()
                
                hourly_distribution = df_audit['hour'].value_counts().sort_index().to_dict()
                daily_distribution = df_audit['day_of_week'].value_counts().to_dict()
                
                # Eventos não resolvidos
                unresolved_events = df_audit[df_audit['resolved'] == False]
                
                analysis = {
                    "total_events": len(df_audit),
                    "severity_distribution": severity_counts,
                    "event_type_distribution": event_type_counts,
                    "user_distribution": user_counts,
                    "temporal_analysis": {
                        "hourly_distribution": hourly_distribution,
                        "daily_distribution": daily_distribution
                    },
                    "unresolved_events": len(unresolved_events),
                    "critical_events": len(df_audit[df_audit['severity'] == 'critical']),
                    "high_severity_events": len(df_audit[df_audit['severity'] == 'high'])
                }
            else:
                analysis = {"message": "Nenhum evento encontrado com os critérios especificados"}
            
            conn.close()
            
            return {
                "query_params": {
                    "query": query,
                    "user_id": user_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "severity": severity
                },
                "events": df_audit.to_dict('records'),
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na consulta de auditoria: {str(e)}")
            return {"error": str(e)}
    
    async def answer_security_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Responde perguntas sobre segurança, auditoria e comportamento"""
        
        # Analisa a pergunta para determinar o tipo de consulta
        question_analysis = self._analyze_question(question)
        
        # Coleta dados relevantes baseado na pergunta
        relevant_data = await self._gather_relevant_data(question_analysis)
        
        # Constrói prompt para IA
        prompt = self._build_analysis_prompt(question, question_analysis, relevant_data, context)
        
        try:
            # Usa NVIDIA AI para análise
            response = await nvidia_ai_service._make_api_request(prompt, context="database_analysis")
            
            # Processa resposta
            analysis = self._process_analysis_response(response, question, relevant_data)
            
            return {
                "success": True,
                "question": question,
                "question_type": question_analysis["type"],
                "analysis": analysis,
                "data_sources": relevant_data.get("sources", []),
                "confidence": analysis.get("confidence", 0.8),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de pergunta: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "question": question
            }
    
    def _analyze_question(self, question: str) -> Dict[str, Any]:
        """Analisa a pergunta para determinar tipo e parâmetros"""
        
        question_lower = question.lower()
        
        # Padrões de perguntas
        patterns = {
            "user_activity": [
                r"quem (acessou|usou|fez|logou)",
                r"qual usuário",
                r"atividade do usuário",
                r"comportamento do",
                r"(login|acesso) do"
            ],
            "security_incident": [
                r"(tentativa|ataque|invasão|hack)",
                r"(suspeito|suspeita|anômalo|anormal)",
                r"(falha|erro) de (login|acesso)",
                r"ip (diferente|novo|suspeito)",
                r"horário (estranho|incomum|fora)"
            ],
            "audit_query": [
                r"quando (foi|aconteceu)",
                r"histórico de",
                r"log de",
                r"auditoria",
                r"registro de"
            ],
            "certificate_usage": [
                r"certificado",
                r"assinatura",
                r"(a1|a3)",
                r"(válido|expirado|revogado)"
            ],
            "performance_analysis": [
                r"(lento|lentidão|performance)",
                r"tempo de (resposta|carregamento)",
                r"(demora|demorou)",
                r"(rápido|velocidade)"
            ],
            "statistical_query": [
                r"quantos",
                r"qual a (média|total|soma)",
                r"estatística",
                r"relatório",
                r"(mais|menos) (usado|ativo)"
            ]
        }
        
        # Detecta tipo da pergunta
        question_type = "general"
        matched_patterns = []
        
        for qtype, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, question_lower):
                    question_type = qtype
                    matched_patterns.append(pattern)
                    break
        
        # Extrai entidades mencionadas
        entities = {
            "users": re.findall(r"usuário (\w+)|user (\w+)", question_lower),
            "ips": re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", question),
            "dates": re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", question),
            "times": re.findall(r"\b\d{1,2}:\d{2}\b", question),
            "actions": re.findall(r"(login|logout|acesso|download|upload|assinatura)", question_lower)
        }
        
        # Detecta período temporal
        time_indicators = {
            "hoje": 1,
            "ontem": 1,
            "última semana": 7,
            "último mês": 30,
            "últimos 7 dias": 7,
            "últimos 30 dias": 30,
            "esta semana": 7,
            "este mês": 30
        }
        
        time_period = None
        for indicator, days in time_indicators.items():
            if indicator in question_lower:
                time_period = days
                break
        
        return {
            "type": question_type,
            "matched_patterns": matched_patterns,
            "entities": entities,
            "time_period": time_period,
            "complexity": len(matched_patterns) + len([e for e in entities.values() if e])
        }
    
    async def _gather_relevant_data(self, question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Coleta dados relevantes baseado na análise da pergunta"""
        
        data = {"sources": []}
        question_type = question_analysis["type"]
        time_period = question_analysis.get("time_period", 7)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Dados básicos sempre incluídos
            if question_type in ["user_activity", "general", "statistical_query"]:
                # Atividade recente dos usuários
                user_activity_query = """
                    SELECT 
                        u.id, u.username, u.full_name, u.role, u.status,
                        o.name as organization,
                        COUNT(al.id) as recent_activities,
                        MAX(al.timestamp) as last_activity,
                        COUNT(DISTINCT al.ip_address) as unique_ips
                    FROM users u
                    LEFT JOIN organizations o ON u.organization_id = o.id
                    LEFT JOIN access_logs al ON u.id = al.user_id 
                        AND al.timestamp >= ?
                    GROUP BY u.id, u.username, u.full_name, u.role, u.status, o.name
                    ORDER BY recent_activities DESC
                """
                
                start_date = (datetime.now() - timedelta(days=time_period)).isoformat()
                df_users = pd.read_sql_query(user_activity_query, conn, params=[start_date])
                data["user_activity"] = df_users.to_dict('records')
                data["sources"].append("user_activity")
            
            if question_type in ["security_incident", "audit_query", "general"]:
                # Eventos de segurança recentes
                security_query = """
                    SELECT 
                        ae.*, u.username, u.full_name, o.name as organization
                    FROM audit_events ae
                    JOIN users u ON ae.user_id = u.id
                    JOIN organizations o ON u.organization_id = o.id
                    WHERE ae.timestamp >= ?
                    ORDER BY ae.timestamp DESC
                    LIMIT 100
                """
                
                start_date = (datetime.now() - timedelta(days=time_period)).isoformat()
                df_security = pd.read_sql_query(security_query, conn, params=[start_date])
                data["security_events"] = df_security.to_dict('records')
                data["sources"].append("security_events")
            
            if question_type in ["certificate_usage", "general"]:
                # Uso de certificados
                cert_query = """
                    SELECT 
                        c.*, u.username, u.full_name,
                        COUNT(al.id) as recent_usage
                    FROM certificates c
                    JOIN users u ON c.user_id = u.id
                    LEFT JOIN access_logs al ON u.id = al.user_id 
                        AND al.action LIKE '%certificate%'
                        AND al.timestamp >= ?
                    GROUP BY c.id, c.user_id, c.certificate_type, c.serial_number, 
                             c.subject_name, c.status, u.username, u.full_name
                    ORDER BY recent_usage DESC
                """
                
                start_date = (datetime.now() - timedelta(days=time_period)).isoformat()
                df_certs = pd.read_sql_query(cert_query, conn, params=[start_date])
                data["certificate_usage"] = df_certs.to_dict('records')
                data["sources"].append("certificate_usage")
            
            if question_type in ["performance_analysis", "general"]:
                # Análise de performance
                perf_query = """
                    SELECT 
                        al.action,
                        COUNT(*) as count,
                        AVG(al.response_time) as avg_response_time,
                        MAX(al.response_time) as max_response_time,
                        MIN(al.response_time) as min_response_time,
                        COUNT(CASE WHEN al.response_time > 5.0 THEN 1 END) as slow_requests
                    FROM access_logs al
                    WHERE al.timestamp >= ?
                    GROUP BY al.action
                    ORDER BY avg_response_time DESC
                """
                
                start_date = (datetime.now() - timedelta(days=time_period)).isoformat()
                df_perf = pd.read_sql_query(perf_query, conn, params=[start_date])
                data["performance_metrics"] = df_perf.to_dict('records')
                data["sources"].append("performance_metrics")
            
            # Logs de acesso detalhados para análises específicas
            if question_type in ["user_activity", "security_incident", "audit_query"]:
                access_query = """
                    SELECT 
                        al.*, u.username, u.full_name, u.role
                    FROM access_logs al
                    JOIN users u ON al.user_id = u.id
                    WHERE al.timestamp >= ?
                    ORDER BY al.timestamp DESC
                    LIMIT 500
                """
                
                start_date = (datetime.now() - timedelta(days=time_period)).isoformat()
                df_access = pd.read_sql_query(access_query, conn, params=[start_date])
                data["access_logs"] = df_access.to_dict('records')
                data["sources"].append("access_logs")
            
            conn.close()
            
            # Adiciona estatísticas gerais
            data["statistics"] = {
                "total_users": len(data.get("user_activity", [])),
                "total_security_events": len(data.get("security_events", [])),
                "total_certificates": len(data.get("certificate_usage", [])),
                "analysis_period_days": time_period,
                "data_collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados: {str(e)}")
            data["error"] = str(e)
        
        return data
    
    def _build_analysis_prompt(self, 
                             question: str, 
                             question_analysis: Dict[str, Any], 
                             relevant_data: Dict[str, Any],
                             context: Dict[str, Any] = None) -> str:
        """Constrói prompt para análise com IA"""
        
        return f"""
        Você é LucIA, a assistente de segurança e auditoria inteligente do CertGuard AI.
        Analise a seguinte pergunta e forneça uma resposta detalhada e acionável baseada nos dados fornecidos.
        
        PERGUNTA DO USUÁRIO: {question}
        
        ANÁLISE DA PERGUNTA:
        - Tipo: {question_analysis['type']}
        - Padrões identificados: {question_analysis['matched_patterns']}
        - Entidades mencionadas: {question_analysis['entities']}
        - Período temporal: {question_analysis.get('time_period', 'não especificado')} dias
        
        DADOS DISPONÍVEIS:
        - Fontes de dados: {relevant_data.get('sources', [])}
        - Estatísticas gerais: {relevant_data.get('statistics', {})}
        
        DADOS DETALHADOS:
        {json.dumps(relevant_data, indent=2, ensure_ascii=False, default=str)[:5000]}...
        
        INSTRUÇÕES PARA RESPOSTA:
        1. Analise os dados fornecidos em relação à pergunta
        2. Identifique padrões, anomalias ou pontos de interesse
        3. Forneça insights específicos e acionáveis
        4. Se houver problemas de segurança, destaque-os claramente
        5. Sugira ações ou investigações adicionais se necessário
        6. Use dados concretos e específicos na resposta
        7. Seja técnica mas compreensível
        
        FORMATO DA RESPOSTA:
        - Resposta direta à pergunta
        - Análise dos dados relevantes
        - Insights e padrões identificados
        - Recomendações de ação (se aplicável)
        - Alertas de segurança (se houver)
        
        Responda em português brasileiro de forma clara, técnica e profissional.
        Use os dados fornecidos para fundamentar sua análise.
        """
    
    def _process_analysis_response(self, 
                                 response: Dict[str, Any], 
                                 question: str, 
                                 relevant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resposta da IA"""
        
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Extrai métricas da resposta se possível
            metrics = {
                "data_sources_used": len(relevant_data.get("sources", [])),
                "total_records_analyzed": sum([
                    len(relevant_data.get("user_activity", [])),
                    len(relevant_data.get("security_events", [])),
                    len(relevant_data.get("access_logs", []))
                ]),
                "analysis_complexity": len(content.split()),
                "response_timestamp": datetime.now().isoformat()
            }
            
            return {
                "response": content,
                "confidence": 0.85,
                "metrics": metrics,
                "data_summary": relevant_data.get("statistics", {})
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento de resposta: {str(e)}")
            return {
                "response": "Erro no processamento da análise",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _analyze_temporal_patterns(self, df_temporal: pd.DataFrame) -> Dict[str, Any]:
        """Analisa padrões temporais de atividade"""
        
        if df_temporal.empty:
            return {"message": "Nenhum dado temporal disponível"}
        
        # Converte para tipos apropriados
        df_temporal['hour'] = df_temporal['hour'].astype(int)
        df_temporal['day_of_week'] = df_temporal['day_of_week'].astype(int)
        
        # Análise por hora
        hourly_activity = df_temporal.groupby('hour')['activity_count'].sum().to_dict()
        
        # Análise por dia da semana (0=domingo, 6=sábado)
        daily_activity = df_temporal.groupby('day_of_week')['activity_count'].sum().to_dict()
        
        # Detecta horários de pico
        peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Detecta atividade fora do horário comercial
        off_hours_activity = sum([
            hourly_activity.get(hour, 0) 
            for hour in list(range(0, 6)) + list(range(22, 24))
        ])
        
        total_activity = sum(hourly_activity.values())
        off_hours_percentage = (off_hours_activity / total_activity * 100) if total_activity > 0 else 0
        
        return {
            "hourly_distribution": hourly_activity,
            "daily_distribution": daily_activity,
            "peak_hours": peak_hours,
            "off_hours_activity": off_hours_activity,
            "off_hours_percentage": round(off_hours_percentage, 2),
            "total_activity": total_activity
        }
    
    def _analyze_action_patterns(self, df_actions: pd.DataFrame) -> Dict[str, Any]:
        """Analisa padrões de ações dos usuários"""
        
        if df_actions.empty:
            return {"message": "Nenhum dado de ação disponível"}
        
        # Top ações por usuário
        top_actions = df_actions.groupby('action')['count'].sum().sort_values(ascending=False).to_dict()
        
        # Usuários mais ativos
        user_activity = df_actions.groupby('username')['count'].sum().sort_values(ascending=False).to_dict()
        
        # Ações com mais falhas
        actions_with_failures = df_actions[df_actions['failures'] > 0].sort_values('failures', ascending=False)
        
        # Taxa de falha por ação
        failure_rates = {}
        for _, row in df_actions.iterrows():
            if row['count'] > 0:
                failure_rate = (row['failures'] / row['count']) * 100
                if failure_rate > 0:
                    failure_rates[row['action']] = round(failure_rate, 2)
        
        return {
            "top_actions": top_actions,
            "most_active_users": user_activity,
            "actions_with_failures": actions_with_failures.to_dict('records'),
            "failure_rates": failure_rates,
            "total_unique_actions": len(top_actions),
            "total_unique_users": len(user_activity)
        }
    
    def _analyze_ip_patterns(self, df_ips: pd.DataFrame) -> Dict[str, Any]:
        """Analisa padrões de IPs"""
        
        if df_ips.empty:
            return {"message": "Nenhum dado de IP disponível"}
        
        # IPs mais utilizados
        top_ips = df_ips.groupby('ip_address')['usage_count'].sum().sort_values(ascending=False).to_dict()
        
        # IPs com falhas
        ips_with_failures = df_ips[df_ips['failed_attempts'] > 0].sort_values('failed_attempts', ascending=False)
        
        # Usuários com múltiplos IPs
        users_multiple_ips = df_ips.groupby('username')['ip_address'].nunique().sort_values(ascending=False)
        users_multiple_ips = users_multiple_ips[users_multiple_ips > 1].to_dict()
        
        # IPs suspeitos (com alta taxa de falha)
        suspicious_ips = []
        for _, row in df_ips.iterrows():
            if row['usage_count'] > 0:
                failure_rate = (row['failed_attempts'] / row['usage_count']) * 100
                if failure_rate > 50:  # Mais de 50% de falhas
                    suspicious_ips.append({
                        "ip": row['ip_address'],
                        "user": row['username'],
                        "failure_rate": round(failure_rate, 2),
                        "total_attempts": row['usage_count'],
                        "failed_attempts": row['failed_attempts']
                    })
        
        return {
            "top_ips": top_ips,
            "ips_with_failures": ips_with_failures.to_dict('records'),
            "users_multiple_ips": users_multiple_ips,
            "suspicious_ips": suspicious_ips,
            "total_unique_ips": len(top_ips),
            "total_users_analyzed": df_ips['username'].nunique()
        }
    
    async def _detect_behavioral_anomalies(self, 
                                         df_activity: pd.DataFrame,
                                         df_temporal: pd.DataFrame,
                                         df_actions: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detecta anomalias comportamentais"""
        
        anomalies = []
        
        if not df_activity.empty:
            # Detecta usuários com atividade anômala
            if len(df_activity) > 1:
                activity_mean = df_activity['total_activities'].mean()
                activity_std = df_activity['total_activities'].std()
                
                for _, user in df_activity.iterrows():
                    z_score = (user['total_activities'] - activity_mean) / activity_std if activity_std > 0 else 0
                    
                    if abs(z_score) > self.analysis_config["anomaly_threshold"]:
                        anomalies.append({
                            "type": "unusual_activity_volume",
                            "user": user['username'],
                            "description": f"Atividade {z_score:.2f} desvios padrão da média",
                            "severity": "high" if abs(z_score) > 3 else "medium",
                            "details": {
                                "total_activities": user['total_activities'],
                                "mean_activities": round(activity_mean, 2),
                                "z_score": round(z_score, 2)
                            }
                        })
            
            # Detecta usuários com muitos IPs únicos
            for _, user in df_activity.iterrows():
                if user['unique_ips'] > 5:
                    anomalies.append({
                        "type": "multiple_ip_usage",
                        "user": user['username'],
                        "description": f"Usuário utilizou {user['unique_ips']} IPs diferentes",
                        "severity": "medium",
                        "details": {
                            "unique_ips": user['unique_ips'],
                            "total_activities": user['total_activities']
                        }
                    })
        
        return anomalies
    
    def _assess_user_risks(self, 
                          df_activity: pd.DataFrame,
                          df_ips: pd.DataFrame,
                          df_actions: pd.DataFrame) -> Dict[str, Any]:
        """Avalia riscos dos usuários"""
        
        risk_assessment = {}
        
        if not df_activity.empty:
            for _, user in df_activity.iterrows():
                username = user['username']
                risk_score = 0.0
                risk_factors = []
                
                # Fator: Múltiplos IPs
                if user['unique_ips'] > 3:
                    risk_score += 0.3
                    risk_factors.append(f"Múltiplos IPs ({user['unique_ips']})")
                
                # Fator: Tentativas falhadas
                if user['failed_attempts'] > 5:
                    risk_score += 0.4
                    risk_factors.append(f"Múltiplas falhas ({user['failed_attempts']})")
                
                # Fator: Atividade muito alta ou muito baixa
                if len(df_activity) > 1:
                    activity_mean = df_activity['total_activities'].mean()
                    if user['total_activities'] > activity_mean * 3:
                        risk_score += 0.2
                        risk_factors.append("Atividade muito alta")
                    elif user['total_activities'] < activity_mean * 0.1:
                        risk_score += 0.1
                        risk_factors.append("Atividade muito baixa")
                
                # Determina nível de risco
                if risk_score >= 0.7:
                    risk_level = "high"
                elif risk_score >= 0.4:
                    risk_level = "medium"
                else:
                    risk_level = "low"
                
                risk_assessment[username] = {
                    "risk_score": round(risk_score, 2),
                    "risk_level": risk_level,
                    "risk_factors": risk_factors,
                    "total_activities": user['total_activities'],
                    "failed_attempts": user['failed_attempts'],
                    "unique_ips": user['unique_ips']
                }
        
        return risk_assessment

# Instância global do serviço
lucia_db_analyzer = LucIADatabaseAnalyzer()

# Funções de conveniência
async def analyze_user_behavior(user_id: str = None, days: int = 30):
    """Função de conveniência para análise comportamental"""
    return await lucia_db_analyzer.analyze_user_behavior(user_id, days)

async def query_audit_logs(query: str, **filters):
    """Função de conveniência para consulta de logs"""
    return await lucia_db_analyzer.query_audit_logs(query, **filters)

async def answer_security_question(question: str, context: Dict[str, Any] = None):
    """Função de conveniência para perguntas de segurança"""
    return await lucia_db_analyzer.answer_security_question(question, context)

