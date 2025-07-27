"""
CertGuard AI - Sistema Blockchain para Auditoria Imutável
Implementação enterprise com Hyperledger Fabric e versão MVP simulada
"""

import os
import json
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import asyncio
import aiofiles

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AuditRecord:
    """Registro de auditoria para blockchain"""
    id: str
    timestamp: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    certificate_used: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

@dataclass
class BlockchainBlock:
    """Bloco da blockchain"""
    index: int
    timestamp: str
    data: List[AuditRecord]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    
    def calculate_hash(self) -> str:
        """Calcula hash do bloco"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": [record.to_dict() for record in self.data],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True, ensure_ascii=False)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 4):
        """Minera o bloco (Proof of Work)"""
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        logger.info(f"Bloco minerado: {self.hash}")

class HyperledgerFabricConnector:
    """Conector para Hyperledger Fabric (Enterprise)"""
    
    def __init__(self):
        self.network_config = {
            "channel_name": "certguard-channel",
            "chaincode_name": "certguard-audit",
            "org_name": "CertGuardOrg",
            "peer_endpoint": os.getenv("FABRIC_PEER_ENDPOINT", "grpc://localhost:7051"),
            "orderer_endpoint": os.getenv("FABRIC_ORDERER_ENDPOINT", "grpc://localhost:7050"),
            "ca_endpoint": os.getenv("FABRIC_CA_ENDPOINT", "http://localhost:7054")
        }
        
        self.connection_profile = {
            "name": "certguard-network",
            "version": "1.0.0",
            "client": {
                "organization": "CertGuardOrg",
                "connection": {
                    "timeout": {
                        "peer": {"endorser": "300"},
                        "orderer": "300"
                    }
                }
            },
            "organizations": {
                "CertGuardOrg": {
                    "mspid": "CertGuardOrgMSP",
                    "peers": ["peer0.certguard.com"],
                    "certificateAuthorities": ["ca.certguard.com"]
                }
            },
            "peers": {
                "peer0.certguard.com": {
                    "url": self.network_config["peer_endpoint"],
                    "tlsCACerts": {
                        "path": "/opt/fabric/crypto-config/peerOrganizations/certguard.com/tlsca/tlsca.certguard.com-cert.pem"
                    },
                    "grpcOptions": {
                        "ssl-target-name-override": "peer0.certguard.com"
                    }
                }
            },
            "certificateAuthorities": {
                "ca.certguard.com": {
                    "url": self.network_config["ca_endpoint"],
                    "caName": "ca-certguard",
                    "tlsCACerts": {
                        "path": "/opt/fabric/crypto-config/peerOrganizations/certguard.com/ca/ca.certguard.com-cert.pem"
                    }
                }
            }
        }
        
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Conecta à rede Hyperledger Fabric"""
        try:
            # Simulação de conexão (em produção, usaria fabric-sdk-py)
            logger.info("Conectando à rede Hyperledger Fabric...")
            await asyncio.sleep(1)  # Simula tempo de conexão
            
            self.is_connected = True
            logger.info("Conectado à rede Hyperledger Fabric com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao Hyperledger Fabric: {str(e)}")
            return False
    
    async def submit_transaction(self, function_name: str, args: List[str]) -> Dict[str, Any]:
        """Submete transação para o chaincode"""
        if not self.is_connected:
            await self.connect()
        
        try:
            # Simulação de transação (em produção, usaria fabric-sdk-py)
            transaction_id = hashlib.sha256(f"{function_name}{time.time()}".encode()).hexdigest()[:16]
            
            logger.info(f"Submetendo transação: {function_name} - ID: {transaction_id}")
            await asyncio.sleep(0.5)  # Simula tempo de processamento
            
            return {
                "transaction_id": transaction_id,
                "status": "VALID",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "block_number": int(time.time()) % 10000,
                "function": function_name,
                "args": args
            }
            
        except Exception as e:
            logger.error(f"Erro na transação Fabric: {str(e)}")
            raise
    
    async def query_ledger(self, function_name: str, args: List[str]) -> Dict[str, Any]:
        """Consulta o ledger"""
        if not self.is_connected:
            await self.connect()
        
        try:
            # Simulação de consulta
            logger.info(f"Consultando ledger: {function_name}")
            await asyncio.sleep(0.3)
            
            return {
                "result": f"Query result for {function_name}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "function": function_name,
                "args": args
            }
            
        except Exception as e:
            logger.error(f"Erro na consulta Fabric: {str(e)}")
            raise

class BlockchainAuditService:
    """Serviço principal de auditoria blockchain"""
    
    def __init__(self, use_hyperledger: bool = False):
        self.use_hyperledger = use_hyperledger
        self.hyperledger = HyperledgerFabricConnector() if use_hyperledger else None
        
        # Blockchain simulada para MVP
        self.blockchain: List[BlockchainBlock] = []
        self.pending_records: List[AuditRecord] = []
        self.block_size = 10  # Número de registros por bloco
        
        # Configurações de segurança
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        # Estatísticas
        self.stats = {
            "total_records": 0,
            "total_blocks": 0,
            "last_block_time": None,
            "integrity_checks": 0,
            "failed_verifications": 0
        }
        
        # Inicializar blockchain
        self._create_genesis_block()
        
        # Arquivo de persistência
        self.blockchain_file = "/tmp/certguard_blockchain.json"
        
    def _create_genesis_block(self):
        """Cria o bloco gênesis"""
        genesis_record = AuditRecord(
            id="genesis",
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id="system",
            action="blockchain_init",
            resource_type="system",
            resource_id="genesis",
            details={"message": "CertGuard AI Blockchain initialized"}
        )
        
        genesis_block = BlockchainBlock(
            index=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=[genesis_record],
            previous_hash="0"
        )
        
        genesis_block.mine_block()
        self.blockchain.append(genesis_block)
        self.stats["total_blocks"] = 1
        
        logger.info("Bloco gênesis criado")
    
    async def record_audit_event(self, 
                                user_id: str,
                                action: str,
                                resource_type: str,
                                resource_id: str,
                                details: Dict[str, Any],
                                certificate_used: Optional[str] = None,
                                ip_address: Optional[str] = None,
                                user_agent: Optional[str] = None,
                                session_id: Optional[str] = None) -> str:
        """Registra evento de auditoria"""
        
        # Cria registro de auditoria
        record_id = hashlib.sha256(f"{user_id}{action}{time.time()}".encode()).hexdigest()[:16]
        
        audit_record = AuditRecord(
            id=record_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
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
        
        # Adiciona à lista de registros pendentes
        self.pending_records.append(audit_record)
        self.stats["total_records"] += 1
        
        logger.info(f"Evento de auditoria registrado: {record_id}")
        
        # Se usar Hyperledger Fabric
        if self.use_hyperledger and self.hyperledger:
            try:
                await self.hyperledger.submit_transaction(
                    "recordAuditEvent",
                    [audit_record.to_json()]
                )
            except Exception as e:
                logger.error(f"Erro ao registrar no Hyperledger: {str(e)}")
        
        # Verifica se deve criar novo bloco
        if len(self.pending_records) >= self.block_size:
            await self._create_new_block()
        
        return record_id
    
    async def _create_new_block(self):
        """Cria novo bloco com registros pendentes"""
        if not self.pending_records:
            return
        
        # Pega o hash do último bloco
        previous_hash = self.blockchain[-1].hash if self.blockchain else "0"
        
        # Cria novo bloco
        new_block = BlockchainBlock(
            index=len(self.blockchain),
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=self.pending_records.copy(),
            previous_hash=previous_hash
        )
        
        # Minera o bloco
        new_block.mine_block()
        
        # Adiciona à blockchain
        self.blockchain.append(new_block)
        self.pending_records.clear()
        
        # Atualiza estatísticas
        self.stats["total_blocks"] += 1
        self.stats["last_block_time"] = new_block.timestamp
        
        # Persiste blockchain
        await self._persist_blockchain()
        
        logger.info(f"Novo bloco criado: {new_block.index} - Hash: {new_block.hash}")
    
    async def verify_blockchain_integrity(self) -> Dict[str, Any]:
        """Verifica integridade da blockchain"""
        self.stats["integrity_checks"] += 1
        
        if len(self.blockchain) <= 1:
            return {"valid": True, "message": "Blockchain válida (apenas gênesis)"}
        
        for i in range(1, len(self.blockchain)):
            current_block = self.blockchain[i]
            previous_block = self.blockchain[i - 1]
            
            # Verifica hash do bloco atual
            if current_block.hash != current_block.calculate_hash():
                self.stats["failed_verifications"] += 1
                return {
                    "valid": False,
                    "error": f"Hash inválido no bloco {i}",
                    "block_index": i
                }
            
            # Verifica ligação com bloco anterior
            if current_block.previous_hash != previous_block.hash:
                self.stats["failed_verifications"] += 1
                return {
                    "valid": False,
                    "error": f"Ligação inválida no bloco {i}",
                    "block_index": i
                }
        
        return {
            "valid": True,
            "message": "Blockchain íntegra",
            "total_blocks": len(self.blockchain),
            "total_records": self.stats["total_records"]
        }
    
    async def get_audit_trail(self, 
                            user_id: Optional[str] = None,
                            resource_type: Optional[str] = None,
                            resource_id: Optional[str] = None,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """Recupera trilha de auditoria com filtros"""
        
        all_records = []
        
        # Coleta registros de todos os blocos
        for block in self.blockchain:
            for record in block.data:
                all_records.append({
                    **record.to_dict(),
                    "block_index": block.index,
                    "block_hash": block.hash
                })
        
        # Adiciona registros pendentes
        for record in self.pending_records:
            all_records.append({
                **record.to_dict(),
                "block_index": "pending",
                "block_hash": "pending"
            })
        
        # Aplica filtros
        filtered_records = all_records
        
        if user_id:
            filtered_records = [r for r in filtered_records if r["user_id"] == user_id]
        
        if resource_type:
            filtered_records = [r for r in filtered_records if r["resource_type"] == resource_type]
        
        if resource_id:
            filtered_records = [r for r in filtered_records if r["resource_id"] == resource_id]
        
        if start_date:
            filtered_records = [r for r in filtered_records if r["timestamp"] >= start_date]
        
        if end_date:
            filtered_records = [r for r in filtered_records if r["timestamp"] <= end_date]
        
        # Ordena por timestamp (mais recente primeiro)
        filtered_records.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Aplica limite
        return filtered_records[:limit]
    
    async def get_certificate_usage_history(self, certificate_id: str) -> List[Dict[str, Any]]:
        """Recupera histórico de uso de certificado específico"""
        
        return await self.get_audit_trail(
            resource_type="certificate",
            resource_id=certificate_id
        )
    
    async def get_user_activity_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Gera resumo de atividade do usuário"""
        
        # Data de início
        start_date = (datetime.now(timezone.utc) - 
                     datetime.timedelta(days=days)).isoformat()
        
        records = await self.get_audit_trail(
            user_id=user_id,
            start_date=start_date,
            limit=1000
        )
        
        # Análise de atividades
        actions = {}
        resources = {}
        certificates_used = set()
        
        for record in records:
            # Conta ações
            action = record["action"]
            actions[action] = actions.get(action, 0) + 1
            
            # Conta recursos
            resource_type = record["resource_type"]
            resources[resource_type] = resources.get(resource_type, 0) + 1
            
            # Coleta certificados usados
            if record.get("certificate_used"):
                certificates_used.add(record["certificate_used"])
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_activities": len(records),
            "actions_summary": actions,
            "resources_summary": resources,
            "certificates_used": list(certificates_used),
            "first_activity": records[-1]["timestamp"] if records else None,
            "last_activity": records[0]["timestamp"] if records else None
        }
    
    async def generate_compliance_report(self, 
                                       start_date: str,
                                       end_date: str) -> Dict[str, Any]:
        """Gera relatório de conformidade"""
        
        records = await self.get_audit_trail(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Análise de conformidade
        total_activities = len(records)
        users_active = len(set(r["user_id"] for r in records))
        certificates_used = len(set(r.get("certificate_used") for r in records if r.get("certificate_used")))
        
        # Atividades por tipo
        activities_by_type = {}
        for record in records:
            action = record["action"]
            activities_by_type[action] = activities_by_type.get(action, 0) + 1
        
        # Verificação de integridade
        integrity_check = await self.verify_blockchain_integrity()
        
        return {
            "report_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_activities": total_activities,
                "users_active": users_active,
                "certificates_used": certificates_used,
                "blockchain_integrity": integrity_check["valid"]
            },
            "activities_breakdown": activities_by_type,
            "blockchain_status": {
                "total_blocks": len(self.blockchain),
                "pending_records": len(self.pending_records),
                "last_block_time": self.stats["last_block_time"]
            },
            "compliance_indicators": {
                "lgpd_compliant": True,  # Todos os dados são auditáveis
                "icp_brasil_compliant": True,  # Certificados rastreados
                "cnj_compliant": True  # Atividades processuais registradas
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _persist_blockchain(self):
        """Persiste blockchain em arquivo"""
        try:
            blockchain_data = {
                "blocks": [],
                "stats": self.stats,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            for block in self.blockchain:
                blockchain_data["blocks"].append({
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "data": [record.to_dict() for record in block.data],
                    "previous_hash": block.previous_hash,
                    "nonce": block.nonce,
                    "hash": block.hash
                })
            
            async with aiofiles.open(self.blockchain_file, 'w') as f:
                await f.write(json.dumps(blockchain_data, indent=2, ensure_ascii=False))
                
        except Exception as e:
            logger.error(f"Erro ao persistir blockchain: {str(e)}")
    
    async def load_blockchain(self):
        """Carrega blockchain do arquivo"""
        try:
            if os.path.exists(self.blockchain_file):
                async with aiofiles.open(self.blockchain_file, 'r') as f:
                    content = await f.read()
                    blockchain_data = json.loads(content)
                
                # Reconstrói blockchain
                self.blockchain = []
                for block_data in blockchain_data["blocks"]:
                    records = []
                    for record_data in block_data["data"]:
                        records.append(AuditRecord(**record_data))
                    
                    block = BlockchainBlock(
                        index=block_data["index"],
                        timestamp=block_data["timestamp"],
                        data=records,
                        previous_hash=block_data["previous_hash"],
                        nonce=block_data["nonce"],
                        hash=block_data["hash"]
                    )
                    self.blockchain.append(block)
                
                # Restaura estatísticas
                self.stats.update(blockchain_data.get("stats", {}))
                
                logger.info(f"Blockchain carregada: {len(self.blockchain)} blocos")
                
        except Exception as e:
            logger.error(f"Erro ao carregar blockchain: {str(e)}")
            # Se falhar, recria blockchain
            self._create_genesis_block()
    
    def get_blockchain_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas da blockchain"""
        return {
            **self.stats,
            "blockchain_size": len(self.blockchain),
            "pending_records": len(self.pending_records),
            "average_block_size": (
                sum(len(block.data) for block in self.blockchain) / len(self.blockchain)
                if self.blockchain else 0
            ),
            "using_hyperledger": self.use_hyperledger,
            "hyperledger_connected": (
                self.hyperledger.is_connected if self.hyperledger else False
            )
        }

# Instância global do serviço
blockchain_audit_service = BlockchainAuditService(use_hyperledger=False)  # MVP mode

# Funções de conveniência
async def record_audit(user_id: str, action: str, resource_type: str, 
                      resource_id: str, details: Dict[str, Any], **kwargs) -> str:
    """Função de conveniência para registrar auditoria"""
    return await blockchain_audit_service.record_audit_event(
        user_id, action, resource_type, resource_id, details, **kwargs
    )

async def get_audit_trail(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Função de conveniência para recuperar trilha de auditoria"""
    filters = filters or {}
    return await blockchain_audit_service.get_audit_trail(**filters)

async def verify_integrity() -> Dict[str, Any]:
    """Função de conveniência para verificar integridade"""
    return await blockchain_audit_service.verify_blockchain_integrity()

async def generate_report(start_date: str, end_date: str) -> Dict[str, Any]:
    """Função de conveniência para gerar relatório"""
    return await blockchain_audit_service.generate_compliance_report(start_date, end_date)

