import os
import sys
from datetime import datetime
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

# Importar instância centralizada do banco
from src.database import db

# Importar todos os modelos DEPOIS de inicializar db
from src.models.user import User, UserRole, UserStatus, UserCertificatePermission
from src.models.organization import Organization, OrganizationType, OrganizationSettings
from src.models.certificate import Certificate, CertificateType, CertificateStatus, CertificateUsageLog
from src.models.lucia import (
    LuciaModel, LuciaModelType, LuciaProviderType,
    LuciaConversation, LuciaMessage, LuciaDocumentAnalysis
)
from src.models.blockchain import (
    BlockchainRecord, BlockchainEventType, BlockchainStatus,
    SmartContract, BlockchainNetwork
)

# Importar rotas
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.certificate import certificate_bp
from src.routes.organization import organization_bp
from src.routes.lucia import lucia_bp
from src.routes.blockchain import blockchain_bp
from src.routes.nvidia_ai import register_nvidia_ai_routes
from src.routes.blockchain_audit import register_blockchain_routes
from src.routes.lucia_advanced import register_lucia_advanced_routes

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = 'certguard_secret_key_2024_secure'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Habilitar CORS para todas as rotas
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(certificate_bp, url_prefix='/api/certificates')
app.register_blueprint(organization_bp, url_prefix='/api/organizations')
app.register_blueprint(lucia_bp, url_prefix='/api/lucia')
app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')

# Registrar rotas avançadas
register_nvidia_ai_routes(app)
register_blockchain_routes(app)
register_lucia_advanced_routes(app)

# Inicializar banco de dados
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health')
def health_check():
    """Endpoint de verificação de saúde do sistema"""
    return {
        'status': 'healthy',
        'service': 'CertGuard System',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
