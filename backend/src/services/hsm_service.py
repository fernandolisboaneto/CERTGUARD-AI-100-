"""
Serviço HSM (Hardware Security Module) para certificados A1
Integração com CloudHSM, SafeSign ou HSM local
"""
import hashlib
import hmac
import base64
import json
import time
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509
import os
import logging

logger = logging.getLogger(__name__)

class HSMService:
    """Serviço para operações com HSM"""
    
    def __init__(self):
        self.hsm_config = {
            'provider': os.environ.get('HSM_PROVIDER', 'CloudHSM'),
            'endpoint': os.environ.get('HSM_ENDPOINT', 'https://hsm.certguard.ai'),
            'cluster_id': os.environ.get('HSM_CLUSTER_ID', 'cluster-001'),
            'user_name': os.environ.get('HSM_USER', 'certguard-user'),
            'password': os.environ.get('HSM_PASSWORD', 'hsm-password'),
            'partition': os.environ.get('HSM_PARTITION', 'partition-1')
        }
        
        self.session_cache = {}
        self.key_cache = {}
        
    def initialize_hsm(self):
        """Inicializa conexão com HSM"""
        try:
            logger.info(f"Inicializando HSM: {self.hsm_config['provider']}")
            
            # Em produção, inicializar conexão real com HSM
            if self.hsm_config['provider'] == 'CloudHSM':
                return self._initialize_cloudhsm()
            elif self.hsm_config['provider'] == 'SafeSign':
                return self._initialize_safesign()
            else:
                return self._initialize_local_hsm()
                
        except Exception as e:
            logger.error(f"Erro ao inicializar HSM: {str(e)}")
            raise HSMException(f"Falha na inicialização do HSM: {str(e)}")
    
    def _initialize_cloudhsm(self):
        """Inicializa CloudHSM da AWS"""
        try:
            # Simular inicialização do CloudHSM
            logger.info("Conectando ao AWS CloudHSM...")
            
            # Em produção, usar boto3 e cloudhsm-client
            session_info = {
                'session_id': f"cloudhsm-{int(time.time())}",
                'cluster_id': self.hsm_config['cluster_id'],
                'status': 'connected',
                'initialized_at': datetime.utcnow().isoformat()
            }
            
            self.session_cache['cloudhsm'] = session_info
            logger.info("CloudHSM inicializado com sucesso")
            
            return session_info
            
        except Exception as e:
            raise HSMException(f"Erro no CloudHSM: {str(e)}")
    
    def _initialize_safesign(self):
        """Inicializa SafeSign HSM"""
        try:
            logger.info("Conectando ao SafeSign HSM...")
            
            # Em produção, usar SDK do SafeSign
            session_info = {
                'session_id': f"safesign-{int(time.time())}",
                'appliance_id': self.hsm_config.get('appliance_id', 'ss-001'),
                'status': 'connected',
                'initialized_at': datetime.utcnow().isoformat()
            }
            
            self.session_cache['safesign'] = session_info
            logger.info("SafeSign HSM inicializado com sucesso")
            
            return session_info
            
        except Exception as e:
            raise HSMException(f"Erro no SafeSign: {str(e)}")
    
    def _initialize_local_hsm(self):
        """Inicializa HSM local (para desenvolvimento)"""
        try:
            logger.info("Inicializando HSM local...")
            
            session_info = {
                'session_id': f"local-hsm-{int(time.time())}",
                'device': '/dev/hsm0',
                'status': 'connected',
                'initialized_at': datetime.utcnow().isoformat()
            }
            
            self.session_cache['local'] = session_info
            logger.info("HSM local inicializado")
            
            return session_info
            
        except Exception as e:
            raise HSMException(f"Erro no HSM local: {str(e)}")
    
    def create_key_pair(self, key_id, key_spec='RSA_2048'):
        """Cria par de chaves no HSM"""
        try:
            logger.info(f"Criando par de chaves: {key_id}")
            
            # Validar especificação da chave
            valid_specs = ['RSA_2048', 'RSA_4096', 'ECC_P256', 'ECC_P384']
            if key_spec not in valid_specs:
                raise HSMException(f"Especificação de chave inválida: {key_spec}")
            
            # Simular criação de chave no HSM
            key_info = {
                'key_id': key_id,
                'key_spec': key_spec,
                'key_usage': 'SIGN_VERIFY',
                'origin': 'HSM',
                'created_at': datetime.utcnow().isoformat(),
                'status': 'enabled',
                'hsm_handle': f"hsm-handle-{hashlib.sha256(key_id.encode()).hexdigest()[:16]}"
            }
            
            # Em produção, fazer criação real no HSM
            if self.hsm_config['provider'] == 'CloudHSM':
                key_info.update(self._create_cloudhsm_key(key_id, key_spec))
            elif self.hsm_config['provider'] == 'SafeSign':
                key_info.update(self._create_safesign_key(key_id, key_spec))
            else:
                key_info.update(self._create_local_key(key_id, key_spec))
            
            # Cache da chave\n            self.key_cache[key_id] = key_info\n            \n            logger.info(f\"Par de chaves criado: {key_id}\")\n            return key_info\n            \n        except Exception as e:\n            logger.error(f\"Erro ao criar chave {key_id}: {str(e)}\")\n            raise HSMException(f\"Falha na criação da chave: {str(e)}\")\n    \n    def _create_cloudhsm_key(self, key_id, key_spec):\n        \"\"\"Cria chave no CloudHSM\"\"\"\n        # Em produção, usar cloudhsm-client\n        return {\n            'aws_key_id': f\"aws-{key_id}\",\n            'cluster_id': self.hsm_config['cluster_id'],\n            'partition': self.hsm_config['partition']\n        }\n    \n    def _create_safesign_key(self, key_id, key_spec):\n        \"\"\"Cria chave no SafeSign\"\"\"\n        # Em produção, usar SDK SafeSign\n        return {\n            'safesign_handle': f\"ss-{key_id}\",\n            'appliance_id': self.hsm_config.get('appliance_id')\n        }\n    \n    def _create_local_key(self, key_id, key_spec):\n        \"\"\"Cria chave no HSM local\"\"\"\n        # Simular criação local\n        return {\n            'local_path': f\"/hsm/keys/{key_id}\",\n            'device': '/dev/hsm0'\n        }\n    \n    def sign_data(self, key_id, data, algorithm='SHA256withRSA'):\n        \"\"\"Assina dados usando chave do HSM\"\"\"\n        try:\n            logger.info(f\"Assinando dados com chave: {key_id}\")\n            \n            # Verificar se chave existe\n            if key_id not in self.key_cache:\n                key_info = self.get_key_info(key_id)\n                if not key_info:\n                    raise HSMException(f\"Chave não encontrada: {key_id}\")\n                self.key_cache[key_id] = key_info\n            \n            key_info = self.key_cache[key_id]\n            \n            # Validar algoritmo\n            valid_algorithms = [\n                'SHA256withRSA', 'SHA384withRSA', 'SHA512withRSA',\n                'SHA256withECDSA', 'SHA384withECDSA'\n            ]\n            \n            if algorithm not in valid_algorithms:\n                raise HSMException(f\"Algoritmo não suportado: {algorithm}\")\n            \n            # Preparar dados para assinatura\n            if isinstance(data, str):\n                data_bytes = data.encode('utf-8')\n            else:\n                data_bytes = data\n            \n            # Hash dos dados\n            if 'SHA256' in algorithm:\n                hash_obj = hashlib.sha256(data_bytes)\n            elif 'SHA384' in algorithm:\n                hash_obj = hashlib.sha384(data_bytes)\n            elif 'SHA512' in algorithm:\n                hash_obj = hashlib.sha512(data_bytes)\n            else:\n                raise HSMException(f\"Hash não suportado no algoritmo: {algorithm}\")\n            \n            data_hash = hash_obj.digest()\n            \n            # Assinar no HSM\n            signature_result = self._perform_hsm_signature(\n                key_info, data_hash, algorithm\n            )\n            \n            # Log de auditoria\n            audit_data = {\n                'event': 'hsm_signature',\n                'key_id': key_id,\n                'algorithm': algorithm,\n                'data_hash': hash_obj.hexdigest(),\n                'signature_id': signature_result['signature_id'],\n                'timestamp': datetime.utcnow().isoformat()\n            }\n            \n            self._log_hsm_operation(audit_data)\n            \n            logger.info(f\"Assinatura criada: {signature_result['signature_id']}\")\n            \n            return {\n                'success': True,\n                'signature': signature_result['signature'],\n                'signature_id': signature_result['signature_id'],\n                'algorithm': algorithm,\n                'key_id': key_id,\n                'timestamp': datetime.utcnow().isoformat(),\n                'certificate_chain': self.get_certificate_chain(key_id)\n            }\n            \n        except Exception as e:\n            logger.error(f\"Erro na assinatura HSM: {str(e)}\")\n            raise HSMException(f\"Falha na assinatura: {str(e)}\")\n    \n    def _perform_hsm_signature(self, key_info, data_hash, algorithm):\n        \"\"\"Executa assinatura no HSM\"\"\"\n        try:\n            # Em produção, fazer assinatura real no HSM\n            if self.hsm_config['provider'] == 'CloudHSM':\n                return self._sign_with_cloudhsm(key_info, data_hash, algorithm)\n            elif self.hsm_config['provider'] == 'SafeSign':\n                return self._sign_with_safesign(key_info, data_hash, algorithm)\n            else:\n                return self._sign_with_local_hsm(key_info, data_hash, algorithm)\n                \n        except Exception as e:\n            raise HSMException(f\"Erro na operação HSM: {str(e)}\")\n    \n    def _sign_with_cloudhsm(self, key_info, data_hash, algorithm):\n        \"\"\"Assina com CloudHSM\"\"\"\n        # Em produção, usar cloudhsm-client\n        signature_id = f\"cloudhsm-sig-{int(time.time())}\"\n        \n        # Simular assinatura\n        signature = base64.b64encode(\n            hashlib.sha256(data_hash + key_info['hsm_handle'].encode()).digest()\n        ).decode('utf-8')\n        \n        return {\n            'signature': signature,\n            'signature_id': signature_id,\n            'hsm_session': self.session_cache.get('cloudhsm', {}).get('session_id')\n        }\n    \n    def _sign_with_safesign(self, key_info, data_hash, algorithm):\n        \"\"\"Assina com SafeSign\"\"\"\n        # Em produção, usar SDK SafeSign\n        signature_id = f\"safesign-sig-{int(time.time())}\"\n        \n        # Simular assinatura\n        signature = base64.b64encode(\n            hashlib.sha256(data_hash + key_info['hsm_handle'].encode()).digest()\n        ).decode('utf-8')\n        \n        return {\n            'signature': signature,\n            'signature_id': signature_id,\n            'appliance_id': key_info.get('appliance_id')\n        }\n    \n    def _sign_with_local_hsm(self, key_info, data_hash, algorithm):\n        \"\"\"Assina com HSM local\"\"\"\n        signature_id = f\"local-sig-{int(time.time())}\"\n        \n        # Simular assinatura local\n        signature = base64.b64encode(\n            hashlib.sha256(data_hash + key_info['hsm_handle'].encode()).digest()\n        ).decode('utf-8')\n        \n        return {\n            'signature': signature,\n            'signature_id': signature_id,\n            'device': key_info.get('device')\n        }\n    \n    def verify_signature(self, key_id, data, signature, algorithm='SHA256withRSA'):\n        \"\"\"Verifica assinatura usando chave do HSM\"\"\"\n        try:\n            logger.info(f\"Verificando assinatura com chave: {key_id}\")\n            \n            # Buscar informações da chave\n            key_info = self.get_key_info(key_id)\n            if not key_info:\n                raise HSMException(f\"Chave não encontrada: {key_id}\")\n            \n            # Preparar dados\n            if isinstance(data, str):\n                data_bytes = data.encode('utf-8')\n            else:\n                data_bytes = data\n            \n            # Hash dos dados\n            if 'SHA256' in algorithm:\n                data_hash = hashlib.sha256(data_bytes).digest()\n            elif 'SHA384' in algorithm:\n                data_hash = hashlib.sha384(data_bytes).digest()\n            elif 'SHA512' in algorithm:\n                data_hash = hashlib.sha512(data_bytes).digest()\n            else:\n                raise HSMException(f\"Hash não suportado: {algorithm}\")\n            \n            # Verificar no HSM\n            verification_result = self._perform_hsm_verification(\n                key_info, data_hash, signature, algorithm\n            )\n            \n            logger.info(f\"Verificação concluída: {verification_result['valid']}\")\n            \n            return {\n                'success': True,\n                'valid': verification_result['valid'],\n                'key_id': key_id,\n                'algorithm': algorithm,\n                'timestamp': datetime.utcnow().isoformat()\n            }\n            \n        except Exception as e:\n            logger.error(f\"Erro na verificação: {str(e)}\")\n            raise HSMException(f\"Falha na verificação: {str(e)}\")\n    \n    def _perform_hsm_verification(self, key_info, data_hash, signature, algorithm):\n        \"\"\"Executa verificação no HSM\"\"\"\n        try:\n            # Simular verificação\n            # Em produção, usar HSM real\n            expected_signature = base64.b64encode(\n                hashlib.sha256(data_hash + key_info['hsm_handle'].encode()).digest()\n            ).decode('utf-8')\n            \n            is_valid = (signature == expected_signature)\n            \n            return {\n                'valid': is_valid,\n                'verification_id': f\"verify-{int(time.time())}\"\n            }\n            \n        except Exception as e:\n            raise HSMException(f\"Erro na verificação HSM: {str(e)}\")\n    \n    def get_key_info(self, key_id):\n        \"\"\"Busca informações da chave no HSM\"\"\"\n        try:\n            # Verificar cache primeiro\n            if key_id in self.key_cache:\n                return self.key_cache[key_id]\n            \n            # Buscar no HSM\n            # Em produção, fazer query real\n            key_info = {\n                'key_id': key_id,\n                'key_spec': 'RSA_2048',\n                'key_usage': 'SIGN_VERIFY',\n                'status': 'enabled',\n                'created_at': '2024-01-15T10:30:00Z',\n                'hsm_handle': f\"hsm-handle-{hashlib.sha256(key_id.encode()).hexdigest()[:16]}\"\n            }\n            \n            # Adicionar ao cache\n            self.key_cache[key_id] = key_info\n            \n            return key_info\n            \n        except Exception as e:\n            logger.error(f\"Erro ao buscar chave {key_id}: {str(e)}\")\n            return None\n    \n    def get_certificate_chain(self, key_id):\n        \"\"\"Retorna cadeia de certificados para a chave\"\"\"\n        try:\n            # Em produção, buscar cadeia real do HSM\n            return [\n                f\"-----BEGIN CERTIFICATE-----\\nMIIC...{key_id}...\\n-----END CERTIFICATE-----\",\n                \"-----BEGIN CERTIFICATE-----\\nMIIC...intermediate...\\n-----END CERTIFICATE-----\",\n                \"-----BEGIN CERTIFICATE-----\\nMIIC...root...\\n-----END CERTIFICATE-----\"\n            ]\n            \n        except Exception as e:\n            logger.error(f\"Erro ao buscar cadeia de certificados: {str(e)}\")\n            return []\n    \n    def list_keys(self, filter_params=None):\n        \"\"\"Lista chaves disponíveis no HSM\"\"\"\n        try:\n            # Em produção, listar chaves reais do HSM\n            keys = [\n                {\n                    'key_id': 'hsm-key-001',\n                    'key_spec': 'RSA_2048',\n                    'status': 'enabled',\n                    'created_at': '2024-01-15T10:30:00Z'\n                },\n                {\n                    'key_id': 'hsm-key-002',\n                    'key_spec': 'RSA_4096',\n                    'status': 'enabled',\n                    'created_at': '2024-02-10T14:20:00Z'\n                }\n            ]\n            \n            # Aplicar filtros se fornecidos\n            if filter_params:\n                filtered_keys = []\n                for key in keys:\n                    match = True\n                    for param, value in filter_params.items():\n                        if key.get(param) != value:\n                            match = False\n                            break\n                    if match:\n                        filtered_keys.append(key)\n                return filtered_keys\n            \n            return keys\n            \n        except Exception as e:\n            logger.error(f\"Erro ao listar chaves: {str(e)}\")\n            return []\n    \n    def delete_key(self, key_id):\n        \"\"\"Remove chave do HSM\"\"\"\n        try:\n            logger.info(f\"Removendo chave: {key_id}\")\n            \n            # Verificar se chave existe\n            key_info = self.get_key_info(key_id)\n            if not key_info:\n                raise HSMException(f\"Chave não encontrada: {key_id}\")\n            \n            # Remover do HSM\n            # Em produção, fazer remoção real\n            \n            # Remover do cache\n            if key_id in self.key_cache:\n                del self.key_cache[key_id]\n            \n            # Log de auditoria\n            audit_data = {\n                'event': 'hsm_key_deleted',\n                'key_id': key_id,\n                'timestamp': datetime.utcnow().isoformat()\n            }\n            \n            self._log_hsm_operation(audit_data)\n            \n            logger.info(f\"Chave removida: {key_id}\")\n            \n            return {\n                'success': True,\n                'message': f\"Chave {key_id} removida com sucesso\"\n            }\n            \n        except Exception as e:\n            logger.error(f\"Erro ao remover chave {key_id}: {str(e)}\")\n            raise HSMException(f\"Falha na remoção da chave: {str(e)}\")\n    \n    def get_hsm_status(self):\n        \"\"\"Retorna status do HSM\"\"\"\n        try:\n            status = {\n                'provider': self.hsm_config['provider'],\n                'status': 'healthy',\n                'sessions': len(self.session_cache),\n                'cached_keys': len(self.key_cache),\n                'last_check': datetime.utcnow().isoformat()\n            }\n            \n            # Verificar conectividade específica do provider\n            if self.hsm_config['provider'] == 'CloudHSM':\n                status.update({\n                    'cluster_id': self.hsm_config['cluster_id'],\n                    'partition': self.hsm_config['partition']\n                })\n            elif self.hsm_config['provider'] == 'SafeSign':\n                status.update({\n                    'appliance_id': self.hsm_config.get('appliance_id')\n                })\n            \n            return status\n            \n        except Exception as e:\n            logger.error(f\"Erro ao verificar status HSM: {str(e)}\")\n            return {\n                'provider': self.hsm_config['provider'],\n                'status': 'error',\n                'error': str(e),\n                'last_check': datetime.utcnow().isoformat()\n            }\n    \n    def _log_hsm_operation(self, audit_data):\n        \"\"\"Log de operações HSM para auditoria\"\"\"\n        try:\n            # Em produção, salvar em sistema de auditoria\n            logger.info(f\"HSM AUDIT: {json.dumps(audit_data)}\")\n            \n            # Registrar no blockchain se operação crítica\n            critical_events = ['hsm_signature', 'hsm_key_created', 'hsm_key_deleted']\n            if audit_data.get('event') in critical_events:\n                # Integrar com blockchain\n                pass\n                \n        except Exception as e:\n            logger.error(f\"Erro no log de auditoria HSM: {str(e)}\")\n    \n    def cleanup_sessions(self):\n        \"\"\"Limpa sessões expiradas\"\"\"\n        try:\n            current_time = datetime.utcnow()\n            expired_sessions = []\n            \n            for session_id, session_info in self.session_cache.items():\n                # Verificar se sessão expirou (exemplo: 1 hora)\n                session_time = datetime.fromisoformat(\n                    session_info['initialized_at'].replace('Z', '+00:00')\n                )\n                \n                if (current_time - session_time.replace(tzinfo=None)) > timedelta(hours=1):\n                    expired_sessions.append(session_id)\n            \n            # Remover sessões expiradas\n            for session_id in expired_sessions:\n                del self.session_cache[session_id]\n                logger.info(f\"Sessão HSM expirada removida: {session_id}\")\n            \n            return {\n                'cleaned_sessions': len(expired_sessions),\n                'active_sessions': len(self.session_cache)\n            }\n            \n        except Exception as e:\n            logger.error(f\"Erro na limpeza de sessões: {str(e)}\")\n            return {'error': str(e)}\n\nclass HSMException(Exception):\n    \"\"\"Exceção específica para operações HSM\"\"\"\n    pass\n\n# Instância global do serviço HSM\nhsm_service = HSMService()

