# Sistema Avançado de Análise de Auditoria e Comportamento - CertGuard AI

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import ipaddress
from collections import defaultdict, Counter
import re
from dataclasses import dataclass
import logging

@dataclass
class SecurityEvent:
    user_id: str
    event_type: str
    ip_address: str
    timestamp: datetime
    details: Dict[str, Any]
    risk_score: float = 0.0
    anomaly_detected: bool = False

@dataclass
class UserBehaviorProfile:
    user_id: str
    typical_login_times: List[int]  # Horas do dia
    typical_locations: List[str]    # IPs/Regiões
    typical_actions: Dict[str, int] # Ações e frequências
    last_updated: datetime
    risk_level: str = "LOW"

class AuditAnalyzer:
    def __init__(self, db_path: str = "certguard_audit.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
        
        # Configurações de detecção de anomalias
        self.anomaly_thresholds = {
            'max_failed_logins': 5,
            'max_login_distance_km': 1000,
            'max_actions_per_hour': 100,
            'suspicious_time_window': 3600,  # 1 hora
            'max_concurrent_sessions': 3
        }
        
        # Padrões suspeitos
        self.suspicious_patterns = {
            'sql_injection': [
                r"(\bunion\b.*\bselect\b)",
                r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
                r"(\bdrop\b.*\btable\b)",
                r"(\binsert\b.*\binto\b)",
                r"(\bdelete\b.*\bfrom\b)"
            ],
            'xss_attempts': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>.*?</iframe>"
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"/etc/passwd",
                r"/windows/system32"
            ]
        }

    def init_database(self):
        """Inicializar banco de dados de auditoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de eventos de segurança
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                details TEXT NOT NULL,
                risk_score REAL DEFAULT 0.0,
                anomaly_detected BOOLEAN DEFAULT FALSE,
                processed BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de perfis comportamentais
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behavior_profiles (
                user_id TEXT PRIMARY KEY,
                typical_login_times TEXT,
                typical_locations TEXT,
                typical_actions TEXT,
                last_updated DATETIME,
                risk_level TEXT DEFAULT 'LOW',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de alertas de segurança
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id TEXT,
                ip_address TEXT,
                description TEXT NOT NULL,
                details TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de sessões ativas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT,
                login_time DATETIME NOT NULL,
                last_activity DATETIME NOT NULL,
                location_info TEXT,
                is_suspicious BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user_time ON security_events(user_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_ip_time ON security_events(ip_address, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON security_events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON active_sessions(user_id)')
        
        conn.commit()
        conn.close()

    def log_security_event(self, event: SecurityEvent) -> int:
        """Registrar evento de segurança"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_events 
            (user_id, event_type, ip_address, timestamp, details, risk_score, anomaly_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.user_id,
            event.event_type,
            event.ip_address,
            event.timestamp,
            json.dumps(event.details),
            event.risk_score,
            event.anomaly_detected
        ))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Analisar evento em tempo real
        self.analyze_event_realtime(event)
        
        return event_id

    def analyze_event_realtime(self, event: SecurityEvent):
        """Análise em tempo real de eventos"""
        anomalies = []
        
        # Verificar padrões suspeitos
        if self.detect_suspicious_patterns(event):
            anomalies.append("Padrão suspeito detectado")
        
        # Verificar comportamento anômalo
        if self.detect_behavioral_anomaly(event):
            anomalies.append("Comportamento anômalo")
        
        # Verificar geolocalização suspeita
        if self.detect_location_anomaly(event):
            anomalies.append("Localização suspeita")
        
        # Verificar tentativas de força bruta
        if self.detect_brute_force(event):
            anomalies.append("Possível ataque de força bruta")
        
        # Verificar sessões concorrentes
        if self.detect_concurrent_sessions(event):
            anomalies.append("Múltiplas sessões simultâneas")
        
        # Gerar alertas se necessário
        if anomalies:
            self.create_security_alert(event, anomalies)

    def detect_suspicious_patterns(self, event: SecurityEvent) -> bool:
        """Detectar padrões suspeitos nos dados do evento"""
        details_str = json.dumps(event.details).lower()
        
        for pattern_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, details_str, re.IGNORECASE):
                    self.logger.warning(f"Padrão suspeito detectado: {pattern_type} - {pattern}")
                    return True
        
        return False

    def detect_behavioral_anomaly(self, event: SecurityEvent) -> bool:
        """Detectar anomalias comportamentais"""
        profile = self.get_user_behavior_profile(event.user_id)
        if not profile:
            return False
        
        current_hour = event.timestamp.hour
        
        # Verificar horário atípico
        if profile.typical_login_times and current_hour not in profile.typical_login_times:
            # Se está fora do horário típico por mais de 3 horas
            min_diff = min(abs(current_hour - h) for h in profile.typical_login_times)
            if min_diff > 3:
                return True
        
        # Verificar ações atípicas
        if event.event_type not in profile.typical_actions:
            return True
        
        return False

    def detect_location_anomaly(self, event: SecurityEvent) -> bool:
        """Detectar anomalias de localização"""
        profile = self.get_user_behavior_profile(event.user_id)
        if not profile or not profile.typical_locations:
            return False
        
        # Verificar se IP está em rede conhecida
        current_ip = ipaddress.ip_address(event.ip_address)
        
        for typical_ip in profile.typical_locations:
            try:
                # Verificar se está na mesma rede /24
                typical_network = ipaddress.ip_network(f"{typical_ip}/24", strict=False)
                if current_ip in typical_network:
                    return False
            except:
                continue
        
        # IP completamente novo - possível anomalia
        return True

    def detect_brute_force(self, event: SecurityEvent) -> bool:
        """Detectar tentativas de força bruta"""
        if event.event_type != 'login_failed':
            return False
        
        # Verificar tentativas falhadas na última hora
        one_hour_ago = event.timestamp - timedelta(hours=1)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM security_events 
            WHERE event_type = 'login_failed' 
            AND ip_address = ? 
            AND timestamp > ?
        ''', (event.ip_address, one_hour_ago))
        
        failed_attempts = cursor.fetchone()[0]
        conn.close()
        
        return failed_attempts >= self.anomaly_thresholds['max_failed_logins']

    def detect_concurrent_sessions(self, event: SecurityEvent) -> bool:
        """Detectar sessões concorrentes suspeitas"""
        if event.event_type != 'login_success':
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM active_sessions 
            WHERE user_id = ? AND last_activity > ?
        ''', (event.user_id, datetime.now() - timedelta(minutes=30)))
        
        active_sessions = cursor.fetchone()[0]
        conn.close()
        
        return active_sessions >= self.anomaly_thresholds['max_concurrent_sessions']

    def create_security_alert(self, event: SecurityEvent, anomalies: List[str]):
        """Criar alerta de segurança"""
        severity = self.calculate_alert_severity(event, anomalies)
        description = f"Anomalias detectadas: {', '.join(anomalies)}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_alerts 
            (alert_type, severity, user_id, ip_address, description, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'BEHAVIORAL_ANOMALY',
            severity,
            event.user_id,
            event.ip_address,
            description,
            json.dumps({
                'event': event.__dict__,
                'anomalies': anomalies,
                'timestamp': event.timestamp.isoformat()
            })
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.warning(f"Alerta de segurança criado: {description}")

    def calculate_alert_severity(self, event: SecurityEvent, anomalies: List[str]) -> str:
        """Calcular severidade do alerta"""
        score = 0
        
        # Pontuação baseada no tipo de evento
        event_scores = {
            'login_failed': 2,
            'unauthorized_access': 5,
            'data_export': 4,
            'admin_action': 3,
            'certificate_download': 2
        }
        
        score += event_scores.get(event.event_type, 1)
        
        # Pontuação baseada nas anomalias
        anomaly_scores = {
            'Padrão suspeito detectado': 5,
            'Comportamento anômalo': 3,
            'Localização suspeita': 4,
            'Possível ataque de força bruta': 5,
            'Múltiplas sessões simultâneas': 3
        }
        
        for anomaly in anomalies:
            score += anomaly_scores.get(anomaly, 2)
        
        # Determinar severidade
        if score >= 10:
            return 'CRITICAL'
        elif score >= 7:
            return 'HIGH'
        elif score >= 4:
            return 'MEDIUM'
        else:
            return 'LOW'

    def update_user_behavior_profile(self, user_id: str):
        """Atualizar perfil comportamental do usuário"""
        # Buscar eventos dos últimos 30 dias
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_type, ip_address, timestamp, details 
            FROM security_events 
            WHERE user_id = ? AND timestamp > ?
            ORDER BY timestamp
        ''', (user_id, thirty_days_ago))
        
        events = cursor.fetchall()
        
        if not events:
            return
        
        # Analisar padrões
        login_times = []
        locations = set()
        actions = Counter()
        
        for event_type, ip_address, timestamp_str, details_str in events:
            timestamp = datetime.fromisoformat(timestamp_str)
            
            if event_type == 'login_success':
                login_times.append(timestamp.hour)
                locations.add(ip_address)
            
            actions[event_type] += 1
        
        # Calcular horários típicos (mais frequentes)
        typical_hours = [hour for hour, count in Counter(login_times).most_common(8)]
        
        # Salvar perfil atualizado
        profile_data = {
            'typical_login_times': typical_hours,
            'typical_locations': list(locations),
            'typical_actions': dict(actions)
        }
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_behavior_profiles 
            (user_id, typical_login_times, typical_locations, typical_actions, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            json.dumps(typical_hours),
            json.dumps(list(locations)),
            json.dumps(dict(actions)),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()

    def get_user_behavior_profile(self, user_id: str) -> Optional[UserBehaviorProfile]:
        """Obter perfil comportamental do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT typical_login_times, typical_locations, typical_actions, 
                   last_updated, risk_level
            FROM user_behavior_profiles 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return UserBehaviorProfile(
            user_id=user_id,
            typical_login_times=json.loads(result[0]) if result[0] else [],
            typical_locations=json.loads(result[1]) if result[1] else [],
            typical_actions=json.loads(result[2]) if result[2] else {},
            last_updated=datetime.fromisoformat(result[3]),
            risk_level=result[4]
        )

    def generate_security_report(self, days: int = 7) -> Dict[str, Any]:
        """Gerar relatório de segurança"""
        start_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estatísticas gerais
        cursor.execute('''
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN anomaly_detected = 1 THEN 1 END) as anomalies,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT ip_address) as unique_ips
            FROM security_events 
            WHERE timestamp > ?
        ''', (start_date,))
        
        stats = cursor.fetchone()
        
        # Eventos por tipo
        cursor.execute('''
            SELECT event_type, COUNT(*) as count
            FROM security_events 
            WHERE timestamp > ?
            GROUP BY event_type
            ORDER BY count DESC
        ''', (start_date,))
        
        events_by_type = dict(cursor.fetchall())
        
        # Top IPs suspeitos
        cursor.execute('''
            SELECT ip_address, COUNT(*) as events, 
                   COUNT(CASE WHEN anomaly_detected = 1 THEN 1 END) as anomalies
            FROM security_events 
            WHERE timestamp > ?
            GROUP BY ip_address
            HAVING anomalies > 0
            ORDER BY anomalies DESC, events DESC
            LIMIT 10
        ''', (start_date,))
        
        suspicious_ips = [
            {
                'ip': row[0],
                'events': row[1],
                'anomalies': row[2]
            }
            for row in cursor.fetchall()
        ]
        
        # Alertas por severidade
        cursor.execute('''
            SELECT severity, COUNT(*) as count
            FROM security_alerts 
            WHERE created_at > ?
            GROUP BY severity
        ''', (start_date,))
        
        alerts_by_severity = dict(cursor.fetchall())
        
        # Usuários com mais anomalias
        cursor.execute('''
            SELECT user_id, COUNT(*) as anomalies
            FROM security_events 
            WHERE timestamp > ? AND anomaly_detected = 1
            GROUP BY user_id
            ORDER BY anomalies DESC
            LIMIT 10
        ''', (start_date,))
        
        users_with_anomalies = [
            {
                'user_id': row[0],
                'anomalies': row[1]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'period': f"Últimos {days} dias",
            'generated_at': datetime.now().isoformat(),
            'statistics': {
                'total_events': stats[0],
                'anomalies_detected': stats[1],
                'unique_users': stats[2],
                'unique_ips': stats[3],
                'anomaly_rate': round((stats[1] / stats[0] * 100) if stats[0] > 0 else 0, 2)
            },
            'events_by_type': events_by_type,
            'suspicious_ips': suspicious_ips,
            'alerts_by_severity': alerts_by_severity,
            'users_with_anomalies': users_with_anomalies
        }

    def get_user_activity_timeline(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Obter timeline de atividades do usuário"""
        start_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_type, ip_address, timestamp, details, risk_score, anomaly_detected
            FROM security_events 
            WHERE user_id = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (user_id, start_date))
        
        events = []
        for row in cursor.fetchall():
            events.append({
                'event_type': row[0],
                'ip_address': row[1],
                'timestamp': row[2],
                'details': json.loads(row[3]),
                'risk_score': row[4],
                'anomaly_detected': bool(row[5])
            })
        
        conn.close()
        return events

    def analyze_ip_behavior(self, ip_address: str, days: int = 7) -> Dict[str, Any]:
        """Analisar comportamento de um IP específico"""
        start_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estatísticas do IP
        cursor.execute('''
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN anomaly_detected = 1 THEN 1 END) as anomalies,
                COUNT(DISTINCT user_id) as unique_users,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen
            FROM security_events 
            WHERE ip_address = ? AND timestamp > ?
        ''', (ip_address, start_date))
        
        stats = cursor.fetchone()
        
        # Eventos por tipo
        cursor.execute('''
            SELECT event_type, COUNT(*) as count
            FROM security_events 
            WHERE ip_address = ? AND timestamp > ?
            GROUP BY event_type
            ORDER BY count DESC
        ''', (ip_address, start_date))
        
        events_by_type = dict(cursor.fetchall())
        
        # Usuários acessados
        cursor.execute('''
            SELECT user_id, COUNT(*) as events
            FROM security_events 
            WHERE ip_address = ? AND timestamp > ?
            GROUP BY user_id
            ORDER BY events DESC
        ''', (ip_address, start_date))
        
        users_accessed = [
            {
                'user_id': row[0],
                'events': row[1]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        # Calcular score de risco
        risk_score = self.calculate_ip_risk_score(ip_address, stats, events_by_type)
        
        return {
            'ip_address': ip_address,
            'analysis_period': f"Últimos {days} dias",
            'statistics': {
                'total_events': stats[0],
                'anomalies': stats[1],
                'unique_users': stats[2],
                'first_seen': stats[3],
                'last_seen': stats[4]
            },
            'events_by_type': events_by_type,
            'users_accessed': users_accessed,
            'risk_score': risk_score,
            'risk_level': self.get_risk_level(risk_score)
        }

    def calculate_ip_risk_score(self, ip_address: str, stats: tuple, events_by_type: Dict[str, int]) -> float:
        """Calcular score de risco para um IP"""
        score = 0.0
        
        # Pontuação baseada em anomalias
        if stats[1] > 0:  # anomalies
            score += (stats[1] / stats[0]) * 50  # % de anomalias * 50
        
        # Pontuação baseada em tipos de eventos suspeitos
        suspicious_events = {
            'login_failed': 5,
            'unauthorized_access': 10,
            'admin_action': 3,
            'data_export': 7
        }
        
        for event_type, count in events_by_type.items():
            if event_type in suspicious_events:
                score += count * suspicious_events[event_type]
        
        # Pontuação baseada em múltiplos usuários
        if stats[2] > 3:  # unique_users
            score += stats[2] * 2
        
        return min(score, 100.0)  # Máximo 100

    def get_risk_level(self, score: float) -> str:
        """Determinar nível de risco baseado no score"""
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        elif score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'

    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obter alertas ativos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, alert_type, severity, user_id, ip_address, 
                   description, details, created_at
            FROM security_alerts 
            WHERE resolved = 0
        '''
        params = []
        
        if severity:
            query += ' AND severity = ?'
            params.append(severity)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'alert_type': row[1],
                'severity': row[2],
                'user_id': row[3],
                'ip_address': row[4],
                'description': row[5],
                'details': json.loads(row[6]) if row[6] else {},
                'created_at': row[7]
            })
        
        conn.close()
        return alerts

    def resolve_alert(self, alert_id: int, resolved_by: str, notes: str = ""):
        """Resolver alerta de segurança"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE security_alerts 
            SET resolved = 1, 
                details = json_set(details, '$.resolved_by', ?, '$.resolved_at', ?, '$.notes', ?)
            WHERE id = ?
        ''', (resolved_by, datetime.now().isoformat(), notes, alert_id))
        
        conn.commit()
        conn.close()

# Exemplo de uso e testes
if __name__ == "__main__":
    analyzer = AuditAnalyzer()
    
    # Simular alguns eventos para teste
    test_events = [
        SecurityEvent(
            user_id="admin",
            event_type="login_success",
            ip_address="192.168.1.100",
            timestamp=datetime.now(),
            details={"user_agent": "Chrome/91.0", "location": "São Paulo"}
        ),
        SecurityEvent(
            user_id="admin",
            event_type="login_failed",
            ip_address="10.0.0.1",
            timestamp=datetime.now(),
            details={"reason": "invalid_password", "attempts": 3}
        ),
        SecurityEvent(
            user_id="user123",
            event_type="certificate_download",
            ip_address="203.0.113.1",
            timestamp=datetime.now(),
            details={"certificate_id": "cert_001", "size": "2.1MB"}
        )
    ]
    
    # Registrar eventos
    for event in test_events:
        analyzer.log_security_event(event)
    
    # Gerar relatório
    report = analyzer.generate_security_report(days=1)
    print("Relatório de Segurança:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

