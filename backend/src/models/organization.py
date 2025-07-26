from src.database import db
from datetime import datetime
from enum import Enum
import json

class OrganizationType(Enum):
    LAW_FIRM = "LAW_FIRM"
    CORPORATE_LEGAL = "CORPORATE_LEGAL"
    SOLO_PRACTICE = "SOLO_PRACTICE"
    PUBLIC_DEFENDER = "PUBLIC_DEFENDER"
    PROSECUTOR = "PROSECUTOR"

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    legal_name = db.Column(db.String(255))
    cnpj = db.Column(db.String(18), unique=True)
    organization_type = db.Column(db.Enum(OrganizationType), nullable=False)
    
    # Informações de contato
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(255))
    
    # Endereço
    address_street = db.Column(db.String(255))
    address_number = db.Column(db.String(20))
    address_complement = db.Column(db.String(100))
    address_neighborhood = db.Column(db.String(100))
    address_city = db.Column(db.String(100))
    address_state = db.Column(db.String(2))
    address_zipcode = db.Column(db.String(10))
    
    # Status e configurações
    active = db.Column(db.Boolean, default=True)
    max_users = db.Column(db.Integer, default=10)
    max_certificates = db.Column(db.Integer, default=5)
    
    # Configurações de segurança
    security_policies = db.Column(db.Text)  # JSON com políticas de segurança
    compliance_settings = db.Column(db.Text)  # JSON com configurações de compliance
    
    # Configurações da LucIA
    lucia_config = db.Column(db.Text)  # JSON com configurações da IA
    lucia_enabled = db.Column(db.Boolean, default=True)
    
    # Configurações de blockchain
    blockchain_enabled = db.Column(db.Boolean, default=True)
    blockchain_config = db.Column(db.Text)  # JSON com configurações blockchain
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Organization {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'legal_name': self.legal_name,
            'cnpj': self.cnpj,
            'organization_type': self.organization_type.value,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'address': {
                'street': self.address_street,
                'number': self.address_number,
                'complement': self.address_complement,
                'neighborhood': self.address_neighborhood,
                'city': self.address_city,
                'state': self.address_state,
                'zipcode': self.address_zipcode
            },
            'active': self.active,
            'max_users': self.max_users,
            'max_certificates': self.max_certificates,
            'lucia_enabled': self.lucia_enabled,
            'blockchain_enabled': self.blockchain_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_security_policies(self):
        """Retorna políticas de segurança da organização"""
        return json.loads(self.security_policies) if self.security_policies else {}
    
    def set_security_policies(self, policies):
        """Define políticas de segurança da organização"""
        self.security_policies = json.dumps(policies)
    
    def get_compliance_settings(self):
        """Retorna configurações de compliance"""
        return json.loads(self.compliance_settings) if self.compliance_settings else {}
    
    def set_compliance_settings(self, settings):
        """Define configurações de compliance"""
        self.compliance_settings = json.dumps(settings)
    
    def get_lucia_config(self):
        """Retorna configurações da LucIA"""
        return json.loads(self.lucia_config) if self.lucia_config else {}
    
    def set_lucia_config(self, config):
        """Define configurações da LucIA"""
        self.lucia_config = json.dumps(config)
    
    def get_blockchain_config(self):
        """Retorna configurações do blockchain"""
        return json.loads(self.blockchain_config) if self.blockchain_config else {}
    
    def set_blockchain_config(self, config):
        """Define configurações do blockchain"""
        self.blockchain_config = json.dumps(config)
    
    def get_active_users_count(self):
        """Retorna número de usuários ativos"""
        from src.models.user import User
        return User.query.filter_by(organization_id=self.id, active=True).count()
    
    def get_active_certificates_count(self):
        """Retorna número de certificados ativos"""
        from src.models.certificate import Certificate, CertificateStatus
        return Certificate.query.filter_by(
            organization_id=self.id, 
            status=CertificateStatus.ACTIVE
        ).count()
    
    def can_add_user(self):
        """Verifica se pode adicionar mais usuários"""
        return self.get_active_users_count() < self.max_users
    
    def can_add_certificate(self):
        """Verifica se pode adicionar mais certificados"""
        return self.get_active_certificates_count() < self.max_certificates

class OrganizationSettings(db.Model):
    __tablename__ = 'organization_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    setting_key = db.Column(db.String(100), nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20), default='string')  # string, json, boolean, integer
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    organization = db.relationship('Organization', backref='settings')
    
    __table_args__ = (db.UniqueConstraint('organization_id', 'setting_key'),)
    
    def __repr__(self):
        return f'<OrganizationSettings {self.setting_key}={self.setting_value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'setting_key': self.setting_key,
            'setting_value': self.get_typed_value(),
            'setting_type': self.setting_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_typed_value(self):
        """Retorna o valor com o tipo correto"""
        if self.setting_type == 'json':
            return json.loads(self.setting_value) if self.setting_value else None
        elif self.setting_type == 'boolean':
            return self.setting_value.lower() == 'true' if self.setting_value else False
        elif self.setting_type == 'integer':
            return int(self.setting_value) if self.setting_value else 0
        else:
            return self.setting_value
    
    def set_typed_value(self, value):
        """Define o valor com conversão de tipo"""
        if self.setting_type == 'json':
            self.setting_value = json.dumps(value)
        elif self.setting_type == 'boolean':
            self.setting_value = str(bool(value)).lower()
        elif self.setting_type == 'integer':
            self.setting_value = str(int(value))
        else:
            self.setting_value = str(value)

