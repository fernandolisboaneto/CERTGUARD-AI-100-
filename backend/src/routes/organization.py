from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import uuid

from src.database import db
from src.models.user import User, UserRole, UserStatus
from src.models.organization import Organization, OrganizationType, OrganizationSettings
from src.models.blockchain import BlockchainRecord, BlockchainEventType
from src.routes.auth import token_required, admin_required, superadmin_required

organization_bp = Blueprint('organization', __name__)

@organization_bp.route('/', methods=['GET'])
@token_required
@superadmin_required
def list_organizations(current_user):
    """Lista todas as organizações (apenas superadmin)"""
    try:
        organizations = Organization.query.all()
        
        organizations_data = []
        for org in organizations:
            org_data = org.to_dict()
            org_data['active_users_count'] = org.get_active_users_count()
            org_data['active_certificates_count'] = org.get_active_certificates_count()
            organizations_data.append(org_data)
        
        return jsonify({
            'organizations': organizations_data,
            'total': len(organizations_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar organizações: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@organization_bp.route('/<int:organization_id>', methods=['GET'])
@token_required
def get_organization(current_user, organization_id):
    """Obtém detalhes de uma organização"""
    try:
        organization = Organization.query.get(organization_id)
        
        if not organization:
            return jsonify({'message': 'Organization not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and current_user.organization_id != organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        org_data = organization.to_dict()
        org_data['active_users_count'] = organization.get_active_users_count()
        org_data['active_certificates_count'] = organization.get_active_certificates_count()
        
        # Adicionar configurações se for admin da organização
        if current_user.is_admin():
            org_data['security_policies'] = organization.get_security_policies()
            org_data['compliance_settings'] = organization.get_compliance_settings()
            org_data['lucia_config'] = organization.get_lucia_config()
            org_data['blockchain_config'] = organization.get_blockchain_config()
        
        return jsonify(org_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar organização: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@organization_bp.route('/', methods=['POST'])
@token_required
@superadmin_required
def create_organization(current_user):
    """Cria uma nova organização (apenas superadmin)"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['name', 'organization_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Field {field} is required'}), 400
        
        # Verificar se CNPJ já existe (se fornecido)
        if data.get('cnpj'):
            existing_org = Organization.query.filter_by(cnpj=data['cnpj']).first()
            if existing_org:
                return jsonify({'message': 'Organization with this CNPJ already exists'}), 400
        
        # Criar organização
        organization = Organization(
            name=data['name'],
            legal_name=data.get('legal_name'),
            cnpj=data.get('cnpj'),
            organization_type=OrganizationType(data['organization_type']),
            email=data.get('email'),
            phone=data.get('phone'),
            website=data.get('website'),
            address_street=data.get('address_street'),
            address_number=data.get('address_number'),
            address_complement=data.get('address_complement'),
            address_neighborhood=data.get('address_neighborhood'),
            address_city=data.get('address_city'),
            address_state=data.get('address_state'),
            address_zipcode=data.get('address_zipcode'),
            max_users=data.get('max_users', 10),
            max_certificates=data.get('max_certificates', 5),
            lucia_enabled=data.get('lucia_enabled', True),
            blockchain_enabled=data.get('blockchain_enabled', True)
        )
        
        db.session.add(organization)
        db.session.flush()  # Para obter o ID
        
        # Registrar criação no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.CONFIGURATION_CHANGE,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=organization.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'organization_created',
                'organization_id': organization.id,
                'organization_name': organization.name,
                'organization_type': organization.organization_type.value,
                'created_by': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar criação de organização no blockchain: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Organization created successfully',
            'organization': organization.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'message': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao criar organização: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@organization_bp.route('/<int:organization_id>', methods=['PUT'])
@token_required
def update_organization(current_user, organization_id):
    """Atualiza uma organização"""
    try:
        organization = Organization.query.get(organization_id)
        
        if not organization:
            return jsonify({'message': 'Organization not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and current_user.organization_id != organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Apenas superadmin pode alterar limites e configurações críticas
        if not current_user.is_superadmin() and not current_user.is_admin():
            return jsonify({'message': 'Admin privileges required'}), 403
        
        data = request.get_json()
        old_data = organization.to_dict()
        
        # Campos que podem ser atualizados
        updatable_fields = [
            'name', 'legal_name', 'email', 'phone', 'website',
            'address_street', 'address_number', 'address_complement',
            'address_neighborhood', 'address_city', 'address_state', 'address_zipcode'
        ]
        
        # Campos que apenas superadmin pode alterar
        superadmin_fields = ['max_users', 'max_certificates', 'active', 'lucia_enabled', 'blockchain_enabled']
        
        for field in updatable_fields:
            if field in data:
                setattr(organization, field, data[field])
        
        if current_user.is_superadmin():
            for field in superadmin_fields:
                if field in data:
                    setattr(organization, field, data[field])
        
        organization.updated_at = datetime.utcnow()
        
        # Registrar alteração no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.CONFIGURATION_CHANGE,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=organization.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'organization_updated',
                'organization_id': organization.id,
                'old_data': old_data,
                'new_data': {field: data[field] for field in data.keys() if field in updatable_fields + superadmin_fields},
                'updated_by': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar atualização de organização no blockchain: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Organization updated successfully',
            'organization': organization.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar organização: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@organization_bp.route('/<int:organization_id>/settings', methods=['GET'])
@token_required
@admin_required
def get_organization_settings(current_user, organization_id):
    """Obtém configurações da organização"""
    try:
        organization = Organization.query.get(organization_id)
        
        if not organization:
            return jsonify({'message': 'Organization not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and current_user.organization_id != organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        settings = OrganizationSettings.query.filter_by(organization_id=organization_id).all()
        
        settings_dict = {}
        for setting in settings:
            settings_dict[setting.setting_key] = setting.get_typed_value()
        
        return jsonify({
            'organization_id': organization_id,
            'settings': settings_dict
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar configurações da organização: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@organization_bp.route('/<int:organization_id>/settings', methods=['POST'])
@token_required
@admin_required
def update_organization_settings(current_user, organization_id):
    """Atualiza configurações da organização"""
    try:
        organization = Organization.query.get(organization_id)
        
        if not organization:
            return jsonify({'message': 'Organization not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and current_user.organization_id != organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        if not data or 'settings' not in data:
            return jsonify({'message': 'Settings data required'}), 400
        
        settings_data = data['settings']
        
        for key, value in settings_data.items():
            # Buscar configuração existente
            setting = OrganizationSettings.query.filter_by(
                organization_id=organization_id,
                setting_key=key
            ).first()
            
            if setting:
                # Atualizar existente
                setting.set_typed_value(value)
                setting.updated_at = datetime.utcnow()
            else:
                # Criar nova
                setting_type = 'string'
                if isinstance(value, bool):
                    setting_type = 'boolean'
                elif isinstance(value, int):
                    setting_type = 'integer'
                elif isinstance(value, (dict, list)):
                    setting_type = 'json'
                
                setting = OrganizationSettings(
                    organization_id=organization_id,
                    setting_key=key,
                    setting_type=setting_type
                )
                setting.set_typed_value(value)
                db.session.add(setting)
        
        # Registrar alteração no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.CONFIGURATION_CHANGE,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=organization_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'organization_settings_updated',
                'organization_id': organization_id,
                'settings_updated': list(settings_data.keys()),
                'updated_by': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar atualização de configurações no blockchain: {str(e)}")
        
        db.session.commit()
        
        return jsonify({'message': 'Settings updated successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar configurações da organização: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@organization_bp.route('/<int:organization_id>/users', methods=['GET'])
@token_required
@admin_required
def get_organization_users(current_user, organization_id):
    """Lista usuários da organização"""
    try:
        organization = Organization.query.get(organization_id)
        
        if not organization:
            return jsonify({'message': 'Organization not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and current_user.organization_id != organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        users = User.query.filter_by(organization_id=organization_id).all()
        
        users_data = []
        for user in users:
            user_data = user.to_dict()
            # Remover informações sensíveis para usuários não-superadmin
            if not current_user.is_superadmin():
                user_data.pop('password_hash', None)
                user_data.pop('mfa_secret', None)
            users_data.append(user_data)
        
        return jsonify({
            'organization_id': organization_id,
            'users': users_data,
            'total': len(users_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar usuários da organização: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@organization_bp.route('/<int:organization_id>/statistics', methods=['GET'])
@token_required
@admin_required
def get_organization_statistics(current_user, organization_id):
    """Obtém estatísticas da organização"""
    try:
        organization = Organization.query.get(organization_id)
        
        if not organization:
            return jsonify({'message': 'Organization not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and current_user.organization_id != organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Estatísticas básicas
        total_users = User.query.filter_by(organization_id=organization_id).count()
        active_users = User.query.filter_by(organization_id=organization_id, status=UserStatus.ACTIVE).count()
        
        from src.models.certificate import Certificate, CertificateStatus
        total_certificates = Certificate.query.filter_by(organization_id=organization_id).count()
        active_certificates = Certificate.query.filter_by(
            organization_id=organization_id, 
            status=CertificateStatus.ACTIVE
        ).count()
        
        # Estatísticas de uso (últimos 30 dias)
        from src.models.certificate import CertificateUsageLog
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_usage = CertificateUsageLog.query.join(Certificate).filter(
            Certificate.organization_id == organization_id,
            CertificateUsageLog.timestamp >= thirty_days_ago
        ).count()
        
        statistics = {
            'organization_id': organization_id,
            'users': {
                'total': total_users,
                'active': active_users,
                'limit': organization.max_users,
                'usage_percentage': (active_users / organization.max_users * 100) if organization.max_users > 0 else 0
            },
            'certificates': {
                'total': total_certificates,
                'active': active_certificates,
                'limit': organization.max_certificates,
                'usage_percentage': (active_certificates / organization.max_certificates * 100) if organization.max_certificates > 0 else 0
            },
            'usage': {
                'last_30_days': recent_usage
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(statistics), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar estatísticas da organização: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

