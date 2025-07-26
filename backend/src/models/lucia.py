from src.database import db
from datetime import datetime
from enum import Enum
import json

class LuciaModelType(Enum):
    CHAT = "CHAT"
    DOCUMENT_ANALYSIS = "DOCUMENT_ANALYSIS"
    OCR = "OCR"
    SUMMARY = "SUMMARY"
    PREDICTION = "PREDICTION"

class LuciaProviderType(Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    GOOGLE = "GOOGLE"
    AZURE = "AZURE"
    LOCAL = "LOCAL"
    CUSTOM = "CUSTOM"

class LuciaModel(db.Model):
    __tablename__ = 'lucia_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.Enum(LuciaModelType), nullable=False)
    provider = db.Column(db.Enum(LuciaProviderType), nullable=False)
    
    # Configurações do modelo
    model_id = db.Column(db.String(255))  # ID do modelo no provedor
    api_endpoint = db.Column(db.String(500))
    api_key = db.Column(db.String(500))  # Criptografado
    model_file_path = db.Column(db.String(500))  # Para modelos locais
    
    # Parâmetros do modelo
    max_tokens = db.Column(db.Integer, default=4096)
    temperature = db.Column(db.Float, default=0.7)
    top_p = db.Column(db.Float, default=1.0)
    frequency_penalty = db.Column(db.Float, default=0.0)
    presence_penalty = db.Column(db.Float, default=0.0)
    
    # Status e configurações
    active = db.Column(db.Boolean, default=True)
    default_for_type = db.Column(db.Boolean, default=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    # Configurações específicas (JSON)
    custom_config = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    organization = db.relationship('Organization', backref='lucia_models')
    
    def __repr__(self):
        return f'<LuciaModel {self.name} ({self.model_type.value})>'
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type.value,
            'provider': self.provider.value,
            'model_id': self.model_id,
            'api_endpoint': self.api_endpoint,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'active': self.active,
            'default_for_type': self.default_for_type,
            'organization_id': self.organization_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['api_key'] = self.api_key
            data['model_file_path'] = self.model_file_path
            data['custom_config'] = self.get_custom_config()
        
        return data
    
    def get_custom_config(self):
        """Retorna configurações customizadas"""
        return json.loads(self.custom_config) if self.custom_config else {}
    
    def set_custom_config(self, config):
        """Define configurações customizadas"""
        self.custom_config = json.dumps(config)

class LuciaConversation(db.Model):
    __tablename__ = 'lucia_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    
    # Contexto da conversa
    context_data = db.Column(db.Text)  # JSON com contexto
    active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='lucia_conversations')
    
    def __repr__(self):
        return f'<LuciaConversation {self.session_id} by {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'title': self.title,
            'context_data': self.get_context_data(),
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None
        }
    
    def get_context_data(self):
        """Retorna dados de contexto"""
        return json.loads(self.context_data) if self.context_data else {}
    
    def set_context_data(self, data):
        """Define dados de contexto"""
        self.context_data = json.dumps(data)

class LuciaMessage(db.Model):
    __tablename__ = 'lucia_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('lucia_conversations.id'), nullable=False)
    
    # Conteúdo da mensagem
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    
    # Metadados
    model_used = db.Column(db.String(100))
    tokens_used = db.Column(db.Integer)
    processing_time = db.Column(db.Float)  # Tempo em segundos
    
    # Contexto adicional
    attachments = db.Column(db.Text)  # JSON com anexos
    message_metadata = db.Column(db.Text)  # JSON com metadados adicionais
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    conversation = db.relationship('LuciaConversation', backref='messages')
    
    def __repr__(self):
        return f'<LuciaMessage {self.role}: {self.content[:50]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
            'processing_time': self.processing_time,
            'attachments': self.get_attachments(),
            'message_metadata': self.get_message_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_attachments(self):
        """Retorna anexos da mensagem"""
        return json.loads(self.attachments) if self.attachments else []
    
    def set_attachments(self, attachments_list):
        """Define anexos da mensagem"""
        self.attachments = json.dumps(attachments_list)
    
    def get_message_metadata(self):
        """Retorna metadados da mensagem"""
        return json.loads(self.message_metadata) if self.message_metadata else {}
    
    def set_message_metadata(self, metadata_dict):
        """Define metadados da mensagem"""
        self.message_metadata = json.dumps(metadata_dict)

class LuciaDocumentAnalysis(db.Model):
    __tablename__ = 'lucia_document_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informações do documento
    document_name = db.Column(db.String(255), nullable=False)
    document_path = db.Column(db.String(500))
    document_hash = db.Column(db.String(255))  # SHA-256
    document_type = db.Column(db.String(50))  # PDF, DOCX, etc.
    document_size = db.Column(db.Integer)  # Tamanho em bytes
    
    # Análise realizada
    analysis_type = db.Column(db.String(50))  # OCR, SUMMARY, EXTRACTION, etc.
    model_used = db.Column(db.String(100))
    
    # Resultados
    extracted_text = db.Column(db.Text)
    summary = db.Column(db.Text)
    entities = db.Column(db.Text)  # JSON com entidades extraídas
    metadata_extracted = db.Column(db.Text)  # JSON com metadados
    
    # Métricas
    processing_time = db.Column(db.Float)
    confidence_score = db.Column(db.Float)
    tokens_used = db.Column(db.Integer)
    
    # Status
    status = db.Column(db.String(20), default='PROCESSING')  # PROCESSING, COMPLETED, FAILED
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relacionamentos
    user = db.relationship('User', backref='lucia_document_analyses')
    
    def __repr__(self):
        return f'<LuciaDocumentAnalysis {self.document_name} by {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'document_name': self.document_name,
            'document_path': self.document_path,
            'document_hash': self.document_hash,
            'document_type': self.document_type,
            'document_size': self.document_size,
            'analysis_type': self.analysis_type,
            'model_used': self.model_used,
            'extracted_text': self.extracted_text,
            'summary': self.summary,
            'entities': self.get_entities(),
            'metadata_extracted': self.get_metadata_extracted(),
            'processing_time': self.processing_time,
            'confidence_score': self.confidence_score,
            'tokens_used': self.tokens_used,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def get_entities(self):
        """Retorna entidades extraídas"""
        return json.loads(self.entities) if self.entities else []
    
    def set_entities(self, entities_list):
        """Define entidades extraídas"""
        self.entities = json.dumps(entities_list)
    
    def get_metadata_extracted(self):
        """Retorna metadados extraídos"""
        return json.loads(self.metadata_extracted) if self.metadata_extracted else {}
    
    def set_metadata_extracted(self, metadata_dict):
        """Define metadados extraídos"""
        self.metadata_extracted = json.dumps(metadata_dict)

