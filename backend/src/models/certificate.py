from src.database import db
from datetime import datetime, timedelta
from enum import Enum
import json

class CertificateType(Enum):
    A1 = "A1"
    A3 = "A3"

class CertificateStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUSPENDED = "SUSPENDED"

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(255), unique=True, nullable=False)
    subject_name = db.Column(db.String(500), nullable=False)
    issuer_name = db.Column(db.String(500), nullable=False)
    certificate_type = db.Column(db.Enum(CertificateType), nullable=False)
    status = db.Column(db.Enum(CertificateStatus), default=CertificateStatus.ACTIVE)
    
    # Datas importantes
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Informações específicas
    oab_number = db.Column(db.String(50))  # Número da OAB quando aplicável
    cpf_cnpj = db.Column(db.String(20))
    email = db.Column(db.String(255))
    
    # Dados técnicos
    thumbprint = db.Column(db.String(255))  # SHA-1 thumbprint
    public_key_info = db.Column(db.Text)  # Informações da chave pública
    certificate_policies = db.Column(db.Text)  # Políticas do certificado (JSON)
    
    # Relacionamentos
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    organization = db.relationship('Organization', backref='certificates')
    
    # Configurações de uso
    allowed_sites = db.Column(db.Text)  # JSON com sites permitidos
    allowed_hours = db.Column(db.Text)  # JSON com horários permitidos
    
    def __repr__(self):
        return f'<Certificate {self.subject_name} ({self.serial_number})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'serial_number': self.serial_number,
            'subject_name': self.subject_name,
            'issuer_name': self.issuer_name,
            'certificate_type': self.certificate_type.value,
            'status': self.status.value,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'oab_number': self.oab_number,
            'cpf_cnpj': self.cpf_cnpj,
            'email': self.email,
            'thumbprint': self.thumbprint,
            'organization_id': self.organization_id,
            'allowed_sites': json.loads(self.allowed_sites) if self.allowed_sites else [],
            'allowed_hours': json.loads(self.allowed_hours) if self.allowed_hours else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_valid(self):
        """Verifica se o certificado está válido"""
        now = datetime.utcnow()
        return (self.status == CertificateStatus.ACTIVE and 
                self.valid_from <= now <= self.valid_until)
    
    def days_until_expiry(self):
        """Retorna quantos dias faltam para expirar"""
        if self.valid_until:
            delta = self.valid_until - datetime.utcnow()
            return delta.days
        return None
    
    def set_allowed_sites(self, sites_list):
        """Define sites permitidos para este certificado"""
        self.allowed_sites = json.dumps(sites_list)
    
    def get_allowed_sites(self):
        """Retorna lista de sites permitidos"""
        return json.loads(self.allowed_sites) if self.allowed_sites else []
    
    def set_allowed_hours(self, hours_config):
        """Define horários permitidos para uso do certificado"""
        self.allowed_hours = json.dumps(hours_config)
    
    def get_allowed_hours(self):
        """Retorna configuração de horários permitidos"""
        return json.loads(self.allowed_hours) if self.allowed_hours else {}

class CertificateUsageLog(db.Model):
    __tablename__ = 'certificate_usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Detalhes do uso
    action = db.Column(db.String(100), nullable=False)  # LOGIN, SIGNATURE, ACCESS, etc.
    target_site = db.Column(db.String(255))  # Site acessado
    ip_address = db.Column(db.String(45))  # IPv4 ou IPv6
    user_agent = db.Column(db.Text)
    geolocation = db.Column(db.Text)  # JSON com lat/lng
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_duration = db.Column(db.Integer)  # Duração em segundos
    
    # Status e resultado
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    # Hash blockchain (quando aplicável)
    blockchain_hash = db.Column(db.String(255))
    
    # Relacionamentos
    certificate = db.relationship('Certificate', backref='usage_logs')
    user = db.relationship('User', backref='certificate_usage_logs')
    
    def __repr__(self):
        return f'<CertificateUsageLog {self.action} by {self.user_id} at {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'user_id': self.user_id,
            'action': self.action,
            'target_site': self.target_site,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'geolocation': json.loads(self.geolocation) if self.geolocation else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_duration': self.session_duration,
            'success': self.success,
            'error_message': self.error_message,
            'blockchain_hash': self.blockchain_hash
        }

