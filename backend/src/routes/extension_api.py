"""
API Backend para comunicação com a extensão CertGuard AI
Endpoints seguros e stateless para autenticação com certificados digitais
"""
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
import hashlib
import hmac
import time
from datetime import datetime, timedelta
import requests
import json
import os

extension_api_bp = Blueprint('extension_api', __name__, url_prefix='/api/extensao')

# Configurações de segurança
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'certguard-ai-secret-key-2024')
NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', 'nvapi-test-key')
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

def require_extension_auth(f):
    """Decorator para validar autenticação da extensão"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verificar header de autorização
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'success': False,
                    'error': 'Token de autorização necessário'
                }), 401
            
            token = auth_header.split(' ')[1]
            
            # Validar JWT
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                request.user_id = payload.get('sub')
                request.user_info = payload
            except jwt.ExpiredSignatureError:
                return jsonify({
                    'success': False,
                    'error': 'Token expirado'
                }), 401
            except jwt.InvalidTokenError:
                return jsonify({
                    'success': False,
                    'error': 'Token inválido'
                }), 401
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro de autenticação: {str(e)}'
            }), 401
    
    return decorated_function

@extension_api_bp.route('/validar', methods=['POST'])
@require_extension_auth
def validate_extension_request():
    """
    Endpoint principal para validação de requisições da extensão
    Determina tipo de certificado e método de autenticação
    """
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['siteUrl', 'hostname', 'timestamp']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório: {field}'
                }), 400
        
        user_id = request.user_id
        site_url = data['siteUrl']
        hostname = data['hostname']
        timestamp = data['timestamp']
        user_agent = data.get('userAgent', 'Unknown')
        geolocation = data.get('geolocation')
        
        # Log de auditoria
        audit_data = {
            'event': 'extension_validation_request',
            'user_id': user_id,
            'site_url': site_url,
            'hostname': hostname,
            'timestamp': timestamp,
            'user_agent': user_agent,
            'geolocation': geolocation,
            'ip_address': request.remote_addr
        }
        log_audit_event(audit_data)
        
        # Verificar se site é homologado
        homologated_sites = [
            'tjrj.jus.br',
            'tjsp.jus.br',
            'trf2.jus.br',
            'pje.jus.br',
            'esaj.tjsp.jus.br',
            'projudi.tjrj.jus.br'
        ]
        
        is_homologated = any(site in hostname for site in homologated_sites)
        
        if not is_homologated:
            return jsonify({
                'success': False,
                'error': 'Site não homologado para autenticação'
            }), 403
        
        # Buscar certificados do usuário
        user_certificates = get_user_certificates(user_id)
        
        if not user_certificates:
            return jsonify({
                'success': False,
                'error': 'Nenhum certificado encontrado para o usuário'
            }), 404
        
        # Determinar melhor certificado para o site
        selected_cert = select_best_certificate(user_certificates, hostname)
        
        if not selected_cert:
            return jsonify({
                'success': False,
                'error': 'Nenhum certificado compatível encontrado'
            }), 404
        
        # Processar autenticação baseada no tipo
        if selected_cert['type'] == 'A1':
            result = process_a1_authentication(user_id, selected_cert, site_url)
        else:
            result = process_a3_authentication(user_id, selected_cert, site_url)
        
        if result['success']:
            # Log de sucesso
            audit_data['event'] = 'authentication_success'
            audit_data['certificate_type'] = selected_cert['type']
            audit_data['certificate_serial'] = selected_cert['serial']
            log_audit_event(audit_data)
            
            return jsonify({
                'success': True,
                'certificateType': selected_cert['type'],
                'certificateInfo': {
                    'type': selected_cert['type'],
                    'owner': selected_cert['owner'],
                    'expiry': selected_cert['expiry'],
                    'serial': selected_cert['serial'],
                    'organization': selected_cert['organization']
                },
                'authMethod': 'hsm' if selected_cert['type'] == 'A1' else 'daemon',
                'sessionId': result['session_id'],
                'signature': result.get('signature'),
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            # Log de falha
            audit_data['event'] = 'authentication_failed'
            audit_data['error'] = result['error']
            log_audit_event(audit_data)
            
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Erro na validação da extensão: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@extension_api_bp.route('/site-detectado', methods=['POST'])
@require_extension_auth
def site_detected():
    """Registra detecção de site homologado pela extensão"""
    try:
        data = request.get_json()
        
        audit_data = {
            'event': 'homologated_site_detected',
            'user_id': request.user_id,
            'site_info': data.get('siteInfo'),
            'tab_id': data.get('tabId'),
            'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
            'ip_address': request.remote_addr
        }
        
        log_audit_event(audit_data)
        
        # Notificar LucIA sobre detecção
        lucia_response = notify_lucia_site_detection(audit_data)
        
        return jsonify({
            'success': True,
            'message': 'Site detectado registrado com sucesso',
            'lucia_analysis': lucia_response
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao registrar detecção de site: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@extension_api_bp.route('/auditoria/evento', methods=['POST'])
@require_extension_auth
def log_audit_event_endpoint():
    """Endpoint para receber eventos de auditoria da extensão"""
    try:
        data = request.get_json()
        
        # Enriquecer dados de auditoria
        audit_data = {
            **data,
            'user_id': request.user_id,
            'ip_address': request.remote_addr,
            'server_timestamp': datetime.utcnow().isoformat()
        }
        
        log_audit_event(audit_data)
        
        # Analisar com LucIA se necessário
        if should_analyze_with_lucia(audit_data):
            lucia_analysis = analyze_with_lucia(audit_data)
            audit_data['lucia_analysis'] = lucia_analysis
        
        return jsonify({
            'success': True,
            'message': 'Evento de auditoria registrado'
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao registrar evento de auditoria: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@extension_api_bp.route('/certificados/<user_id>', methods=['GET'])
@require_extension_auth
def get_user_certificates_endpoint(user_id):
    """Retorna certificados disponíveis para o usuário"""
    try:
        # Verificar se usuário pode acessar estes certificados
        if request.user_id != user_id and not is_admin_user(request.user_id):
            return jsonify({
                'success': False,
                'error': 'Acesso negado'
            }), 403
        
        certificates = get_user_certificates(user_id)
        
        return jsonify({
            'success': True,
            'certificates': certificates,
            'total': len(certificates)
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar certificados: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@extension_api_bp.route('/hsm/assinar', methods=['POST'])
@require_extension_auth
def hsm_sign():
    """Endpoint para assinatura via HSM (certificados A1)"""
    try:
        data = request.get_json()
        
        required_fields = ['certificate_serial', 'data_to_sign', 'algorithm']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório: {field}'
                }), 400
        
        # Validar certificado
        certificate = validate_certificate_access(
            request.user_id, 
            data['certificate_serial']
        )
        
        if not certificate:
            return jsonify({
                'success': False,
                'error': 'Certificado não encontrado ou acesso negado'
            }), 404
        
        # Processar assinatura via HSM
        signature_result = sign_with_hsm(
            certificate['hsm_key_id'],
            data['data_to_sign'],
            data['algorithm']
        )
        
        if signature_result['success']:
            # Log de auditoria
            audit_data = {
                'event': 'hsm_signature_created',
                'user_id': request.user_id,
                'certificate_serial': data['certificate_serial'],
                'algorithm': data['algorithm'],
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': request.remote_addr
            }
            log_audit_event(audit_data)
            
            # Registrar no blockchain
            blockchain_record = {
                'event_type': 'digital_signature',
                'user_id': request.user_id,
                'certificate_serial': data['certificate_serial'],
                'signature_hash': hashlib.sha256(signature_result['signature'].encode()).hexdigest(),
                'timestamp': datetime.utcnow().isoformat()
            }
            register_blockchain_event(blockchain_record)
            
            return jsonify({
                'success': True,
                'signature': signature_result['signature'],
                'certificate_chain': signature_result['certificate_chain'],
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': signature_result['error']
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Erro na assinatura HSM: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@extension_api_bp.route('/daemon/iniciar', methods=['POST'])
@require_extension_auth
def start_daemon():
    """Inicia daemon local para certificados A3"""
    try:
        data = request.get_json()
        
        user_id = request.user_id
        certificate_serial = data.get('certificate_serial')
        
        if not certificate_serial:
            return jsonify({
                'success': False,
                'error': 'Serial do certificado é obrigatório'
            }), 400
        
        # Validar certificado A3
        certificate = validate_certificate_access(user_id, certificate_serial)
        
        if not certificate or certificate['type'] != 'A3':
            return jsonify({
                'success': False,
                'error': 'Certificado A3 não encontrado'
            }), 404
        
        # Gerar comando para daemon local
        daemon_config = generate_daemon_config(user_id, certificate)
        
        # Log de auditoria
        audit_data = {
            'event': 'daemon_start_requested',
            'user_id': user_id,
            'certificate_serial': certificate_serial,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr
        }
        log_audit_event(audit_data)
        
        return jsonify({
            'success': True,
            'daemon_config': daemon_config,
            'message': 'Configuração do daemon gerada'
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao iniciar daemon: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@extension_api_bp.route('/lucia/consultar', methods=['POST'])
@require_extension_auth
def lucia_query():
    """Endpoint para consultas à LucIA sobre auditoria e segurança"""
    try:
        data = request.get_json()
        
        query = data.get('query')
        context = data.get('context', {})
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query é obrigatória'
            }), 400
        
        # Enriquecer contexto com dados do usuário
        context.update({
            'user_id': request.user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr
        })
        
        # Consultar LucIA
        lucia_response = query_lucia_ai(query, context)
        
        # Log da consulta
        audit_data = {
            'event': 'lucia_query',
            'user_id': request.user_id,
            'query': query,
            'response_summary': lucia_response.get('summary', ''),
            'timestamp': datetime.utcnow().isoformat()
        }
        log_audit_event(audit_data)
        
        return jsonify({
            'success': True,
            'response': lucia_response
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro na consulta à LucIA: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# Funções auxiliares

def get_user_certificates(user_id):
    """Busca certificados do usuário no banco de dados"""
    # Simular busca no banco de dados
    # Em produção, fazer query real
    certificates = [
        {
            'id': 'cert-001',
            'serial': 'CG1234567890',
            'type': 'A1',
            'owner': 'João Silva',
            'cpf': '123.456.789-00',
            'organization': 'Silva & Associados',
            'expiry': '2025-12-31',
            'status': 'active',
            'hsm_key_id': 'hsm-key-001',
            'issued_at': '2024-01-15T10:30:00Z'
        },
        {
            'id': 'cert-002',
            'serial': 'CG9876543210',
            'type': 'A3',
            'owner': 'João Silva',
            'cpf': '123.456.789-00',
            'organization': 'Silva & Associados',
            'expiry': '2027-06-10',
            'status': 'active',
            'token_serial': 'TOKEN123456',
            'issued_at': '2024-06-10T14:20:00Z'
        }
    ]
    
    return certificates

def select_best_certificate(certificates, hostname):
    """Seleciona o melhor certificado para o site"""
    # Lógica para selecionar certificado baseado no site
    # Por ora, retornar o primeiro ativo
    for cert in certificates:
        if cert['status'] == 'active':
            return cert
    return None

def process_a1_authentication(user_id, certificate, site_url):
    """Processa autenticação A1 via HSM"""
    try:
        # Simular assinatura via HSM
        session_id = f"a1-sess-{int(time.time())}"
        
        # Em produção, fazer assinatura real via HSM
        signature = sign_with_hsm(
            certificate['hsm_key_id'],
            f"auth-{site_url}-{session_id}",
            'SHA256withRSA'
        )
        
        return {
            'success': True,
            'session_id': session_id,
            'signature': signature.get('signature', 'simulated-signature'),
            'method': 'hsm'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro na autenticação A1: {str(e)}'
        }

def process_a3_authentication(user_id, certificate, site_url):
    """Processa autenticação A3 via daemon local"""
    try:
        session_id = f"a3-sess-{int(time.time())}"
        
        # Gerar configuração para daemon local
        daemon_config = generate_daemon_config(user_id, certificate)
        
        return {
            'success': True,
            'session_id': session_id,
            'daemon_config': daemon_config,
            'method': 'daemon'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro na autenticação A3: {str(e)}'
        }

def sign_with_hsm(key_id, data, algorithm):
    """Simula assinatura via HSM"""
    # Em produção, integrar com HSM real (CloudHSM, SafeSign, etc.)
    return {
        'success': True,
        'signature': f'hsm-signature-{hashlib.sha256(data.encode()).hexdigest()[:16]}',
        'certificate_chain': ['cert1', 'cert2', 'ca-cert'],
        'algorithm': algorithm
    }

def generate_daemon_config(user_id, certificate):
    """Gera configuração para daemon local A3"""
    return {
        'user_id': user_id,
        'certificate_serial': certificate['serial'],
        'token_serial': certificate.get('token_serial'),
        'pkcs11_library': '/usr/lib/libeToken.so',
        'slot_id': 0,
        'timeout': 300,
        'callback_url': f"{request.host_url}api/extensao/daemon/callback"
    }

def validate_certificate_access(user_id, certificate_serial):
    """Valida se usuário tem acesso ao certificado"""
    certificates = get_user_certificates(user_id)
    for cert in certificates:
        if cert['serial'] == certificate_serial:
            return cert
    return None

def is_admin_user(user_id):
    """Verifica se usuário é administrador"""
    # Em produção, verificar no banco de dados
    return user_id in ['admin', 'superadmin']

def log_audit_event(audit_data):
    """Registra evento de auditoria"""
    # Em produção, salvar no banco de dados
    print(f"📝 AUDIT: {json.dumps(audit_data, indent=2)}")
    
    # Registrar no blockchain se evento crítico
    if audit_data.get('event') in ['authentication_success', 'hsm_signature_created']:
        register_blockchain_event(audit_data)

def register_blockchain_event(event_data):
    """Registra evento no blockchain"""
    # Em produção, integrar com Hyperledger Fabric ou similar
    blockchain_record = {
        'block_id': f"block-{int(time.time())}",
        'event_hash': hashlib.sha256(json.dumps(event_data).encode()).hexdigest(),
        'timestamp': datetime.utcnow().isoformat(),
        'data': event_data
    }
    
    print(f"⛓️ BLOCKCHAIN: {json.dumps(blockchain_record, indent=2)}")

def notify_lucia_site_detection(audit_data):
    """Notifica LucIA sobre detecção de site"""
    try:
        query = f"Site {audit_data['site_info']['hostname']} foi detectado pelo usuário {audit_data['user_id']}. Analisar padrão de acesso."
        return query_lucia_ai(query, audit_data)
    except Exception as e:
        print(f"❌ Erro ao notificar LucIA: {str(e)}")
        return None

def should_analyze_with_lucia(audit_data):
    """Determina se evento deve ser analisado pela LucIA"""
    critical_events = [
        'authentication_failed',
        'multiple_failed_attempts',
        'suspicious_ip_access',
        'unusual_time_access'
    ]
    
    return audit_data.get('event') in critical_events

def analyze_with_lucia(audit_data):
    """Analisa evento com LucIA"""
    try:
        query = f"Analisar evento de segurança: {audit_data['event']} para usuário {audit_data['user_id']}"
        return query_lucia_ai(query, audit_data)
    except Exception as e:
        print(f"❌ Erro na análise LucIA: {str(e)}")
        return None

def query_lucia_ai(query, context=None):
    """Consulta a LucIA usando API NVIDIA"""
    try:
        # Preparar prompt para LucIA
        system_prompt = """Você é LucIA, uma IA especializada em segurança digital e auditoria de certificados.
        Analise eventos de segurança, detecte anomalias e forneça insights sobre padrões de acesso.
        Responda de forma concisa e técnica."""
        
        user_prompt = f"Query: {query}"
        if context:
            user_prompt += f"\nContexto: {json.dumps(context, indent=2)}"
        
        # Simular resposta da NVIDIA API
        # Em produção, fazer requisição real
        response = simulate_nvidia_api_response(system_prompt, user_prompt)
        
        return {
            'response': response,
            'timestamp': datetime.utcnow().isoformat(),
            'model': 'meta/llama-3.3-70b-instruct',
            'summary': response[:100] + '...' if len(response) > 100 else response
        }
        
    except Exception as e:
        print(f"❌ Erro na consulta LucIA: {str(e)}")
        return {
            'response': 'Erro na consulta à LucIA',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def simulate_nvidia_api_response(system_prompt, user_prompt):
    """Simula resposta da API NVIDIA"""
    # Em produção, fazer requisição real para NVIDIA API
    responses = [
        "Evento de autenticação analisado. Padrão normal detectado para o usuário.",
        "Alerta: Múltiplas tentativas de acesso detectadas. Recomendo monitoramento adicional.",
        "Site homologado acessado dentro do horário comercial. Comportamento esperado.",
        "Certificado A1 utilizado com sucesso. Assinatura HSM validada.",
        "Daemon A3 iniciado para token físico. Procedimento padrão seguido."
    ]
    
    import random
    return random.choice(responses)

