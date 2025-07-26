from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import jwt
import uuid
from functools import wraps

from src.database import db
from src.models.user import User, UserRole, UserStatus
from src.models.organization import Organization
from src.models.blockchain import BlockchainRecord, BlockchainEventType

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """Decorator para verificar token JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
            
            if not current_user or not current_user.is_active():
                return jsonify({'message': 'Token is invalid'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator para verificar se usuário é admin"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'message': 'Admin privileges required'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

def superadmin_required(f):
    """Decorator para verificar se usuário é superadmin"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_superadmin():
            return jsonify({'message': 'Superadmin privileges required'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password required'}), 400
        
        username = data['username']
        password = data['password']
        
        # Buscar usuário
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Verificar se usuário está bloqueado
        if user.is_locked():
            return jsonify({'message': 'Account is locked'}), 423
        
        # Verificar senha
        if not user.check_password(password):
            # Incrementar tentativas de login
            user.login_attempts += 1
            if user.login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            db.session.commit()
            
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Verificar se usuário está ativo
        if not user.is_active():
            return jsonify({'message': 'Account is not active'}), 403
        
        # Verificar horário de acesso
        if not user.can_access_now():
            return jsonify({'message': 'Access not allowed at this time'}), 403
        
        # Reset tentativas de login
        user.login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        user.last_activity = datetime.utcnow()
        
        # Gerar token JWT
        token_payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'organization_id': user.organization_id,
            'exp': datetime.utcnow() + timedelta(hours=8),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        # Registrar login no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.LOGIN,
                event_id=str(uuid.uuid4()),
                user_id=user.id,
                organization_id=user.organization_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'login',
                'username': user.username,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'success': True
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            # Log erro mas não falha o login
            current_app.logger.error(f"Erro ao registrar login no blockchain: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict(),
            'expires_in': 28800  # 8 horas em segundos
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no login: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Endpoint de logout"""
    try:
        # Atualizar última atividade
        current_user.last_activity = datetime.utcnow()
        
        # Registrar logout no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.LOGOUT,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'logout',
                'username': current_user.username,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent')
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar logout no blockchain: {str(e)}")
        
        db.session.commit()
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no logout: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Retorna informações do usuário atual"""
    try:
        # Atualizar última atividade
        current_user.last_activity = datetime.utcnow()
        db.session.commit()
        
        user_data = current_user.to_dict(include_sensitive=True)
        
        # Adicionar informações da organização se aplicável
        if current_user.organization:
            user_data['organization'] = current_user.organization.to_dict()
        
        return jsonify(user_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar usuário atual: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Renova token JWT"""
    try:
        # Atualizar última atividade
        current_user.last_activity = datetime.utcnow()
        db.session.commit()
        
        # Gerar novo token
        token_payload = {
            'user_id': current_user.id,
            'username': current_user.username,
            'role': current_user.role.value,
            'organization_id': current_user.organization_id,
            'exp': datetime.utcnow() + timedelta(hours=8),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Token refreshed',
            'token': token,
            'expires_in': 28800
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao renovar token: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Altera senha do usuário"""
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'message': 'Current password and new password required'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verificar senha atual
        if not current_user.check_password(current_password):
            return jsonify({'message': 'Current password is incorrect'}), 400
        
        # Validar nova senha
        if len(new_password) < 8:
            return jsonify({'message': 'New password must be at least 8 characters long'}), 400
        
        # Alterar senha
        current_user.set_password(new_password)
        current_user.updated_at = datetime.utcnow()
        
        # Registrar alteração no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.SECURITY_EVENT,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'password_change',
                'username': current_user.username,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': request.remote_addr
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar alteração de senha no blockchain: {str(e)}")
        
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao alterar senha: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/verify-access', methods=['POST'])
@token_required
def verify_access(current_user):
    """Verifica se usuário pode acessar um site específico"""
    try:
        data = request.get_json()
        
        if not data or not data.get('site_url'):
            return jsonify({'message': 'Site URL required'}), 400
        
        site_url = data['site_url']
        
        # Verificar se usuário pode acessar o site
        can_access = current_user.can_access_site(site_url)
        
        # Verificar horário de acesso
        can_access_now = current_user.can_access_now()
        
        return jsonify({
            'can_access': can_access and can_access_now,
            'site_url': site_url,
            'user_id': current_user.id,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar acesso: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

