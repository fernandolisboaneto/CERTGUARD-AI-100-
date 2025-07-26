from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import uuid

from src.database import db
from src.models.user import User
from src.models.blockchain import (
    BlockchainRecord, BlockchainEventType, BlockchainStatus,
    SmartContract, BlockchainNetwork
)
from src.routes.auth import token_required, admin_required, superadmin_required

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/records', methods=['GET'])
@token_required
@admin_required
def list_blockchain_records(current_user):
    """Lista registros blockchain"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Filtros
        event_type = request.args.get('event_type')
        user_id = request.args.get('user_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        status = request.args.get('status')
        
        # Construir query base
        if current_user.is_superadmin():
            query = BlockchainRecord.query
        else:
            query = BlockchainRecord.query.filter_by(organization_id=current_user.organization_id)
        
        # Aplicar filtros
        if event_type:
            try:
                query = query.filter(BlockchainRecord.event_type == BlockchainEventType(event_type))
            except ValueError:
                return jsonify({'message': 'Invalid event type'}), 400
        
        if user_id:
            query = query.filter(BlockchainRecord.user_id == user_id)
        
        if status:
            try:
                query = query.filter(BlockchainRecord.status == BlockchainStatus(status))
            except ValueError:
                return jsonify({'message': 'Invalid status'}), 400
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(BlockchainRecord.created_at >= date_from_obj)
            except ValueError:
                return jsonify({'message': 'Invalid date_from format'}), 400
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(BlockchainRecord.created_at <= date_to_obj)
            except ValueError:
                return jsonify({'message': 'Invalid date_to format'}), 400
        
        # Ordenar por data decrescente
        query = query.order_by(BlockchainRecord.created_at.desc())
        
        # Paginar
        records = query.paginate(page=page, per_page=per_page, error_out=False)
        
        records_data = []
        for record in records.items:
            record_data = record.to_dict()
            # Adicionar informações do usuário se disponível
            if record.user:
                record_data['user_info'] = {
                    'username': record.user.username,
                    'full_name': record.user.full_name
                }
            records_data.append(record_data)
        
        return jsonify({
            'records': records_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': records.total,
                'pages': records.pages,
                'has_next': records.has_next,
                'has_prev': records.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar registros blockchain: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@blockchain_bp.route('/records/<record_id>', methods=['GET'])
@token_required
@admin_required
def get_blockchain_record(current_user, record_id):
    """Obtém detalhes de um registro blockchain"""
    try:
        record = BlockchainRecord.query.filter_by(event_id=record_id).first()
        
        if not record:
            return jsonify({'message': 'Record not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and record.organization_id != current_user.organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        record_data = record.to_dict()
        
        # Adicionar informações adicionais
        if record.user:
            record_data['user_info'] = record.user.to_dict()
        
        if record.certificate:
            record_data['certificate_info'] = record.certificate.to_dict()
        
        # Verificar integridade
        record_data['integrity_check'] = record.verify_integrity()
        record_data['is_confirmed'] = record.is_confirmed()
        
        return jsonify(record_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar registro blockchain: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@blockchain_bp.route('/verify/<record_id>', methods=['POST'])
@token_required
@admin_required
def verify_blockchain_record(current_user, record_id):
    """Verifica integridade de um registro blockchain"""
    try:
        record = BlockchainRecord.query.filter_by(event_id=record_id).first()
        
        if not record:
            return jsonify({'message': 'Record not found'}), 404
        
        # Verificar permissão
        if not current_user.is_superadmin() and record.organization_id != current_user.organization_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Verificar integridade
        integrity_check = record.verify_integrity()
        is_confirmed = record.is_confirmed()
        
        verification_result = {
            'record_id': record_id,
            'event_type': record.event_type.value,
            'integrity_check': integrity_check,
            'is_confirmed': is_confirmed,
            'status': record.status.value,
            'confirmations': record.confirmations,
            'blockchain_hash': record.blockchain_hash,
            'verification_timestamp': datetime.utcnow().isoformat()
        }
        
        # Se há hash blockchain, simular verificação na rede
        if record.blockchain_hash:
            verification_result['blockchain_verification'] = {
                'hash_exists': True,  # Simulação
                'block_number': record.block_number,
                'transaction_confirmed': is_confirmed
            }
        
        return jsonify(verification_result), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar registro blockchain: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@blockchain_bp.route('/statistics', methods=['GET'])
@token_required
@admin_required
def get_blockchain_statistics(current_user):
    """Obtém estatísticas do blockchain"""
    try:
        # Período para estatísticas (padrão: últimos 30 dias)
        days = request.args.get('days', 30, type=int)
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Query base
        if current_user.is_superadmin():
            base_query = BlockchainRecord.query
        else:
            base_query = BlockchainRecord.query.filter_by(organization_id=current_user.organization_id)
        
        # Estatísticas gerais
        total_records = base_query.count()
        recent_records = base_query.filter(BlockchainRecord.created_at >= date_from).count()
        
        # Por status
        confirmed_records = base_query.filter(BlockchainRecord.status == BlockchainStatus.CONFIRMED).count()
        pending_records = base_query.filter(BlockchainRecord.status == BlockchainStatus.PENDING).count()
        failed_records = base_query.filter(BlockchainRecord.status == BlockchainStatus.FAILED).count()
        
        # Por tipo de evento (últimos X dias)
        event_types_stats = {}
        for event_type in BlockchainEventType:
            count = base_query.filter(
                BlockchainRecord.event_type == event_type,
                BlockchainRecord.created_at >= date_from
            ).count()
            event_types_stats[event_type.value] = count
        
        # Estatísticas por dia (últimos 7 dias)
        daily_stats = []
        for i in range(7):
            day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_count = base_query.filter(
                BlockchainRecord.created_at >= day_start,
                BlockchainRecord.created_at < day_end
            ).count()
            
            daily_stats.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': day_count
            })
        
        daily_stats.reverse()  # Ordem cronológica
        
        statistics = {
            'period_days': days,
            'total_records': total_records,
            'recent_records': recent_records,
            'status_distribution': {
                'confirmed': confirmed_records,
                'pending': pending_records,
                'failed': failed_records
            },
            'event_types_distribution': event_types_stats,
            'daily_statistics': daily_stats,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(statistics), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar estatísticas blockchain: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@blockchain_bp.route('/networks', methods=['GET'])
@token_required
@superadmin_required
def list_blockchain_networks(current_user):
    """Lista redes blockchain configuradas (apenas superadmin)"""
    try:
        networks = BlockchainNetwork.query.all()
        
        networks_data = []
        for network in networks:
            network_data = network.to_dict()
            # Remover informações sensíveis
            network_data.pop('admin_cert', None)
            network_data.pop('admin_key', None)
            network_data.pop('ca_cert', None)
            networks_data.append(network_data)
        
        return jsonify({
            'networks': networks_data,
            'total': len(networks_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar redes blockchain: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@blockchain_bp.route('/smart-contracts', methods=['GET'])
@token_required
@superadmin_required
def list_smart_contracts(current_user):
    """Lista smart contracts (apenas superadmin)"""
    try:
        contracts = SmartContract.query.filter_by(active=True).all()
        
        contracts_data = []
        for contract in contracts:
            contract_data = contract.to_dict()
            # Remover código fonte e bytecode para reduzir tamanho da resposta
            contract_data.pop('source_code', None)
            contract_data.pop('bytecode', None)
            contract_data.pop('abi', None)
            contracts_data.append(contract_data)
        
        return jsonify({
            'contracts': contracts_data,
            'total': len(contracts_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar smart contracts: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@blockchain_bp.route('/audit-trail/<entity_type>/<int:entity_id>', methods=['GET'])
@token_required
@admin_required
def get_audit_trail(current_user, entity_type, entity_id):
    """Obtém trilha de auditoria para uma entidade específica"""
    try:
        # Validar tipo de entidade
        valid_entities = ['user', 'certificate', 'organization']
        if entity_type not in valid_entities:
            return jsonify({'message': f'Invalid entity type. Must be one of: {valid_entities}'}), 400
        
        # Construir query baseada no tipo de entidade
        if entity_type == 'user':
            query = BlockchainRecord.query.filter_by(user_id=entity_id)
        elif entity_type == 'certificate':
            query = BlockchainRecord.query.filter_by(certificate_id=entity_id)
        elif entity_type == 'organization':
            query = BlockchainRecord.query.filter_by(organization_id=entity_id)
        
        # Verificar permissão
        if not current_user.is_superadmin():
            query = query.filter_by(organization_id=current_user.organization_id)
        
        # Ordenar por data
        records = query.order_by(BlockchainRecord.created_at.desc()).all()
        
        audit_trail = []
        for record in records:
            record_data = record.to_dict()
            # Adicionar informações contextuais
            if record.user:
                record_data['user_info'] = {
                    'username': record.user.username,
                    'full_name': record.user.full_name
                }
            audit_trail.append(record_data)
        
        return jsonify({
            'entity_type': entity_type,
            'entity_id': entity_id,
            'audit_trail': audit_trail,
            'total_records': len(audit_trail)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar trilha de auditoria: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@blockchain_bp.route('/export', methods=['POST'])
@token_required
@admin_required
def export_blockchain_data(current_user):
    """Exporta dados blockchain para auditoria"""
    try:
        data = request.get_json()
        
        # Parâmetros de exportação
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        event_types = data.get('event_types', [])
        format_type = data.get('format', 'json')  # json, csv
        
        # Construir query
        if current_user.is_superadmin():
            query = BlockchainRecord.query
        else:
            query = BlockchainRecord.query.filter_by(organization_id=current_user.organization_id)
        
        # Aplicar filtros
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(BlockchainRecord.created_at >= date_from_obj)
            except ValueError:
                return jsonify({'message': 'Invalid date_from format'}), 400
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(BlockchainRecord.created_at <= date_to_obj)
            except ValueError:
                return jsonify({'message': 'Invalid date_to format'}), 400
        
        if event_types:
            try:
                event_type_enums = [BlockchainEventType(et) for et in event_types]
                query = query.filter(BlockchainRecord.event_type.in_(event_type_enums))
            except ValueError:
                return jsonify({'message': 'Invalid event type in list'}), 400
        
        # Limitar exportação para evitar sobrecarga
        records = query.order_by(BlockchainRecord.created_at.desc()).limit(10000).all()
        
        if format_type == 'json':
            export_data = {
                'export_info': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'generated_by': current_user.username,
                    'total_records': len(records),
                    'filters': {
                        'date_from': date_from,
                        'date_to': date_to,
                        'event_types': event_types
                    }
                },
                'records': [record.to_dict() for record in records]
            }
            
            return jsonify(export_data), 200
        
        else:
            return jsonify({'message': 'CSV export not implemented yet'}), 501
        
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar dados blockchain: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

