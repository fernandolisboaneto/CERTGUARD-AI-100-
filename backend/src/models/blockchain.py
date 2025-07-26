from src.database import db
from datetime import datetime
from enum import Enum
import json
import hashlib

class BlockchainEventType(Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CERTIFICATE_ACCESS = "CERTIFICATE_ACCESS"
    DOCUMENT_SIGNATURE = "DOCUMENT_SIGNATURE"
    DOCUMENT_ACCESS = "DOCUMENT_ACCESS"
    PERMISSION_CHANGE = "PERMISSION_CHANGE"
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
    SECURITY_EVENT = "SECURITY_EVENT"
    AUDIT_EVENT = "AUDIT_EVENT"

class BlockchainStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"

class BlockchainRecord(db.Model):
    __tablename__ = 'blockchain_records'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Identificação do evento
    event_type = db.Column(db.Enum(BlockchainEventType), nullable=False)
    event_id = db.Column(db.String(255), unique=True, nullable=False)  # UUID único
    
    # Dados do evento
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'))
    
    # Conteúdo do evento
    event_data = db.Column(db.Text, nullable=False)  # JSON com dados do evento
    event_hash = db.Column(db.String(255), nullable=False)  # SHA-256 dos dados
    
    # Contexto técnico
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    geolocation = db.Column(db.Text)  # JSON com lat/lng
    
    # Informações blockchain
    blockchain_hash = db.Column(db.String(255))  # Hash da transação no blockchain
    block_number = db.Column(db.Integer)
    transaction_id = db.Column(db.String(255))
    gas_used = db.Column(db.Integer)
    
    # Status
    status = db.Column(db.Enum(BlockchainStatus), default=BlockchainStatus.PENDING)
    confirmations = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    blockchain_timestamp = db.Column(db.DateTime)
    confirmed_at = db.Column(db.DateTime)
    
    # Relacionamentos
    user = db.relationship('User', backref='blockchain_records')
    organization = db.relationship('Organization', backref='blockchain_records')
    certificate = db.relationship('Certificate', backref='blockchain_records')
    
    def __repr__(self):
        return f'<BlockchainRecord {self.event_type.value} {self.event_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'certificate_id': self.certificate_id,
            'event_data': self.get_event_data(),
            'event_hash': self.event_hash,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'geolocation': self.get_geolocation(),
            'blockchain_hash': self.blockchain_hash,
            'block_number': self.block_number,
            'transaction_id': self.transaction_id,
            'gas_used': self.gas_used,
            'status': self.status.value,
            'confirmations': self.confirmations,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'blockchain_timestamp': self.blockchain_timestamp.isoformat() if self.blockchain_timestamp else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None
        }
    
    def get_event_data(self):
        """Retorna dados do evento"""
        return json.loads(self.event_data) if self.event_data else {}
    
    def set_event_data(self, data):
        """Define dados do evento e calcula hash"""
        self.event_data = json.dumps(data, sort_keys=True)
        self.event_hash = self.calculate_event_hash()
    
    def get_geolocation(self):
        """Retorna dados de geolocalização"""
        return json.loads(self.geolocation) if self.geolocation else {}
    
    def set_geolocation(self, location_data):
        """Define dados de geolocalização"""
        self.geolocation = json.dumps(location_data)
    
    def calculate_event_hash(self):
        """Calcula hash SHA-256 dos dados do evento"""
        if not self.event_data:
            return None
        
        # Cria string determinística para hash
        hash_data = {
            'event_type': self.event_type.value,
            'event_data': self.event_data,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'certificate_id': self.certificate_id,
            'timestamp': self.created_at.isoformat() if self.created_at else None
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def verify_integrity(self):
        """Verifica integridade do registro"""
        calculated_hash = self.calculate_event_hash()
        return calculated_hash == self.event_hash
    
    def is_confirmed(self):
        """Verifica se o registro está confirmado no blockchain"""
        return self.status == BlockchainStatus.CONFIRMED and self.confirmations >= 6

class SmartContract(db.Model):
    __tablename__ = 'smart_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contract_type = db.Column(db.String(50), nullable=False)  # AUDIT, COMPLIANCE, ACCESS_CONTROL
    
    # Informações do contrato
    contract_address = db.Column(db.String(255))
    abi = db.Column(db.Text)  # Application Binary Interface
    bytecode = db.Column(db.Text)
    source_code = db.Column(db.Text)
    
    # Configurações
    active = db.Column(db.Boolean, default=True)
    version = db.Column(db.String(20))
    description = db.Column(db.Text)
    
    # Deployment info
    deployed_at = db.Column(db.DateTime)
    deployed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    deployment_tx = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    deployer = db.relationship('User', backref='deployed_contracts')
    
    def __repr__(self):
        return f'<SmartContract {self.name} ({self.contract_type})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contract_type': self.contract_type,
            'contract_address': self.contract_address,
            'active': self.active,
            'version': self.version,
            'description': self.description,
            'deployed_at': self.deployed_at.isoformat() if self.deployed_at else None,
            'deployed_by': self.deployed_by,
            'deployment_tx': self.deployment_tx,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BlockchainNetwork(db.Model):
    __tablename__ = 'blockchain_networks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    network_type = db.Column(db.String(50), default='HYPERLEDGER_FABRIC')
    
    # Configurações de rede
    network_config = db.Column(db.Text)  # JSON com configuração da rede
    peer_nodes = db.Column(db.Text)  # JSON com lista de nós peer
    orderer_nodes = db.Column(db.Text)  # JSON com lista de nós orderer
    
    # Credenciais e certificados
    admin_cert = db.Column(db.Text)
    admin_key = db.Column(db.Text)
    ca_cert = db.Column(db.Text)
    
    # Status
    active = db.Column(db.Boolean, default=True)
    last_block_number = db.Column(db.Integer, default=0)
    last_sync = db.Column(db.DateTime)
    
    # Métricas
    total_transactions = db.Column(db.Integer, default=0)
    avg_block_time = db.Column(db.Float)  # Tempo médio entre blocos em segundos
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BlockchainNetwork {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'network_type': self.network_type,
            'active': self.active,
            'last_block_number': self.last_block_number,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'total_transactions': self.total_transactions,
            'avg_block_time': self.avg_block_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_network_config(self):
        """Retorna configuração da rede"""
        return json.loads(self.network_config) if self.network_config else {}
    
    def set_network_config(self, config):
        """Define configuração da rede"""
        self.network_config = json.dumps(config)
    
    def get_peer_nodes(self):
        """Retorna lista de nós peer"""
        return json.loads(self.peer_nodes) if self.peer_nodes else []
    
    def set_peer_nodes(self, nodes):
        """Define lista de nós peer"""
        self.peer_nodes = json.dumps(nodes)
    
    def get_orderer_nodes(self):
        """Retorna lista de nós orderer"""
        return json.loads(self.orderer_nodes) if self.orderer_nodes else []
    
    def set_orderer_nodes(self, nodes):
        """Define lista de nós orderer"""
        self.orderer_nodes = json.dumps(nodes)

