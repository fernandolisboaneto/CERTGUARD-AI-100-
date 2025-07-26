from src.database import db
from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
import json

class UserRole(Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    USER = "USER"

class UserStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Informações pessoais
    full_name = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14))
    oab_number = db.Column(db.String(50))
    oab_state = db.Column(db.String(2))
    phone = db.Column(db.String(20))
    
    # Hierarquia e permissões
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    status = db.Column(db.Enum(UserStatus), default=UserStatus.PENDING)
    
    # Relacionamentos
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization', backref='users')
    
    # Configurações de segurança
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(255))
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Configurações de acesso
    allowed_sites = db.Column(db.Text)  # JSON com sites permitidos
    allowed_hours = db.Column(db.Text)  # JSON com horários permitidos
    ip_restrictions = db.Column(db.Text)  # JSON com restrições de IP
    
    # Configurações da LucIA
    lucia_preferences = db.Column(db.Text)  # JSON com preferências da IA
    lucia_enabled = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role.value})>'
    
    def set_password(self, password):
        """Define senha com hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica senha"""
        return check_password_hash(self.password_hash, password)
    
    def is_superadmin(self):
        """Verifica se é superadmin"""
        return self.role == UserRole.SUPERADMIN
    
    def is_admin(self):
        """Verifica se é admin ou superadmin"""
        return self.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    
    def is_active(self):
        """Verifica se usuário está ativo"""
        return self.status == UserStatus.ACTIVE
    
    def is_locked(self):
        """Verifica se usuário está bloqueado"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'cpf': self.cpf,
            'oab_number': self.oab_number,
            'oab_state': self.oab_state,
            'phone': self.phone,
            'role': self.role.value,
            'status': self.status.value,
            'organization_id': self.organization_id,
            'mfa_enabled': self.mfa_enabled,
            'lucia_enabled': self.lucia_enabled,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
        
        if include_sensitive:
            data.update({
                'allowed_sites': self.get_allowed_sites(),
                'allowed_hours': self.get_allowed_hours(),
                'ip_restrictions': self.get_ip_restrictions(),
                'lucia_preferences': self.get_lucia_preferences()
            })
        
        return data
    
    def get_allowed_sites(self):
        """Retorna sites permitidos para o usuário"""
        return json.loads(self.allowed_sites) if self.allowed_sites else []
    
    def set_allowed_sites(self, sites_list):
        """Define sites permitidos para o usuário"""
        self.allowed_sites = json.dumps(sites_list)
    
    def get_allowed_hours(self):
        """Retorna horários permitidos"""
        return json.loads(self.allowed_hours) if self.allowed_hours else {}
    
    def set_allowed_hours(self, hours_config):
        """Define horários permitidos"""
        self.allowed_hours = json.dumps(hours_config)
    
    def get_ip_restrictions(self):
        """Retorna restrições de IP"""
        return json.loads(self.ip_restrictions) if self.ip_restrictions else []
    
    def set_ip_restrictions(self, ip_list):
        """Define restrições de IP"""
        self.ip_restrictions = json.dumps(ip_list)
    
    def get_lucia_preferences(self):
        """Retorna preferências da LucIA"""
        return json.loads(self.lucia_preferences) if self.lucia_preferences else {}
    
    def set_lucia_preferences(self, preferences):
        """Define preferências da LucIA"""
        self.lucia_preferences = json.dumps(preferences)
    
    def can_access_site(self, site_url):
        """Verifica se usuário pode acessar um site específico"""
        allowed_sites = self.get_allowed_sites()
        if not allowed_sites:
            return False
        
        # Verifica se o site está na lista de permitidos
        for allowed_site in allowed_sites:
            if site_url.startswith(allowed_site) or allowed_site in site_url:
                return True
        return False
    
    def can_access_now(self):
        """Verifica se usuário pode acessar no horário atual"""
        if not self.is_active() or self.is_locked():
            return False
        
        allowed_hours = self.get_allowed_hours()
        if not allowed_hours:
            return True  # Se não há restrições, permite acesso
        
        now = datetime.utcnow()
        weekday = now.strftime('%A').lower()
        current_time = now.strftime('%H:%M')
        
        if weekday in allowed_hours:
            day_config = allowed_hours[weekday]
            if day_config.get('enabled', True):
                start_time = day_config.get('start', '00:00')
                end_time = day_config.get('end', '23:59')
                return start_time <= current_time <= end_time
        
        return False

class UserCertificatePermission(db.Model):
    __tablename__ = 'user_certificate_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=False)
    
    # Permissões específicas
    can_login = db.Column(db.Boolean, default=True)
    can_sign = db.Column(db.Boolean, default=False)
    can_access_confidential = db.Column(db.Boolean, default=False)
    can_download_documents = db.Column(db.Boolean, default=False)
    
    # Restrições temporais específicas para este certificado
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='certificate_permissions')
    certificate = db.relationship('Certificate', backref='user_permissions')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'certificate_id'),)
    
    def __repr__(self):
        return f'<UserCertificatePermission User:{self.user_id} Cert:{self.certificate_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'certificate_id': self.certificate_id,
            'can_login': self.can_login,
            'can_sign': self.can_sign,
            'can_access_confidential': self.can_access_confidential,
            'can_download_documents': self.can_download_documents,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_valid_now(self):
        """Verifica se a permissão está válida no momento atual"""
        now = datetime.utcnow()
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        return True
