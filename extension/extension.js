// CertGuard AI - Extensão para Navegador
// Manifest V3 Extension for Chrome/Edge

// Background Service Worker
class CertGuardExtension {
    constructor() {
        this.isActive = false;
        this.certificates = [];
        this.currentSite = null;
        this.autoLogin = false;
    }

    // Inicializar extensão
    init() {
        console.log('CertGuard AI Extension iniciada');
        this.loadCertificates();
        this.setupEventListeners();
        this.detectTribunalSite();
    }

    // Carregar certificados disponíveis
    loadCertificates() {
        // Simular carregamento de certificados A1/A3
        this.certificates = [
            {
                id: 1,
                name: "João Silva Santos",
                type: "A3",
                cpf: "123.456.789-01",
                organization: "Escritório Silva & Associados",
                device: "Token SafeNet",
                status: "Ativo"
            },
            {
                id: 2,
                name: "Maria Costa Oliveira",
                type: "A1",
                cpf: "987.654.321-09",
                organization: "Advocacia Costa",
                device: "Arquivo .pfx",
                status: "Ativo"
            }
        ];
    }

    // Detectar site de tribunal
    detectTribunalSite() {
        const hostname = window.location.hostname;
        const tribunalSites = {
            'tjrj.jus.br': 'TJ-RJ',
            'tjsp.jus.br': 'TJSP',
            'trf2.jus.br': 'TRF-2',
            'pje.jus.br': 'PJe',
            'esaj.tjsp.jus.br': 'E-SAJ',
            'projudi.tjrj.jus.br': 'PROJUDI'
        };

        for (const [domain, name] of Object.entries(tribunalSites)) {
            if (hostname.includes(domain)) {
                this.currentSite = name;
                this.showTribunalDetected(name);
                break;
            }
        }
    }

    // Mostrar notificação de tribunal detectado
    showTribunalDetected(tribunalName) {
        const notification = document.createElement('div');
        notification.id = 'certguard-notification';
        notification.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 350px;
                animation: slideIn 0.3s ease-out;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="
                        width: 24px;
                        height: 24px;
                        background: rgba(255,255,255,0.2);
                        border-radius: 6px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                    ">
                        🛡️
                    </div>
                    <strong style="font-size: 14px;">CertGuard AI Detectado</strong>
                </div>
                <div style="font-size: 13px; opacity: 0.9; margin-bottom: 12px;">
                    Tribunal: <strong>${tribunalName}</strong><br>
                    Certificados disponíveis: ${this.certificates.length}
                </div>
                <div style="display: flex; gap: 8px;">
                    <button id="certguard-auto-login" style="
                        background: rgba(255,255,255,0.2);
                        border: 1px solid rgba(255,255,255,0.3);
                        color: white;
                        padding: 6px 12px;
                        border-radius: 6px;
                        font-size: 12px;
                        cursor: pointer;
                        transition: all 0.2s;
                    ">
                        🔐 Auto Login
                    </button>
                    <button id="certguard-select-cert" style="
                        background: rgba(255,255,255,0.2);
                        border: 1px solid rgba(255,255,255,0.3);
                        color: white;
                        padding: 6px 12px;
                        border-radius: 6px;
                        font-size: 12px;
                        cursor: pointer;
                        transition: all 0.2s;
                    ">
                        📋 Selecionar Certificado
                    </button>
                    <button id="certguard-close" style="
                        background: transparent;
                        border: none;
                        color: white;
                        padding: 6px;
                        border-radius: 6px;
                        font-size: 16px;
                        cursor: pointer;
                        opacity: 0.7;
                    ">
                        ✕
                    </button>
                </div>
            </div>
            <style>
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            </style>
        `;

        document.body.appendChild(notification);

        // Event listeners para os botões
        document.getElementById('certguard-auto-login').addEventListener('click', () => {
            this.performAutoLogin();
        });

        document.getElementById('certguard-select-cert').addEventListener('click', () => {
            this.showCertificateSelector();
        });

        document.getElementById('certguard-close').addEventListener('click', () => {
            notification.remove();
        });

        // Auto-remover após 10 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }

    // Realizar login automático
    performAutoLogin() {
        console.log('Iniciando auto login...');
        
        // Simular processo de login automático
        const loginSteps = [
            'Detectando campos de login...',
            'Selecionando certificado A3...',
            'Validando certificado...',
            'Preenchendo credenciais...',
            'Enviando formulário...',
            'Login realizado com sucesso!'
        ];

        let currentStep = 0;
        const progressNotification = this.showProgressNotification('Auto Login em Progresso');

        const interval = setInterval(() => {
            if (currentStep < loginSteps.length) {
                this.updateProgressNotification(progressNotification, loginSteps[currentStep], (currentStep + 1) / loginSteps.length * 100);
                currentStep++;
            } else {
                clearInterval(interval);
                setTimeout(() => {
                    progressNotification.remove();
                    this.showSuccessNotification('Login realizado com sucesso!');
                }, 1000);
            }
        }, 800);
    }

    // Mostrar seletor de certificados
    showCertificateSelector() {
        const modal = document.createElement('div');
        modal.id = 'certguard-modal';
        modal.innerHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 10001;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            ">
                <div style="
                    background: white;
                    border-radius: 16px;
                    padding: 24px;
                    max-width: 500px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                ">
                    <div style="display: flex; align-items: center; justify-content: between; margin-bottom: 20px;">
                        <h2 style="margin: 0; color: #1f2937; font-size: 18px; font-weight: 600;">
                            🛡️ Selecionar Certificado Digital
                        </h2>
                        <button id="modal-close" style="
                            background: none;
                            border: none;
                            font-size: 20px;
                            cursor: pointer;
                            color: #6b7280;
                            margin-left: auto;
                        ">✕</button>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <p style="color: #6b7280; font-size: 14px; margin: 0;">
                            Tribunal detectado: <strong>${this.currentSite}</strong>
                        </p>
                    </div>

                    <div style="space-y: 12px;">
                        ${this.certificates.map((cert, index) => `
                            <div class="cert-option" data-cert-id="${cert.id}" style="
                                border: 2px solid #e5e7eb;
                                border-radius: 12px;
                                padding: 16px;
                                cursor: pointer;
                                transition: all 0.2s;
                                margin-bottom: 12px;
                            ">
                                <div style="display: flex; align-items: center;">
                                    <div style="
                                        width: 40px;
                                        height: 40px;
                                        background: ${cert.type === 'A3' ? '#3b82f6' : '#10b981'};
                                        border-radius: 8px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        margin-right: 12px;
                                    ">
                                        <span style="color: white; font-weight: bold; font-size: 12px;">
                                            ${cert.type}
                                        </span>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; color: #1f2937; font-size: 14px;">
                                            ${cert.name}
                                        </div>
                                        <div style="color: #6b7280; font-size: 12px;">
                                            CPF: ${cert.cpf} • ${cert.organization}
                                        </div>
                                        <div style="color: #6b7280; font-size: 11px;">
                                            ${cert.device} • Status: ${cert.status}
                                        </div>
                                    </div>
                                    <div style="
                                        width: 20px;
                                        height: 20px;
                                        border: 2px solid #d1d5db;
                                        border-radius: 50%;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                    ">
                                        <div style="
                                            width: 10px;
                                            height: 10px;
                                            background: #3b82f6;
                                            border-radius: 50%;
                                            display: none;
                                        " class="radio-dot"></div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>

                    <div style="margin-top: 20px; display: flex; gap: 12px;">
                        <button id="use-certificate" style="
                            flex: 1;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            padding: 12px 20px;
                            border-radius: 8px;
                            font-weight: 600;
                            cursor: pointer;
                            font-size: 14px;
                        ">
                            Usar Certificado Selecionado
                        </button>
                        <button id="cancel-selection" style="
                            background: #f3f4f6;
                            color: #374151;
                            border: none;
                            padding: 12px 20px;
                            border-radius: 8px;
                            font-weight: 600;
                            cursor: pointer;
                            font-size: 14px;
                        ">
                            Cancelar
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Event listeners
        let selectedCert = null;

        modal.querySelectorAll('.cert-option').forEach(option => {
            option.addEventListener('click', () => {
                // Remover seleção anterior
                modal.querySelectorAll('.cert-option').forEach(opt => {
                    opt.style.borderColor = '#e5e7eb';
                    opt.querySelector('.radio-dot').style.display = 'none';
                });

                // Selecionar atual
                option.style.borderColor = '#3b82f6';
                option.querySelector('.radio-dot').style.display = 'block';
                selectedCert = option.dataset.certId;
            });
        });

        document.getElementById('modal-close').addEventListener('click', () => modal.remove());
        document.getElementById('cancel-selection').addEventListener('click', () => modal.remove());
        
        document.getElementById('use-certificate').addEventListener('click', () => {
            if (selectedCert) {
                modal.remove();
                this.useCertificate(selectedCert);
            } else {
                alert('Por favor, selecione um certificado.');
            }
        });

        // Fechar modal clicando fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    // Usar certificado selecionado
    useCertificate(certId) {
        const cert = this.certificates.find(c => c.id == certId);
        if (cert) {
            console.log('Usando certificado:', cert);
            this.showSuccessNotification(`Certificado ${cert.type} de ${cert.name} selecionado!`);
            this.performAutoLogin();
        }
    }

    // Mostrar notificação de progresso
    showProgressNotification(title) {
        const notification = document.createElement('div');
        notification.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border: 1px solid #e5e7eb;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 350px;
                min-width: 300px;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <div style="
                        width: 24px;
                        height: 24px;
                        background: #3b82f6;
                        border-radius: 6px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                    ">
                        🔄
                    </div>
                    <strong style="font-size: 14px; color: #1f2937;">${title}</strong>
                </div>
                <div id="progress-text" style="font-size: 13px; color: #6b7280; margin-bottom: 12px;">
                    Iniciando...
                </div>
                <div style="background: #f3f4f6; border-radius: 8px; height: 6px; overflow: hidden;">
                    <div id="progress-bar" style="
                        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                        height: 100%;
                        width: 0%;
                        transition: width 0.3s ease;
                    "></div>
                </div>
            </div>
        `;

        document.body.appendChild(notification);
        return notification;
    }

    // Atualizar notificação de progresso
    updateProgressNotification(notification, text, progress) {
        const progressText = notification.querySelector('#progress-text');
        const progressBar = notification.querySelector('#progress-bar');
        
        if (progressText) progressText.textContent = text;
        if (progressBar) progressBar.style.width = progress + '%';
    }

    // Mostrar notificação de sucesso
    showSuccessNotification(message) {
        const notification = document.createElement('div');
        notification.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 350px;
                animation: slideIn 0.3s ease-out;
            ">
                <div style="display: flex; align-items: center;">
                    <div style="
                        width: 24px;
                        height: 24px;
                        background: rgba(255,255,255,0.2);
                        border-radius: 6px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 12px;
                    ">
                        ✅
                    </div>
                    <div style="font-size: 14px; font-weight: 500;">
                        ${message}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Configurar event listeners
    setupEventListeners() {
        // Detectar mudanças de página
        let currentUrl = window.location.href;
        setInterval(() => {
            if (window.location.href !== currentUrl) {
                currentUrl = window.location.href;
                this.detectTribunalSite();
            }
        }, 1000);

        // Atalhos de teclado
        document.addEventListener('keydown', (e) => {
            // Ctrl + Shift + C = Abrir seletor de certificados
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                this.showCertificateSelector();
            }

            // Ctrl + Shift + L = Auto login
            if (e.ctrlKey && e.shiftKey && e.key === 'L') {
                e.preventDefault();
                this.performAutoLogin();
            }
        });
    }
}

// Inicializar extensão quando a página carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const extension = new CertGuardExtension();
        extension.init();
    });
} else {
    const extension = new CertGuardExtension();
    extension.init();
}

// Exportar para uso global
window.CertGuardExtension = CertGuardExtension;

