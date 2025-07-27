"""
CertGuard AI - LucIA Security Intelligence
Sistema de IA para análise comportamental, detecção de anomalias e monitoramento de segurança
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import hashlib
import ipaddress
from dataclasses import dataclass
from collections import defaultdict, Counter
import re
import geoip2.database
import geoip2.errors

from .nvidia_ai import nvidia_ai_service
from .blockchain_audit import blockchain_audit_service, record_audit

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Evento de segurança detectado"""
    id: str
    timestamp: str
    event_type: str
    severity: str  # low, medium, high, critical
    user_id: str
    ip_address: str
    user_agent: str
    description: str
    details: Dict[str, Any]
    risk_score: float
    location: Optional[Dict[str, str]] = None
    recommendations: List[str] = None

@dataclass
class UserBehaviorProfile:
    """Perfil comportamental do usuário"""
    user_id: str
    usual_ips: List[str]
    usual_locations: List[str]
    usual_hours: List[int]
    usual_devices: List[str]
    login_frequency: float
    average_session_duration: float
    common_actions: Dict[str, int]
    risk_level: str
    last_updated: str

class LucIASecurityAI:
    """Sistema principal de IA de segurança LucIA"""
    
    def __init__(self):
        # Configurações de detecção
        self.anomaly_thresholds = {
            "new_ip_risk": 0.7,
            "unusual_time_risk": 0.6,
            "new_location_risk": 0.8,
            "multiple_failed_logins": 5,
            "session_duration_anomaly": 3.0,  # desvios padrão
            "unusual_activity_volume": 2.5
        }
        
        # Base de conhecimento de ameaças
        self.threat_intelligence = {
            "known_malicious_ips": set(),
            "suspicious_user_agents": [
                "sqlmap", "nikto", "nmap", "masscan", "zap",
                "burp", "w3af", "skipfish", "dirb", "gobuster"
            ],
            "blocked_countries": ["CN", "RU", "KP"],  # Configurável
            "vpn_indicators": [
                "vpn", "proxy", "tor", "tunnel", "anonymous"
            ]
        }
        
        # Perfis comportamentais dos usuários
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}
        
        # Cache de eventos recentes
        self.recent_events: List[SecurityEvent] = []
        self.max_recent_events = 1000
        
        # Estatísticas de segurança
        self.security_stats = {
            "total_events": 0,
            "critical_events": 0,
            "blocked_attempts": 0,
            "anomalies_detected": 0,
            "users_monitored": 0,
            "last_threat_update": None
        }
        
        # Configuração de geolocalização (simulada)
        self.geoip_enabled = False
        
    async def analyze_login_attempt(self, 
                                  user_id: str,
                                  ip_address: str,
                                  user_agent: str,
                                  success: bool,
                                  session_id: str = None) -> Dict[str, Any]:
        """Analisa tentativa de login e detecta anomalias"""
        
        timestamp = datetime.now().isoformat()
        risk_factors = []
        risk_score = 0.0
        
        # Análise de IP
        ip_analysis = await self._analyze_ip_address(user_id, ip_address)
        risk_score += ip_analysis["risk_score"]
        risk_factors.extend(ip_analysis["factors"])
        
        # Análise de User Agent
        ua_analysis = self._analyze_user_agent(user_agent)
        risk_score += ua_analysis["risk_score"]
        risk_factors.extend(ua_analysis["factors"])
        
        # Análise temporal
        time_analysis = await self._analyze_access_time(user_id, timestamp)
        risk_score += time_analysis["risk_score"]
        risk_factors.extend(time_analysis["factors"])
        
        # Análise de padrão de login
        pattern_analysis = await self._analyze_login_pattern(user_id, success, ip_address)
        risk_score += pattern_analysis["risk_score"]
        risk_factors.extend(pattern_analysis["factors"])
        
        # Determina severidade
        severity = self._calculate_severity(risk_score)
        
        # Cria evento de segurança
        event = SecurityEvent(
            id=hashlib.sha256(f"{user_id}{ip_address}{timestamp}".encode()).hexdigest()[:16],
            timestamp=timestamp,
            event_type="login_attempt",
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"{'Successful' if success else 'Failed'} login attempt with risk score {risk_score:.2f}",
            details={
                "success": success,
                "risk_factors": risk_factors,
                "session_id": session_id,
                "ip_analysis": ip_analysis,
                "ua_analysis": ua_analysis,
                "time_analysis": time_analysis,
                "pattern_analysis": pattern_analysis
            },
            risk_score=risk_score,
            location=ip_analysis.get("location"),
            recommendations=self._generate_recommendations(risk_factors, risk_score)
        )
        
        # Registra evento
        await self._record_security_event(event)
        
        # Atualiza perfil do usuário se login bem-sucedido
        if success:
            await self._update_user_profile(user_id, ip_address, user_agent, timestamp)
        
        return {
            "event_id": event.id,
            "risk_score": risk_score,
            "severity": severity,
            "risk_factors": risk_factors,
            "recommendations": event.recommendations,
            "should_block": risk_score > 0.8,
            "requires_mfa": risk_score > 0.5,
            "location": event.location
        }
    
    async def analyze_user_activity(self,
                                  user_id: str,
                                  action: str,
                                  resource_type: str,
                                  resource_id: str,
                                  ip_address: str,
                                  user_agent: str,
                                  session_id: str = None) -> Dict[str, Any]:
        """Analisa atividade do usuário e detecta comportamento anômalo"""
        
        timestamp = datetime.now().isoformat()
        risk_factors = []
        risk_score = 0.0
        
        # Análise de volume de atividade
        volume_analysis = await self._analyze_activity_volume(user_id, action)
        risk_score += volume_analysis["risk_score"]
        risk_factors.extend(volume_analysis["factors"])
        
        # Análise de padrão de acesso
        access_analysis = await self._analyze_access_pattern(user_id, resource_type, resource_id)
        risk_score += access_analysis["risk_score"]
        risk_factors.extend(access_analysis["factors"])
        
        # Análise de contexto de sessão
        session_analysis = await self._analyze_session_context(user_id, session_id, ip_address)
        risk_score += session_analysis["risk_score"]
        risk_factors.extend(session_analysis["factors"])
        
        # Determina severidade
        severity = self._calculate_severity(risk_score)
        
        # Cria evento de segurança
        event = SecurityEvent(
            id=hashlib.sha256(f"{user_id}{action}{timestamp}".encode()).hexdigest()[:16],
            timestamp=timestamp,
            event_type="user_activity",
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"User activity: {action} on {resource_type} with risk score {risk_score:.2f}",
            details={
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "session_id": session_id,
                "risk_factors": risk_factors,
                "volume_analysis": volume_analysis,
                "access_analysis": access_analysis,
                "session_analysis": session_analysis
            },
            risk_score=risk_score,
            recommendations=self._generate_recommendations(risk_factors, risk_score)
        )
        
        # Registra evento
        await self._record_security_event(event)
        
        return {
            "event_id": event.id,
            "risk_score": risk_score,
            "severity": severity,
            "risk_factors": risk_factors,
            "recommendations": event.recommendations,
            "should_alert": risk_score > 0.6
        }
    
    async def get_security_insights(self, query: str, user_id: str = None) -> Dict[str, Any]:
        """Responde perguntas sobre segurança usando IA"""
        
        # Coleta dados relevantes
        context_data = await self._gather_security_context(query, user_id)
        
        # Constrói prompt para IA
        prompt = self._build_security_query_prompt(query, context_data)
        
        try:
            # Usa NVIDIA AI para análise
            response = await nvidia_ai_service._make_api_request(prompt, context="security_analysis")
            
            # Processa resposta
            analysis = self._process_security_response(response, query, context_data)
            
            # Registra consulta
            await record_audit(
                user_id=user_id or "system",
                action="security_query",
                resource_type="security_analysis",
                resource_id=f"query_{datetime.now().timestamp()}",
                details={
                    "query": query,
                    "context_size": len(str(context_data)),
                    "response_confidence": analysis.get("confidence", 0.0)
                }
            )
            
            return {
                "success": True,
                "query": query,
                "analysis": analysis,
                "context_data": context_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de segurança: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def detect_anomalies(self, time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """Detecta anomalias no período especificado"""
        
        start_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Coleta eventos recentes
        recent_events = [
            event for event in self.recent_events
            if datetime.fromisoformat(event.timestamp) >= start_time
        ]
        
        anomalies = []
        
        # Análise de padrões anômalos
        
        # 1. Múltiplos logins falhados
        failed_logins = defaultdict(list)
        for event in recent_events:
            if event.event_type == "login_attempt" and not event.details.get("success"):
                failed_logins[event.user_id].append(event)
        
        for user_id, events in failed_logins.items():
            if len(events) >= self.anomaly_thresholds["multiple_failed_logins"]:
                anomalies.append({
                    "type": "multiple_failed_logins",
                    "user_id": user_id,
                    "count": len(events),
                    "severity": "high",
                    "description": f"Usuário {user_id} teve {len(events)} tentativas de login falhadas",
                    "events": [e.id for e in events]
                })
        
        # 2. Acessos de IPs suspeitos
        suspicious_ips = defaultdict(list)
        for event in recent_events:
            if event.risk_score > 0.7:
                suspicious_ips[event.ip_address].append(event)
        
        for ip, events in suspicious_ips.items():
            if len(events) > 1:
                anomalies.append({
                    "type": "suspicious_ip_activity",
                    "ip_address": ip,
                    "count": len(events),
                    "severity": "medium",
                    "description": f"IP {ip} teve {len(events)} atividades suspeitas",
                    "events": [e.id for e in events]
                })
        
        # 3. Atividade fora do horário normal
        unusual_time_events = [
            event for event in recent_events
            if "unusual_time" in event.details.get("risk_factors", [])
        ]
        
        if len(unusual_time_events) > 5:
            anomalies.append({
                "type": "unusual_time_activity",
                "count": len(unusual_time_events),
                "severity": "medium",
                "description": f"{len(unusual_time_events)} atividades fora do horário normal",
                "events": [e.id for e in unusual_time_events]
            })
        
        return anomalies
    
    async def generate_security_report(self, 
                                     start_date: str,
                                     end_date: str,
                                     user_id: str = None) -> Dict[str, Any]:
        """Gera relatório de segurança detalhado"""
        
        # Coleta eventos do período
        events = [
            event for event in self.recent_events
            if start_date <= event.timestamp <= end_date
        ]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        # Análise estatística
        total_events = len(events)
        critical_events = len([e for e in events if e.severity == "critical"])
        high_risk_events = len([e for e in events if e.severity == "high"])
        
        # Análise por tipo de evento
        event_types = Counter(e.event_type for e in events)
        
        # Análise por usuário
        user_activity = defaultdict(int)
        for event in events:
            user_activity[event.user_id] += 1
        
        # Top IPs suspeitos
        ip_risks = defaultdict(list)
        for event in events:
            ip_risks[event.ip_address].append(event.risk_score)
        
        top_risky_ips = sorted(
            [(ip, sum(scores)/len(scores), len(scores)) for ip, scores in ip_risks.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Detecta anomalias no período
        period_anomalies = await self.detect_anomalies(
            time_window_hours=int((datetime.fromisoformat(end_date) - 
                                 datetime.fromisoformat(start_date)).total_seconds() / 3600)
        )
        
        # Gera insights com IA
        insights_prompt = f"""
        Analise o seguinte relatório de segurança e forneça insights:
        
        Período: {start_date} a {end_date}
        Total de eventos: {total_events}
        Eventos críticos: {critical_events}
        Eventos de alto risco: {high_risk_events}
        
        Tipos de eventos: {dict(event_types)}
        Atividade por usuário: {dict(user_activity)}
        Top IPs suspeitos: {top_risky_ips[:5]}
        Anomalias detectadas: {len(period_anomalies)}
        
        Forneça:
        1. Resumo executivo da situação de segurança
        2. Principais riscos identificados
        3. Recomendações de ação
        4. Tendências observadas
        """
        
        try:
            ai_response = await nvidia_ai_service._make_api_request(
                insights_prompt, context="security_report"
            )
            ai_insights = ai_response["choices"][0]["message"]["content"]
        except Exception as e:
            ai_insights = f"Erro na geração de insights: {str(e)}"
        
        return {
            "report_period": {
                "start_date": start_date,
                "end_date": end_date,
                "user_filter": user_id
            },
            "summary": {
                "total_events": total_events,
                "critical_events": critical_events,
                "high_risk_events": high_risk_events,
                "anomalies_detected": len(period_anomalies)
            },
            "analysis": {
                "event_types": dict(event_types),
                "user_activity": dict(user_activity),
                "top_risky_ips": top_risky_ips,
                "anomalies": period_anomalies
            },
            "ai_insights": ai_insights,
            "recommendations": self._generate_security_recommendations(events),
            "generated_at": datetime.now().isoformat()
        }
    
    async def _analyze_ip_address(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """Analisa endereço IP para detectar riscos"""
        
        risk_score = 0.0
        factors = []
        location = None
        
        # Verifica se é IP conhecido do usuário
        user_profile = self.user_profiles.get(user_id)
        if user_profile and ip_address not in user_profile.usual_ips:
            risk_score += 0.3
            factors.append("new_ip")
        
        # Verifica lista de IPs maliciosos
        if ip_address in self.threat_intelligence["known_malicious_ips"]:
            risk_score += 0.9
            factors.append("known_malicious_ip")
        
        # Análise de geolocalização (simulada)
        try:
            # Simula análise de geolocalização
            if ip_address.startswith("192.168.") or ip_address.startswith("10."):
                location = {"country": "BR", "city": "Local", "region": "LAN"}
            else:
                # Simula diferentes localizações baseado no IP
                ip_hash = hash(ip_address) % 10
                locations = [
                    {"country": "BR", "city": "São Paulo", "region": "SP"},
                    {"country": "BR", "city": "Rio de Janeiro", "region": "RJ"},
                    {"country": "US", "city": "New York", "region": "NY"},
                    {"country": "CN", "city": "Beijing", "region": "BJ"},
                    {"country": "RU", "city": "Moscow", "region": "MOW"},
                ]
                location = locations[ip_hash % len(locations)]
            
            # Verifica países bloqueados
            if location["country"] in self.threat_intelligence["blocked_countries"]:
                risk_score += 0.8
                factors.append("blocked_country")
            
            # Verifica se é nova localização para o usuário
            if user_profile and location["country"] not in [
                loc.split(",")[0] for loc in user_profile.usual_locations
            ]:
                risk_score += 0.4
                factors.append("new_location")
                
        except Exception as e:
            logger.warning(f"Erro na análise de geolocalização: {str(e)}")
        
        return {
            "risk_score": min(risk_score, 1.0),
            "factors": factors,
            "location": location,
            "is_new_ip": "new_ip" in factors,
            "is_malicious": "known_malicious_ip" in factors
        }
    
    def _analyze_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """Analisa User Agent para detectar ferramentas suspeitas"""
        
        risk_score = 0.0
        factors = []
        
        user_agent_lower = user_agent.lower()
        
        # Verifica ferramentas de hacking conhecidas
        for suspicious_tool in self.threat_intelligence["suspicious_user_agents"]:
            if suspicious_tool in user_agent_lower:
                risk_score += 0.8
                factors.append(f"suspicious_tool_{suspicious_tool}")
        
        # Verifica indicadores de VPN/Proxy
        for vpn_indicator in self.threat_intelligence["vpn_indicators"]:
            if vpn_indicator in user_agent_lower:
                risk_score += 0.3
                factors.append("vpn_indicator")
        
        # Verifica User Agent muito curto ou suspeito
        if len(user_agent) < 10:
            risk_score += 0.2
            factors.append("short_user_agent")
        
        # Verifica User Agent comum de bots
        bot_indicators = ["bot", "crawler", "spider", "scraper"]
        for bot_indicator in bot_indicators:
            if bot_indicator in user_agent_lower:
                risk_score += 0.4
                factors.append("bot_indicator")
        
        return {
            "risk_score": min(risk_score, 1.0),
            "factors": factors,
            "user_agent": user_agent
        }
    
    async def _analyze_access_time(self, user_id: str, timestamp: str) -> Dict[str, Any]:
        """Analisa horário de acesso para detectar padrões anômalos"""
        
        risk_score = 0.0
        factors = []
        
        access_time = datetime.fromisoformat(timestamp)
        hour = access_time.hour
        
        # Verifica perfil do usuário
        user_profile = self.user_profiles.get(user_id)
        if user_profile:
            # Verifica se está fora do horário usual
            if hour not in user_profile.usual_hours:
                risk_score += 0.3
                factors.append("unusual_time")
        else:
            # Para usuários sem perfil, considera horário comercial como normal
            if hour < 6 or hour > 22:
                risk_score += 0.2
                factors.append("outside_business_hours")
        
        # Verifica horários de alto risco (madrugada)
        if 2 <= hour <= 5:
            risk_score += 0.4
            factors.append("high_risk_hours")
        
        return {
            "risk_score": min(risk_score, 1.0),
            "factors": factors,
            "access_hour": hour,
            "access_time": timestamp
        }
    
    async def _analyze_login_pattern(self, 
                                   user_id: str, 
                                   success: bool, 
                                   ip_address: str) -> Dict[str, Any]:
        """Analisa padrão de login para detectar ataques"""
        
        risk_score = 0.0
        factors = []
        
        # Conta tentativas recentes do usuário
        recent_attempts = [
            event for event in self.recent_events[-100:]  # Últimos 100 eventos
            if (event.user_id == user_id and 
                event.event_type == "login_attempt" and
                (datetime.now() - datetime.fromisoformat(event.timestamp)).total_seconds() < 3600)
        ]
        
        failed_attempts = [e for e in recent_attempts if not e.details.get("success")]
        
        # Verifica múltiplas tentativas falhadas
        if len(failed_attempts) >= 3:
            risk_score += 0.5
            factors.append("multiple_failed_attempts")
        
        if len(failed_attempts) >= 5:
            risk_score += 0.3
            factors.append("brute_force_pattern")
        
        # Verifica tentativas de múltiplos IPs
        recent_ips = set(e.ip_address for e in recent_attempts)
        if len(recent_ips) > 3:
            risk_score += 0.4
            factors.append("multiple_ip_attempts")
        
        # Verifica velocidade de tentativas
        if len(recent_attempts) > 10:
            time_span = (
                datetime.fromisoformat(recent_attempts[0].timestamp) -
                datetime.fromisoformat(recent_attempts[-1].timestamp)
            ).total_seconds()
            
            if time_span < 300:  # Menos de 5 minutos
                risk_score += 0.6
                factors.append("rapid_attempts")
        
        return {
            "risk_score": min(risk_score, 1.0),
            "factors": factors,
            "recent_attempts": len(recent_attempts),
            "failed_attempts": len(failed_attempts),
            "unique_ips": len(recent_ips)
        }
    
    async def _analyze_activity_volume(self, user_id: str, action: str) -> Dict[str, Any]:
        """Analisa volume de atividade para detectar comportamento anômalo"""
        
        risk_score = 0.0
        factors = []
        
        # Conta atividades recentes do usuário
        recent_activities = [
            event for event in self.recent_events[-200:]
            if (event.user_id == user_id and
                (datetime.now() - datetime.fromisoformat(event.timestamp)).total_seconds() < 3600)
        ]
        
        # Verifica volume anômalo
        if len(recent_activities) > 50:
            risk_score += 0.4
            factors.append("high_activity_volume")
        
        # Verifica ações repetitivas
        action_count = len([e for e in recent_activities if e.details.get("action") == action])
        if action_count > 20:
            risk_score += 0.3
            factors.append("repetitive_action")
        
        return {
            "risk_score": min(risk_score, 1.0),
            "factors": factors,
            "recent_activities": len(recent_activities),
            "action_count": action_count
        }
    
    async def _analyze_access_pattern(self, 
                                    user_id: str, 
                                    resource_type: str, 
                                    resource_id: str) -> Dict[str, Any]:
        """Analisa padrão de acesso a recursos"""
        
        risk_score = 0.0
        factors = []
        
        # Verifica acessos recentes ao mesmo recurso
        recent_access = [
            event for event in self.recent_events[-100:]
            if (event.user_id == user_id and
                event.details.get("resource_type") == resource_type and
                event.details.get("resource_id") == resource_id and
                (datetime.now() - datetime.fromisoformat(event.timestamp)).total_seconds() < 1800)
        ]
        
        if len(recent_access) > 10:
            risk_score += 0.3
            factors.append("excessive_resource_access")
        
        # Verifica acesso a recursos sensíveis
        sensitive_resources = ["certificate", "user", "organization"]
        if resource_type in sensitive_resources:
            risk_score += 0.1
            factors.append("sensitive_resource_access")
        
        return {
            "risk_score": min(risk_score, 1.0),
            "factors": factors,
            "recent_access_count": len(recent_access)
        }
    
    async def _analyze_session_context(self, 
                                     user_id: str, 
                                     session_id: str, 
                                     ip_address: str) -> Dict[str, Any]:
        """Analisa contexto da sessão"""
        
        risk_score = 0.0
        factors = []
        
        if session_id:
            # Verifica atividades da sessão
            session_events = [
                event for event in self.recent_events[-50:]
                if event.details.get("session_id") == session_id
            ]
            
            # Verifica mudança de IP na sessão
            session_ips = set(e.ip_address for e in session_events)
            if len(session_ips) > 1:
                risk_score += 0.7
                factors.append("ip_change_in_session")
            
            # Verifica duração da sessão
            if len(session_events) > 0:
                session_start = min(datetime.fromisoformat(e.timestamp) for e in session_events)
                session_duration = (datetime.now() - session_start).total_seconds()
                
                if session_duration > 28800:  # Mais de 8 horas
                    risk_score += 0.2
                    factors.append("long_session")
        
        return {
            "risk_score": min(risk_score, 1.0),
            "factors": factors,
            "session_id": session_id
        }
    
    def _calculate_severity(self, risk_score: float) -> str:
        """Calcula severidade baseada no score de risco"""
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, risk_factors: List[str], risk_score: float) -> List[str]:
        """Gera recomendações baseadas nos fatores de risco"""
        
        recommendations = []
        
        if "new_ip" in risk_factors:
            recommendations.append("Verificar se o acesso é legítimo do novo IP")
        
        if "new_location" in risk_factors:
            recommendations.append("Confirmar localização do usuário")
        
        if "multiple_failed_attempts" in risk_factors:
            recommendations.append("Considerar bloqueio temporário da conta")
        
        if "suspicious_tool" in str(risk_factors):
            recommendations.append("Bloquear acesso imediatamente - ferramenta de hacking detectada")
        
        if "blocked_country" in risk_factors:
            recommendations.append("Bloquear acesso de país restrito")
        
        if risk_score > 0.8:
            recommendations.append("AÇÃO IMEDIATA: Investigar e possivelmente bloquear acesso")
        elif risk_score > 0.5:
            recommendations.append("Solicitar autenticação adicional (MFA)")
        
        if "brute_force_pattern" in risk_factors:
            recommendations.append("Implementar CAPTCHA ou delay progressivo")
        
        return recommendations
    
    async def _record_security_event(self, event: SecurityEvent):
        """Registra evento de segurança"""
        
        # Adiciona à lista de eventos recentes
        self.recent_events.append(event)
        
        # Mantém apenas os eventos mais recentes
        if len(self.recent_events) > self.max_recent_events:
            self.recent_events = self.recent_events[-self.max_recent_events:]
        
        # Atualiza estatísticas
        self.security_stats["total_events"] += 1
        if event.severity == "critical":
            self.security_stats["critical_events"] += 1
        
        # Registra na blockchain
        await record_audit(
            user_id=event.user_id,
            action="security_event",
            resource_type="security",
            resource_id=event.id,
            details={
                "event_type": event.event_type,
                "severity": event.severity,
                "risk_score": event.risk_score,
                "risk_factors": event.details.get("risk_factors", []),
                "description": event.description
            },
            ip_address=event.ip_address,
            user_agent=event.user_agent
        )
        
        logger.info(f"Evento de segurança registrado: {event.id} - {event.severity}")
    
    async def _update_user_profile(self, 
                                 user_id: str, 
                                 ip_address: str, 
                                 user_agent: str, 
                                 timestamp: str):
        """Atualiza perfil comportamental do usuário"""
        
        access_time = datetime.fromisoformat(timestamp)
        
        if user_id not in self.user_profiles:
            # Cria novo perfil
            self.user_profiles[user_id] = UserBehaviorProfile(
                user_id=user_id,
                usual_ips=[ip_address],
                usual_locations=[],
                usual_hours=[access_time.hour],
                usual_devices=[user_agent[:50]],
                login_frequency=1.0,
                average_session_duration=0.0,
                common_actions={},
                risk_level="low",
                last_updated=timestamp
            )
        else:
            # Atualiza perfil existente
            profile = self.user_profiles[user_id]
            
            # Atualiza IPs usuais (mantém últimos 10)
            if ip_address not in profile.usual_ips:
                profile.usual_ips.append(ip_address)
                profile.usual_ips = profile.usual_ips[-10:]
            
            # Atualiza horários usuais
            if access_time.hour not in profile.usual_hours:
                profile.usual_hours.append(access_time.hour)
                profile.usual_hours = list(set(profile.usual_hours))
            
            # Atualiza dispositivos usuais
            device_signature = user_agent[:50]
            if device_signature not in profile.usual_devices:
                profile.usual_devices.append(device_signature)
                profile.usual_devices = profile.usual_devices[-5:]
            
            profile.last_updated = timestamp
        
        self.security_stats["users_monitored"] = len(self.user_profiles)
    
    async def _gather_security_context(self, query: str, user_id: str = None) -> Dict[str, Any]:
        """Coleta dados de contexto para análise de segurança"""
        
        context = {
            "recent_events": [],
            "user_profiles": {},
            "security_stats": self.security_stats.copy(),
            "threat_intelligence": {
                "known_threats": len(self.threat_intelligence["known_malicious_ips"]),
                "blocked_countries": self.threat_intelligence["blocked_countries"]
            }
        }
        
        # Adiciona eventos recentes relevantes
        if user_id:
            user_events = [
                {
                    "timestamp": e.timestamp,
                    "event_type": e.event_type,
                    "severity": e.severity,
                    "risk_score": e.risk_score,
                    "description": e.description
                }
                for e in self.recent_events[-20:]
                if e.user_id == user_id
            ]
            context["recent_events"] = user_events
            
            # Adiciona perfil do usuário
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                context["user_profiles"][user_id] = {
                    "usual_ips_count": len(profile.usual_ips),
                    "usual_hours": profile.usual_hours,
                    "risk_level": profile.risk_level,
                    "last_updated": profile.last_updated
                }
        else:
            # Adiciona eventos gerais recentes
            context["recent_events"] = [
                {
                    "timestamp": e.timestamp,
                    "event_type": e.event_type,
                    "severity": e.severity,
                    "risk_score": e.risk_score,
                    "user_id": e.user_id,
                    "description": e.description
                }
                for e in self.recent_events[-50:]
            ]
        
        return context
    
    def _build_security_query_prompt(self, query: str, context_data: Dict[str, Any]) -> str:
        """Constrói prompt para consulta de segurança"""
        
        return f"""
        Você é LucIA, a assistente de segurança inteligente do CertGuard AI.
        Analise a seguinte consulta de segurança e forneça uma resposta detalhada e acionável.
        
        CONSULTA: {query}
        
        CONTEXTO DE SEGURANÇA:
        - Eventos recentes: {len(context_data.get('recent_events', []))} eventos
        - Estatísticas: {context_data.get('security_stats', {})}
        - Inteligência de ameaças: {context_data.get('threat_intelligence', {})}
        - Perfis de usuário: {len(context_data.get('user_profiles', {}))} usuários monitorados
        
        EVENTOS RECENTES RELEVANTES:
        {json.dumps(context_data.get('recent_events', [])[:10], indent=2, ensure_ascii=False)}
        
        Forneça uma resposta que inclua:
        1. Análise da situação atual
        2. Identificação de riscos ou ameaças
        3. Recomendações específicas de ação
        4. Contexto histórico relevante
        5. Próximos passos sugeridos
        
        Seja específica, técnica e focada em segurança. Use dados concretos do contexto fornecido.
        Responda em português brasileiro de forma clara e profissional.
        """
    
    def _process_security_response(self, 
                                 response: Dict[str, Any], 
                                 query: str, 
                                 context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resposta da IA para consulta de segurança"""
        
        try:
            content = response["choices"][0]["message"]["content"]
            
            return {
                "response": content,
                "confidence": 0.85,
                "query": query,
                "context_events": len(context_data.get("recent_events", [])),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento de resposta: {str(e)}")
            return {
                "response": "Erro no processamento da consulta de segurança",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _generate_security_recommendations(self, events: List[SecurityEvent]) -> List[str]:
        """Gera recomendações de segurança baseadas nos eventos"""
        
        recommendations = []
        
        # Análise de padrões
        high_risk_events = [e for e in events if e.severity in ["high", "critical"]]
        
        if len(high_risk_events) > 0:
            recommendations.append(
                f"ATENÇÃO: {len(high_risk_events)} eventos de alto risco detectados - revisar imediatamente"
            )
        
        # Análise de IPs
        unique_ips = set(e.ip_address for e in events)
        if len(unique_ips) > 20:
            recommendations.append(
                "Grande número de IPs únicos detectados - considerar implementar geo-blocking"
            )
        
        # Análise de usuários
        user_events = defaultdict(int)
        for event in events:
            user_events[event.user_id] += 1
        
        high_activity_users = [user for user, count in user_events.items() if count > 50]
        if high_activity_users:
            recommendations.append(
                f"Usuários com alta atividade detectados: {', '.join(high_activity_users[:5])}"
            )
        
        return recommendations

# Instância global do serviço
lucia_security_ai = LucIASecurityAI()

# Funções de conveniência
async def analyze_login(user_id: str, ip_address: str, user_agent: str, 
                       success: bool, session_id: str = None):
    """Função de conveniência para análise de login"""
    return await lucia_security_ai.analyze_login_attempt(
        user_id, ip_address, user_agent, success, session_id
    )

async def analyze_activity(user_id: str, action: str, resource_type: str,
                          resource_id: str, ip_address: str, user_agent: str,
                          session_id: str = None):
    """Função de conveniência para análise de atividade"""
    return await lucia_security_ai.analyze_user_activity(
        user_id, action, resource_type, resource_id, ip_address, user_agent, session_id
    )

async def get_security_insights(query: str, user_id: str = None):
    """Função de conveniência para insights de segurança"""
    return await lucia_security_ai.get_security_insights(query, user_id)

async def detect_anomalies(hours: int = 24):
    """Função de conveniência para detecção de anomalias"""
    return await lucia_security_ai.detect_anomalies(hours)

async def generate_security_report(start_date: str, end_date: str, user_id: str = None):
    """Função de conveniência para relatório de segurança"""
    return await lucia_security_ai.generate_security_report(start_date, end_date, user_id)

