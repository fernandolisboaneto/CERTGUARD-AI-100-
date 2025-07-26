from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import uuid
import json
import hashlib
import os

from src.database import db
from src.models.user import User
from src.models.lucia import (
    LuciaModel, LuciaModelType, LuciaProviderType,
    LuciaConversation, LuciaMessage, LuciaDocumentAnalysis
)
from src.models.blockchain import BlockchainRecord, BlockchainEventType
from src.routes.auth import token_required, admin_required, superadmin_required

lucia_bp = Blueprint('lucia', __name__)

@lucia_bp.route('/models', methods=['GET'])
@token_required
@admin_required
def list_lucia_models(current_user):
    """Lista modelos da LucIA disponíveis"""
    try:
        # Filtrar por organização se não for superadmin
        if current_user.is_superadmin():
            models = LuciaModel.query.filter_by(active=True).all()
        else:
            models = LuciaModel.query.filter(
                (LuciaModel.organization_id == current_user.organization_id) |
                (LuciaModel.organization_id.is_(None))  # Modelos globais
            ).filter_by(active=True).all()
        
        # Agrupar por tipo
        models_by_type = {}
        for model in models:
            model_type = model.model_type.value
            if model_type not in models_by_type:
                models_by_type[model_type] = []
            
            model_data = model.to_dict()
            if not current_user.is_superadmin():
                # Remover informações sensíveis
                model_data.pop('api_key', None)
                model_data.pop('model_file_path', None)
            
            models_by_type[model_type].append(model_data)
        
        return jsonify({
            'models_by_type': models_by_type,
            'total_models': len(models)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar modelos da LucIA: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@lucia_bp.route('/models', methods=['POST'])
@token_required
@superadmin_required
def create_lucia_model(current_user):
    """Cria um novo modelo da LucIA (apenas superadmin)"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['name', 'model_type', 'provider']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Field {field} is required'}), 400
        
        # Criar modelo
        model = LuciaModel(
            name=data['name'],
            model_type=LuciaModelType(data['model_type']),
            provider=LuciaProviderType(data['provider']),
            model_id=data.get('model_id'),
            api_endpoint=data.get('api_endpoint'),
            api_key=data.get('api_key'),
            model_file_path=data.get('model_file_path'),
            max_tokens=data.get('max_tokens', 4096),
            temperature=data.get('temperature', 0.7),
            top_p=data.get('top_p', 1.0),
            frequency_penalty=data.get('frequency_penalty', 0.0),
            presence_penalty=data.get('presence_penalty', 0.0),
            default_for_type=data.get('default_for_type', False),
            organization_id=data.get('organization_id')  # None para modelos globais
        )
        
        if data.get('custom_config'):
            model.set_custom_config(data['custom_config'])
        
        # Se for marcado como padrão, desmarcar outros do mesmo tipo
        if model.default_for_type:
            existing_defaults = LuciaModel.query.filter_by(
                model_type=model.model_type,
                default_for_type=True,
                organization_id=model.organization_id
            ).all()
            
            for existing in existing_defaults:
                existing.default_for_type = False
        
        db.session.add(model)
        db.session.flush()
        
        # Registrar criação no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.CONFIGURATION_CHANGE,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=model.organization_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'lucia_model_created',
                'model_id': model.id,
                'model_name': model.name,
                'model_type': model.model_type.value,
                'provider': model.provider.value,
                'created_by': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar criação de modelo no blockchain: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'LucIA model created successfully',
            'model': model.to_dict(include_sensitive=True)
        }), 201
        
    except ValueError as e:
        return jsonify({'message': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao criar modelo da LucIA: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@lucia_bp.route('/chat', methods=['POST'])
@token_required
def chat_with_lucia(current_user):
    """Inicia ou continua conversa com a LucIA"""
    try:
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({'message': 'Message is required'}), 400
        
        message_content = data['message']
        session_id = data.get('session_id')
        context = data.get('context', {})
        
        # Buscar ou criar conversa
        if session_id:
            conversation = LuciaConversation.query.filter_by(
                session_id=session_id,
                user_id=current_user.id
            ).first()
            
            if not conversation:
                return jsonify({'message': 'Conversation not found'}), 404
        else:
            # Criar nova conversa
            session_id = str(uuid.uuid4())
            conversation = LuciaConversation(
                user_id=current_user.id,
                session_id=session_id,
                title=message_content[:50] + "..." if len(message_content) > 50 else message_content
            )
            conversation.set_context_data(context)
            db.session.add(conversation)
            db.session.flush()
        
        # Adicionar mensagem do usuário
        user_message = LuciaMessage(
            conversation_id=conversation.id,
            role='user',
            content=message_content
        )
        db.session.add(user_message)
        
        # Buscar modelo de chat padrão
        chat_model = LuciaModel.query.filter_by(
            model_type=LuciaModelType.CHAT,
            default_for_type=True,
            active=True
        ).filter(
            (LuciaModel.organization_id == current_user.organization_id) |
            (LuciaModel.organization_id.is_(None))
        ).first()
        
        if not chat_model:
            return jsonify({'message': 'No chat model configured'}), 500
        
        # Simular resposta da IA (em implementação real, seria chamada para o modelo)
        ai_response = generate_lucia_response(message_content, conversation, chat_model)
        
        # Adicionar resposta da IA
        ai_message = LuciaMessage(
            conversation_id=conversation.id,
            role='assistant',
            content=ai_response['content'],
            model_used=chat_model.name,
            tokens_used=ai_response.get('tokens_used', 0),
            processing_time=ai_response.get('processing_time', 0.0)
        )
        db.session.add(ai_message)
        
        # Atualizar conversa
        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'session_id': session_id,
            'conversation_id': conversation.id,
            'response': ai_response['content'],
            'model_used': chat_model.name,
            'tokens_used': ai_response.get('tokens_used', 0),
            'processing_time': ai_response.get('processing_time', 0.0)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no chat com LucIA: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@lucia_bp.route('/conversations', methods=['GET'])
@token_required
def list_conversations(current_user):
    """Lista conversas do usuário"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        conversations = LuciaConversation.query.filter_by(
            user_id=current_user.id,
            active=True
        ).order_by(LuciaConversation.last_message_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        conversations_data = []
        for conv in conversations.items:
            conv_data = conv.to_dict()
            # Adicionar última mensagem
            last_message = LuciaMessage.query.filter_by(
                conversation_id=conv.id
            ).order_by(LuciaMessage.created_at.desc()).first()
            
            if last_message:
                conv_data['last_message'] = {
                    'role': last_message.role,
                    'content': last_message.content[:100] + "..." if len(last_message.content) > 100 else last_message.content,
                    'created_at': last_message.created_at.isoformat()
                }
            
            conversations_data.append(conv_data)
        
        return jsonify({
            'conversations': conversations_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': conversations.total,
                'pages': conversations.pages,
                'has_next': conversations.has_next,
                'has_prev': conversations.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar conversas: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@lucia_bp.route('/conversations/<session_id>/messages', methods=['GET'])
@token_required
def get_conversation_messages(current_user, session_id):
    """Obtém mensagens de uma conversa"""
    try:
        conversation = LuciaConversation.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'message': 'Conversation not found'}), 404
        
        messages = LuciaMessage.query.filter_by(
            conversation_id=conversation.id
        ).order_by(LuciaMessage.created_at.asc()).all()
        
        return jsonify({
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar mensagens da conversa: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@lucia_bp.route('/analyze-document', methods=['POST'])
@token_required
def analyze_document(current_user):
    """Analisa um documento com a LucIA"""
    try:
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        analysis_type = request.form.get('analysis_type', 'SUMMARY')
        
        # Validar tipo de análise
        valid_types = ['OCR', 'SUMMARY', 'EXTRACTION', 'CLASSIFICATION']
        if analysis_type not in valid_types:
            return jsonify({'message': f'Invalid analysis type. Must be one of: {valid_types}'}), 400
        
        # Salvar arquivo temporariamente
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join('/tmp', filename)
        file.save(file_path)
        
        # Calcular hash do arquivo
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Buscar modelo apropriado
        if analysis_type == 'OCR':
            model_type = LuciaModelType.OCR
        elif analysis_type in ['SUMMARY', 'EXTRACTION', 'CLASSIFICATION']:
            model_type = LuciaModelType.DOCUMENT_ANALYSIS
        else:
            model_type = LuciaModelType.DOCUMENT_ANALYSIS
        
        model = LuciaModel.query.filter_by(
            model_type=model_type,
            default_for_type=True,
            active=True
        ).filter(
            (LuciaModel.organization_id == current_user.organization_id) |
            (LuciaModel.organization_id.is_(None))
        ).first()
        
        if not model:
            os.remove(file_path)
            return jsonify({'message': f'No {model_type.value} model configured'}), 500
        
        # Criar registro de análise
        analysis = LuciaDocumentAnalysis(
            user_id=current_user.id,
            document_name=file.filename,
            document_path=file_path,
            document_hash=file_hash,
            document_type=file.filename.split('.')[-1].upper(),
            document_size=os.path.getsize(file_path),
            analysis_type=analysis_type,
            model_used=model.name,
            status='PROCESSING'
        )
        
        db.session.add(analysis)
        db.session.flush()
        
        # Simular análise do documento
        analysis_result = perform_document_analysis(file_path, analysis_type, model)
        
        # Atualizar análise com resultados
        analysis.extracted_text = analysis_result.get('extracted_text')
        analysis.summary = analysis_result.get('summary')
        analysis.set_entities(analysis_result.get('entities', []))
        analysis.set_metadata_extracted(analysis_result.get('metadata', {}))
        analysis.processing_time = analysis_result.get('processing_time', 0.0)
        analysis.confidence_score = analysis_result.get('confidence_score', 0.0)
        analysis.tokens_used = analysis_result.get('tokens_used', 0)
        analysis.status = 'COMPLETED'
        analysis.completed_at = datetime.utcnow()
        
        # Registrar análise no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.DOCUMENT_ACCESS,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'document_analysis',
                'analysis_id': analysis.id,
                'document_name': analysis.document_name,
                'document_hash': analysis.document_hash,
                'analysis_type': analysis_type,
                'model_used': model.name,
                'analyzed_by': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar análise no blockchain: {str(e)}")
        
        db.session.commit()
        
        # Remover arquivo temporário
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify({
            'message': 'Document analysis completed',
            'analysis': analysis.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro na análise de documento: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@lucia_bp.route('/document-analyses', methods=['GET'])
@token_required
def list_document_analyses(current_user):
    """Lista análises de documentos do usuário"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        analyses = LuciaDocumentAnalysis.query.filter_by(
            user_id=current_user.id
        ).order_by(LuciaDocumentAnalysis.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'analyses': [analysis.to_dict() for analysis in analyses.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': analyses.total,
                'pages': analyses.pages,
                'has_next': analyses.has_next,
                'has_prev': analyses.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar análises de documentos: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

def generate_lucia_response(message, conversation, model):
    """Gera resposta da LucIA (simulação)"""
    # Em implementação real, seria feita chamada para o modelo de IA
    responses = [
        "Olá! Sou a LucIA, sua assistente jurídica inteligente. Como posso ajudá-lo hoje?",
        "Entendi sua solicitação. Vou analisar as informações disponíveis e fornecer uma resposta detalhada.",
        "Baseado no contexto fornecido, posso sugerir as seguintes ações...",
        "Para melhor atendê-lo, preciso de algumas informações adicionais sobre o processo.",
        "Analisei o documento e identifiquei os seguintes pontos importantes..."
    ]
    
    import random
    response_content = random.choice(responses)
    
    return {
        'content': response_content,
        'tokens_used': len(response_content.split()) * 2,  # Simulação
        'processing_time': random.uniform(0.5, 2.0)  # Simulação
    }

def perform_document_analysis(file_path, analysis_type, model):
    """Realiza análise de documento (simulação)"""
    # Em implementação real, seria feita análise com modelo de IA
    
    result = {
        'processing_time': random.uniform(1.0, 5.0),
        'confidence_score': random.uniform(0.8, 0.95),
        'tokens_used': random.randint(100, 1000)
    }
    
    if analysis_type == 'OCR':
        result['extracted_text'] = "Texto extraído do documento via OCR..."
    elif analysis_type == 'SUMMARY':
        result['summary'] = "Resumo do documento: Este documento trata de..."
        result['extracted_text'] = "Texto completo do documento..."
    elif analysis_type == 'EXTRACTION':
        result['entities'] = [
            {'type': 'PERSON', 'value': 'João Silva', 'confidence': 0.95},
            {'type': 'DATE', 'value': '2024-01-15', 'confidence': 0.90},
            {'type': 'MONEY', 'value': 'R$ 10.000,00', 'confidence': 0.85}
        ]
        result['metadata'] = {
            'document_type': 'Contrato',
            'parties': ['João Silva', 'Maria Santos'],
            'date': '2024-01-15',
            'value': 'R$ 10.000,00'
        }
    
    import random
    return result

