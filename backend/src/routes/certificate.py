from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import uuid
import hashlib
import json

from src.database import db
from src.models.user import User
from src.models.certificate import Certificate, CertificateType, CertificateStatus, CertificateUsageLog
from src.models.organization import Organization
from src.models.blockchain import BlockchainRecord, BlockchainEventType
from src.routes.auth import token_required, admin_required

certificate_bp = Blueprint('certificate', __name__)

@certificate_bp.route('/', methods=['GET'])
@token_required
def list_certificates(current_user):
    """Lista certificados da organização do usuário"""
    try:
        # Filtrar por organização se não for superadmin
        if current_user.is_superadmin():
            certificates = Certificate.query.all()
        else:
            certificates = Certificate.query.filter_by(organization_id=current_user.organization_id).all()
        
        # Aplicar filtros opcionais
        status_filter = request.args.get('status')
        if status_filter:
            certificates = [cert for cert in certificates if cert.status.value == status_filter]
        
        cert_type_filter = request.args.get('type')
        if cert_type_filter:
            certificates = [cert for cert in certificates if cert.certificate_type.value == cert_type_filter]
        
        # Verificar expiração próxima
        days_to_expire = request.args.get('expires_in_days')
        if days_to_expire:
            try:
                days = int(days_to_expire)
                certificates = [cert for cert in certificates if cert.days_until_expiry() and cert.days_until_expiry() <= days]
            except ValueError:
                pass
        
        certificates_data = []
        for cert in certificates:
            cert_data = cert.to_dict()
            cert_data['days_until_expiry'] = cert.days_until_expiry()
            cert_data['is_valid'] = cert.is_valid()
            certificates_data.append(cert_data)
        
        return jsonify({
            'certificates': certificates_data,
            'total': len(certificates_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar certificados: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@certificate_bp.route('/<int:certificate_id>', methods=['GET'])
@token_required
def get_certificate(current_user, certificate_id):
    """Obtém detalhes de um certificado específico"""
    try:
        certificate = Certificate.query.get(certificate_id)
        
        if not certificate:
            return jsonify({'message': 'Certificate not found'}), 404
        
        # Verificar permissão de acesso
        if not current_user.is_superadmin() and certificate.organization_id != current_user.organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        cert_data = certificate.to_dict()
        cert_data['days_until_expiry'] = certificate.days_until_expiry()
        cert_data['is_valid'] = certificate.is_valid()
        
        # Adicionar logs de uso recentes se for admin
        if current_user.is_admin():
            recent_logs = CertificateUsageLog.query.filter_by(
                certificate_id=certificate_id
            ).order_by(CertificateUsageLog.timestamp.desc()).limit(10).all()
            
            cert_data['recent_usage'] = [log.to_dict() for log in recent_logs]
        
        return jsonify(cert_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar certificado: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@certificate_bp.route('/', methods=['POST'])
@token_required
@admin_required
def create_certificate(current_user):
    """Cria um novo certificado"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['subject_name', 'issuer_name', 'certificate_type', 'valid_from', 'valid_until', 'serial_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Field {field} is required'}), 400
        
        # Verificar se organização pode adicionar mais certificados
        organization = Organization.query.get(current_user.organization_id)
        if not organization.can_add_certificate():
            return jsonify({'message': 'Certificate limit reached for organization'}), 400
        
        # Verificar se serial number já existe
        existing_cert = Certificate.query.filter_by(serial_number=data['serial_number']).first()
        if existing_cert:
            return jsonify({'message': 'Certificate with this serial number already exists'}), 400
        
        # Criar certificado
        certificate = Certificate(
            serial_number=data['serial_number'],
            subject_name=data['subject_name'],
            issuer_name=data['issuer_name'],
            certificate_type=CertificateType(data['certificate_type']),
            valid_from=datetime.fromisoformat(data['valid_from'].replace('Z', '+00:00')),
            valid_until=datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00')),
            organization_id=current_user.organization_id,
            oab_number=data.get('oab_number'),
            cpf_cnpj=data.get('cpf_cnpj'),
            email=data.get('email'),
            thumbprint=data.get('thumbprint'),
            public_key_info=data.get('public_key_info'),
            certificate_policies=data.get('certificate_policies')
        )
        
        # Configurar sites e horários permitidos
        if data.get('allowed_sites'):
            certificate.set_allowed_sites(data['allowed_sites'])
        
        if data.get('allowed_hours'):
            certificate.set_allowed_hours(data['allowed_hours'])
        
        db.session.add(certificate)
        db.session.flush()  # Para obter o ID
        
        # Registrar criação no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.CONFIGURATION_CHANGE,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                certificate_id=certificate.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'certificate_created',
                'certificate_id': certificate.id,
                'serial_number': certificate.serial_number,
                'subject_name': certificate.subject_name,
                'certificate_type': certificate.certificate_type.value,
                'created_by': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar criação de certificado no blockchain: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Certificate created successfully',
            'certificate': certificate.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'message': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao criar certificado: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@certificate_bp.route('/<int:certificate_id>', methods=['PUT'])
@token_required
@admin_required
def update_certificate(current_user, certificate_id):
    """Atualiza um certificado"""
    try:
        certificate = Certificate.query.get(certificate_id)
        
        if not certificate:
            return jsonify({'message': 'Certificate not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and certificate.organization_id != current_user.organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        updatable_fields = ['status', 'oab_number', 'cpf_cnpj', 'email', 'allowed_sites', 'allowed_hours']
        
        old_data = certificate.to_dict()
        
        for field in updatable_fields:
            if field in data:
                if field == 'status':
                    certificate.status = CertificateStatus(data[field])
                elif field == 'allowed_sites':
                    certificate.set_allowed_sites(data[field])
                elif field == 'allowed_hours':
                    certificate.set_allowed_hours(data[field])
                else:
                    setattr(certificate, field, data[field])
        
        certificate.updated_at = datetime.utcnow()
        
        # Registrar alteração no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.CONFIGURATION_CHANGE,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                certificate_id=certificate.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'certificate_updated',
                'certificate_id': certificate.id,
                'serial_number': certificate.serial_number,
                'old_data': old_data,
                'new_data': {field: data[field] for field in updatable_fields if field in data},
                'updated_by': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar atualização de certificado no blockchain: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Certificate updated successfully',
            'certificate': certificate.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'message': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar certificado: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@certificate_bp.route('/<int:certificate_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_certificate(current_user, certificate_id):
    """Remove um certificado"""
    try:
        certificate = Certificate.query.get(certificate_id)
        
        if not certificate:
            return jsonify({'message': 'Certificate not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and certificate.organization_id != current_user.organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        cert_data = certificate.to_dict()
        
        # Registrar remoção no blockchain antes de deletar
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.CONFIGURATION_CHANGE,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                certificate_id=certificate.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'certificate_deleted',
                'certificate_data': cert_data,
                'deleted_by': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar remoção de certificado no blockchain: {str(e)}")
        
        # Remover certificado
        db.session.delete(certificate)
        db.session.commit()
        
        return jsonify({'message': 'Certificate deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover certificado: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@certificate_bp.route('/<int:certificate_id>/validate', methods=['POST'])
@token_required
def validate_certificate(current_user, certificate_id):
    """Valida um certificado"""
    try:
        certificate = Certificate.query.get(certificate_id)
        
        if not certificate:
            return jsonify({'message': 'Certificate not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and certificate.organization_id != current_user.organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Simular validação (em implementação real, seria feita validação com AC)
        validation_result = {
            'certificate_id': certificate.id,
            'serial_number': certificate.serial_number,
            'is_valid': certificate.is_valid(),
            'status': certificate.status.value,
            'days_until_expiry': certificate.days_until_expiry(),
            'validation_timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'validity_period': certificate.valid_from <= datetime.utcnow() <= certificate.valid_until,
                'status_active': certificate.status == CertificateStatus.ACTIVE,
                'not_revoked': certificate.status != CertificateStatus.REVOKED,
                'not_expired': certificate.valid_until > datetime.utcnow()
            }
        }
        
        # Registrar validação no blockchain
        try:
            blockchain_record = BlockchainRecord(
                event_type=BlockchainEventType.CERTIFICATE_ACCESS,
                event_id=str(uuid.uuid4()),
                user_id=current_user.id,
                organization_id=current_user.organization_id,
                certificate_id=certificate.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            event_data = {
                'action': 'certificate_validation',
                'certificate_id': certificate.id,
                'serial_number': certificate.serial_number,
                'validation_result': validation_result,
                'validated_by': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            blockchain_record.set_event_data(event_data)
            db.session.add(blockchain_record)
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar validação no blockchain: {str(e)}")
        
        return jsonify(validation_result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao validar certificado: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@certificate_bp.route('/<int:certificate_id>/usage-logs', methods=['GET'])
@token_required
@admin_required
def get_certificate_usage_logs(current_user, certificate_id):
    """Obtém logs de uso de um certificado"""
    try:
        certificate = Certificate.query.get(certificate_id)
        
        if not certificate:
            return jsonify({'message': 'Certificate not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and certificate.organization_id != current_user.organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Filtros opcionais
        action_filter = request.args.get('action')
        user_filter = request.args.get('user_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Construir query
        query = CertificateUsageLog.query.filter_by(certificate_id=certificate_id)
        
        if action_filter:
            query = query.filter(CertificateUsageLog.action == action_filter)
        
        if user_filter:
            query = query.filter(CertificateUsageLog.user_id == user_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(CertificateUsageLog.timestamp >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(CertificateUsageLog.timestamp <= date_to_obj)
            except ValueError:
                pass
        
        # Ordenar por timestamp decrescente
        query = query.order_by(CertificateUsageLog.timestamp.desc())
        
        # Paginar
        logs = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': logs.total,
                'pages': logs.pages,
                'has_next': logs.has_next,
                'has_prev': logs.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar logs de uso: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@certificate_bp.route('/expiring', methods=['GET'])
@token_required
@admin_required
def get_expiring_certificates(current_user):
    """Lista certificados próximos do vencimento"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Filtrar por organização se não for superadmin
        if current_user.is_superadmin():
            certificates = Certificate.query.filter(
                Certificate.status == CertificateStatus.ACTIVE
            ).all()
        else:
            certificates = Certificate.query.filter(
                Certificate.organization_id == current_user.organization_id,
                Certificate.status == CertificateStatus.ACTIVE
            ).all()
        
        # Filtrar certificados que expiram nos próximos X dias
        expiring_certificates = []
        for cert in certificates:
            days_until_expiry = cert.days_until_expiry()
            if days_until_expiry is not None and 0 <= days_until_expiry <= days:
                cert_data = cert.to_dict()
                cert_data['days_until_expiry'] = days_until_expiry
                expiring_certificates.append(cert_data)
        
        # Ordenar por dias até expiração
        expiring_certificates.sort(key=lambda x: x['days_until_expiry'])
        
        return jsonify({
            'expiring_certificates': expiring_certificates,
            'total': len(expiring_certificates),
            'days_threshold': days
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar certificados expirando: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

