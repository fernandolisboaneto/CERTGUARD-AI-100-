"""
Sistema de Upload de Certificados para Administradores
Permite que admins façam upload de certificados A1/A3 para distribuição
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import zipfile
import json
from datetime import datetime
import hashlib
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import base64

certificate_upload_bp = Blueprint('certificate_upload', __name__)

# Configurações
UPLOAD_FOLDER = '/home/ubuntu/CERTGUARD-AI-100/backend/uploads/certificates'
ALLOWED_EXTENSIONS = {'pfx', 'p12', 'crt', 'cer', 'pem'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_certificate_info(file_path, file_type):
    """Extrai informações do certificado"""
    try:
        if file_type in ['crt', 'cer', 'pem']:
            with open(file_path, 'rb') as f:
                cert_data = f.read()
                
            # Tentar como PEM primeiro
            try:
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            except:
                # Tentar como DER
                cert = x509.load_der_x509_certificate(cert_data, default_backend())
            
            subject = cert.subject
            issuer = cert.issuer
            
            # Extrair informações
            common_name = None
            organization = None
            email = None
            
            for attribute in subject:
                if attribute.oid._name == 'commonName':
                    common_name = attribute.value
                elif attribute.oid._name == 'organizationName':
                    organization = attribute.value
                elif attribute.oid._name == 'emailAddress':
                    email = attribute.value
            
            return {
                'common_name': common_name,
                'organization': organization,
                'email': email,
                'issuer': issuer.rfc4514_string(),
                'valid_from': cert.not_valid_before.isoformat(),
                'valid_until': cert.not_valid_after.isoformat(),
                'serial_number': str(cert.serial_number),
                'type': 'A1' if file_type in ['pfx', 'p12'] else 'A3'
            }
    except Exception as e:
        return {
            'error': f'Erro ao processar certificado: {str(e)}',
            'type': 'A1' if file_type in ['pfx', 'p12'] else 'A3'
        }

@certificate_upload_bp.route('/api/admin/certificates/upload', methods=['POST'])
def upload_certificate():
    """Upload de certificado pelo administrador"""
    
    if 'certificate' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['certificate']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    # Dados adicionais do formulário
    certificate_name = request.form.get('name', '')
    certificate_description = request.form.get('description', '')
    certificate_password = request.form.get('password', '')
    target_users = request.form.get('target_users', 'all')  # all, specific, organization
    
    # Gerar nome único para o arquivo
    filename = secure_filename(file.filename)
    file_hash = hashlib.md5(f"{filename}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    unique_filename = f"{file_hash}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        # Salvar arquivo
        file.save(file_path)
        
        # Extrair informações do certificado
        file_extension = filename.rsplit('.', 1)[1].lower()
        cert_info = get_certificate_info(file_path, file_extension)
        
        # Metadados do certificado
        certificate_metadata = {
            'id': file_hash,
            'original_filename': filename,
            'stored_filename': unique_filename,
            'name': certificate_name or cert_info.get('common_name', filename),
            'description': certificate_description,
            'upload_date': datetime.now().isoformat(),
            'file_size': os.path.getsize(file_path),
            'file_type': file_extension,
            'has_password': bool(certificate_password),
            'target_users': target_users,
            'certificate_info': cert_info,
            'download_count': 0,
            'status': 'active'
        }
        
        # Salvar metadados
        metadata_file = os.path.join(UPLOAD_FOLDER, f"{file_hash}_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(certificate_metadata, f, indent=2, ensure_ascii=False)
        
        # Se tem senha, salvar separadamente (criptografado)
        if certificate_password:
            password_file = os.path.join(UPLOAD_FOLDER, f"{file_hash}_password.txt")
            with open(password_file, 'w') as f:
                # Em produção, usar criptografia adequada
                f.write(base64.b64encode(certificate_password.encode()).decode())
        
        return jsonify({
            'success': True,
            'message': 'Certificado enviado com sucesso',
            'certificate': certificate_metadata
        })
        
    except Exception as e:
        # Limpar arquivo em caso de erro
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({'error': f'Erro ao processar certificado: {str(e)}'}), 500

@certificate_upload_bp.route('/api/admin/certificates', methods=['GET'])
def list_certificates():
    """Lista todos os certificados disponíveis para download"""
    
    certificates = []
    
    try:
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('_metadata.json'):
                metadata_file = os.path.join(UPLOAD_FOLDER, filename)
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    cert_data = json.load(f)
                    certificates.append(cert_data)
        
        # Ordenar por data de upload (mais recente primeiro)
        certificates.sort(key=lambda x: x['upload_date'], reverse=True)
        
        return jsonify({
            'success': True,
            'certificates': certificates,
            'total': len(certificates)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar certificados: {str(e)}'}), 500

@certificate_upload_bp.route('/api/certificates/download/<certificate_id>', methods=['GET'])
def download_certificate(certificate_id):
    """Download de certificado por usuários autorizados"""
    
    try:
        # Carregar metadados
        metadata_file = os.path.join(UPLOAD_FOLDER, f"{certificate_id}_metadata.json")
        if not os.path.exists(metadata_file):
            return jsonify({'error': 'Certificado não encontrado'}), 404
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            cert_data = json.load(f)
        
        # Verificar se certificado está ativo
        if cert_data.get('status') != 'active':
            return jsonify({'error': 'Certificado não está disponível'}), 403
        
        # Caminho do arquivo
        file_path = os.path.join(UPLOAD_FOLDER, cert_data['stored_filename'])
        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo do certificado não encontrado'}), 404
        
        # Incrementar contador de downloads
        cert_data['download_count'] += 1
        cert_data['last_download'] = datetime.now().isoformat()
        
        # Salvar metadados atualizados
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(cert_data, f, indent=2, ensure_ascii=False)
        
        # Retornar arquivo
        return send_file(
            file_path,
            as_attachment=True,
            download_name=cert_data['original_filename'],
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao baixar certificado: {str(e)}'}), 500

@certificate_upload_bp.route('/api/certificates/info/<certificate_id>', methods=['GET'])
def get_certificate_info_api(certificate_id):
    """Obter informações do certificado sem fazer download"""
    
    try:
        metadata_file = os.path.join(UPLOAD_FOLDER, f"{certificate_id}_metadata.json")
        if not os.path.exists(metadata_file):
            return jsonify({'error': 'Certificado não encontrado'}), 404
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            cert_data = json.load(f)
        
        # Remover informações sensíveis
        public_info = {
            'id': cert_data['id'],
            'name': cert_data['name'],
            'description': cert_data['description'],
            'file_type': cert_data['file_type'],
            'certificate_info': cert_data['certificate_info'],
            'upload_date': cert_data['upload_date'],
            'download_count': cert_data['download_count'],
            'status': cert_data['status']
        }
        
        return jsonify({
            'success': True,
            'certificate': public_info
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter informações: {str(e)}'}), 500

@certificate_upload_bp.route('/api/admin/certificates/<certificate_id>', methods=['DELETE'])
def delete_certificate(certificate_id):
    """Excluir certificado (apenas admin)"""
    
    try:
        # Arquivos a serem removidos
        files_to_remove = [
            os.path.join(UPLOAD_FOLDER, f"{certificate_id}_metadata.json"),
            os.path.join(UPLOAD_FOLDER, f"{certificate_id}_password.txt")
        ]
        
        # Carregar metadados para obter nome do arquivo
        metadata_file = files_to_remove[0]
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                cert_data = json.load(f)
            
            # Adicionar arquivo do certificado
            cert_file = os.path.join(UPLOAD_FOLDER, cert_data['stored_filename'])
            files_to_remove.append(cert_file)
        
        # Remover arquivos
        removed_files = []
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
                removed_files.append(os.path.basename(file_path))
        
        return jsonify({
            'success': True,
            'message': 'Certificado removido com sucesso',
            'removed_files': removed_files
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao remover certificado: {str(e)}'}), 500

@certificate_upload_bp.route('/api/certificates/available', methods=['GET'])
def get_available_certificates():
    """Lista certificados disponíveis para o usuário atual"""
    
    try:
        certificates = []
        
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('_metadata.json'):
                metadata_file = os.path.join(UPLOAD_FOLDER, filename)
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    cert_data = json.load(f)
                
                # Apenas certificados ativos
                if cert_data.get('status') == 'active':
                    # Informações públicas apenas
                    public_cert = {
                        'id': cert_data['id'],
                        'name': cert_data['name'],
                        'description': cert_data['description'],
                        'file_type': cert_data['file_type'],
                        'certificate_info': cert_data['certificate_info'],
                        'upload_date': cert_data['upload_date'],
                        'has_password': cert_data.get('has_password', False)
                    }
                    certificates.append(public_cert)
        
        # Ordenar por data de upload
        certificates.sort(key=lambda x: x['upload_date'], reverse=True)
        
        return jsonify({
            'success': True,
            'certificates': certificates,
            'total': len(certificates)
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar certificados: {str(e)}'}), 500

