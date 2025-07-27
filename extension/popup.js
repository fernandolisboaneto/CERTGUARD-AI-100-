// Popup JavaScript para CertGuard AI Extension

class CertGuardPopup {
    constructor() {
        this.apiBase = 'https://8081-ick1rotydcjwas9kzjqp5-50bdaabf.manusvm.computer';
        this.certificates = [];
        this.currentSite = null;
        this.settings = {
            autoLogin: false,
            autoCapture: false,
            notifications: true
        };
        
        this.init();
    }
    
    async init() {
        await this.loadSettings();
        await this.detectCurrentSite();
        await this.loadCertificates();
        this.setupEventListeners();
        this.updateUI();
    }
    
    async loadSettings() {
        try {
            const result = await chrome.storage.sync.get(['certguard_settings']);
            if (result.certguard_settings) {
                this.settings = { ...this.settings, ...result.certguard_settings };
            }
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
        }
    }
    
    async saveSettings() {
        try {
            await chrome.storage.sync.set({ certguard_settings: this.settings });
        } catch (error) {
            console.error('Erro ao salvar configurações:', error);
        }
    }
    
    async detectCurrentSite() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            const url = tab.url;
            
            const tribunals = {
                'tjrj.jus.br': { name: 'TJ-RJ', fullName: 'Tribunal de Justiça do Rio de Janeiro' },
                'tjsp.jus.br': { name: 'TJSP', fullName: 'Tribunal de Justiça de São Paulo' },
                'trf2.jus.br': { name: 'TRF-2', fullName: 'Tribunal Regional Federal da 2ª Região' },
                'pje.jus.br': { name: 'PJe', fullName: 'Processo Judicial Eletrônico' },
                'esaj.tjsp.jus.br': { name: 'E-SAJ', fullName: 'Sistema de Automação da Justiça' },
                'projudi.tjrj.jus.br': { name: 'PROJUDI', fullName: 'Processo Judicial Digital' }
            };
            
            for (const [domain, info] of Object.entries(tribunals)) {
                if (url.includes(domain)) {
                    this.currentSite = {
                        domain,
                        ...info,
                        url,
                        detected: true
                    };
                    break;
                }
            }
            
            if (!this.currentSite) {
                this.currentSite = {
                    name: 'Site Não Reconhecido',
                    fullName: 'Site não é um tribunal conhecido',
                    detected: false
                };
            }
        } catch (error) {
            console.error('Erro ao detectar site:', error);
            this.currentSite = {
                name: 'Erro',
                fullName: 'Erro ao detectar site atual',
                detected: false
            };
        }
    }
    
    async loadCertificates() {
        const loadingElement = document.getElementById('loadingCerts');
        loadingElement.style.display = 'block';
        
        try {
            // Simular certificados disponíveis (em produção, buscar da API)
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            this.certificates = [
                {
                    id: 'cert_001',
                    name: 'João Silva - Advogado',
                    type: 'A1',
                    organization: 'OAB-RJ',
                    validUntil: '2025-12-31',
                    size: '2.1 MB'
                },
                {
                    id: 'cert_002',
                    name: 'Maria Santos - Empresa',
                    type: 'A3',
                    organization: 'Santos & Associados',
                    validUntil: '2026-06-15',
                    size: '1.8 MB'
                },
                {
                    id: 'cert_003',
                    name: 'Carlos Pereira - PF',
                    type: 'A1',
                    organization: 'Pessoa Física',
                    validUntil: '2025-09-20',
                    size: '1.9 MB'
                }
            ];
            
            this.displayCertificates();
            
        } catch (error) {
            console.error('Erro ao carregar certificados:', error);
            this.showError('Erro ao carregar certificados');
        } finally {
            loadingElement.style.display = 'none';
        }
    }
    
    displayCertificates() {
        const container = document.getElementById('certificatesList');
        const loadingElement = document.getElementById('loadingCerts');
        
        // Remover loading se ainda estiver visível
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        if (this.certificates.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 20px; opacity: 0.7;">
                    <div style="font-size: 24px; margin-bottom: 8px;">📭</div>
                    <div style="font-size: 12px;">Nenhum certificado disponível</div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.certificates.map(cert => `
            <div class="certificate-item" data-cert-id="${cert.id}">
                <div class="cert-name">${cert.name}</div>
                <div class="cert-details">
                    <span>${cert.type} • ${cert.organization}</span>
                    <span>${cert.size}</span>
                </div>
            </div>
        `).join('');
        
        // Adicionar event listeners para certificados
        container.querySelectorAll('.certificate-item').forEach(item => {
            item.addEventListener('click', () => {
                const certId = item.dataset.certId;
                this.downloadCertificate(certId);
            });
        });
    }
    
    async downloadCertificate(certId) {
        const cert = this.certificates.find(c => c.id === certId);
        if (!cert) return;
        
        try {
            this.showNotification(`Baixando ${cert.name}...`);
            
            // Simular download (em produção, usar API real)
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Usar Chrome Downloads API
            const downloadUrl = `${this.apiBase}/api/certificates/download/${certId}`;
            
            await chrome.downloads.download({
                url: downloadUrl,
                filename: `${cert.name.replace(/[^a-zA-Z0-9]/g, '_')}_${cert.type}.pfx`,
                saveAs: true
            });
            
            this.showNotification(`${cert.name} baixado com sucesso!`);
            
            // Registrar evento de download
            this.logSecurityEvent('certificate_download', {
                certificate_id: certId,
                certificate_name: cert.name
            });
            
        } catch (error) {
            console.error('Erro ao baixar certificado:', error);
            this.showNotification('Erro ao baixar certificado', 'error');
        }
    }
    
    setupEventListeners() {
        // Botões de ação
        document.getElementById('autoLoginBtn').addEventListener('click', () => {
            this.performAutoLogin();
        });
        
        document.getElementById('captureBtn').addEventListener('click', () => {
            this.captureScreen();
        });
        
        document.getElementById('dashboardBtn').addEventListener('click', () => {
            this.openDashboard();
        });
        
        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.openDownloads();
        });
        
        // Toggles de configuração
        document.getElementById('autoLoginToggle').addEventListener('click', () => {
            this.toggleSetting('autoLogin');
        });
        
        document.getElementById('autoCaptureToggle').addEventListener('click', () => {
            this.toggleSetting('autoCapture');
        });
        
        document.getElementById('notificationsToggle').addEventListener('click', () => {
            this.toggleSetting('notifications');
        });
        
        // Links do footer
        document.getElementById('helpLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.openHelp();
        });
        
        document.getElementById('configLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.openConfig();
        });
        
        document.getElementById('aboutLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.openAbout();
        });
    }
    
    updateUI() {
        // Atualizar status do site
        const statusIcon = document.getElementById('siteStatusIcon');
        const statusTitle = document.getElementById('siteStatusTitle');
        const statusDesc = document.getElementById('siteStatusDesc');
        
        if (this.currentSite.detected) {
            statusIcon.textContent = '✅';
            statusIcon.className = 'status-icon success';
            statusTitle.textContent = this.currentSite.name;
            statusDesc.textContent = this.currentSite.fullName;
        } else {
            statusIcon.textContent = '⚠️';
            statusIcon.className = 'status-icon warning';
            statusTitle.textContent = this.currentSite.name;
            statusDesc.textContent = this.currentSite.fullName;
        }
        
        // Atualizar toggles
        this.updateToggle('autoLoginToggle', this.settings.autoLogin);
        this.updateToggle('autoCaptureToggle', this.settings.autoCapture);
        this.updateToggle('notificationsToggle', this.settings.notifications);
    }
    
    updateToggle(toggleId, active) {
        const toggle = document.getElementById(toggleId);
        if (active) {
            toggle.classList.add('active');
        } else {
            toggle.classList.remove('active');
        }
    }
    
    toggleSetting(setting) {
        this.settings[setting] = !this.settings[setting];
        this.updateToggle(setting + 'Toggle', this.settings[setting]);
        this.saveSettings();
        
        this.showNotification(`${setting} ${this.settings[setting] ? 'ativado' : 'desativado'}`);
    }
    
    async performAutoLogin() {
        if (!this.currentSite.detected) {
            this.showNotification('Site não suportado para auto login', 'error');
            return;
        }
        
        try {
            this.showNotification('Iniciando auto login...');
            
            // Enviar mensagem para content script
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            await chrome.tabs.sendMessage(tab.id, {
                action: 'autoLogin',
                site: this.currentSite,
                certificates: this.certificates
            });
            
            this.logSecurityEvent('auto_login_attempt', {
                site: this.currentSite.name,
                url: this.currentSite.url
            });
            
        } catch (error) {
            console.error('Erro no auto login:', error);
            this.showNotification('Erro no auto login', 'error');
        }
    }
    
    async captureScreen() {
        try {
            this.showNotification('Capturando tela...');
            
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // Capturar screenshot
            const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, {
                format: 'png',
                quality: 90
            });
            
            // Download da captura
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `CertGuard_Capture_${timestamp}.png`;
            
            await chrome.downloads.download({
                url: dataUrl,
                filename: filename,
                saveAs: false
            });
            
            this.showNotification('Tela capturada com sucesso!');
            
            this.logSecurityEvent('screen_capture', {
                site: this.currentSite.name,
                filename: filename
            });
            
        } catch (error) {
            console.error('Erro ao capturar tela:', error);
            this.showNotification('Erro ao capturar tela', 'error');
        }
    }
    
    openDashboard() {
        chrome.tabs.create({
            url: this.apiBase
        });
    }
    
    openDownloads() {
        chrome.tabs.create({
            url: 'chrome://downloads/'
        });
    }
    
    openHelp() {
        chrome.tabs.create({
            url: `${this.apiBase}/help`
        });
    }
    
    openConfig() {
        chrome.tabs.create({
            url: `${this.apiBase}/config`
        });
    }
    
    openAbout() {
        this.showNotification('CertGuard AI v2.0.0 - Extensão Oficial');
    }
    
    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
        
        // Notificação do sistema se habilitada
        if (this.settings.notifications) {
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'CertGuard AI',
                message: message
            });
        }
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    async logSecurityEvent(eventType, details = {}) {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // Obter IP (simulado)
            const ipAddress = '192.168.1.100'; // Em produção, obter IP real
            
            const eventData = {
                user_id: 'extension_user',
                event_type: eventType,
                ip_address: ipAddress,
                details: {
                    ...details,
                    url: tab.url,
                    timestamp: new Date().toISOString(),
                    user_agent: navigator.userAgent
                }
            };
            
            // Enviar para API (em produção)
            // await fetch(`${this.apiBase}/api/lucia/security-event`, {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(eventData)
            // });
            
            console.log('Security event logged:', eventData);
            
        } catch (error) {
            console.error('Erro ao registrar evento de segurança:', error);
        }
    }
}

// Inicializar popup quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    new CertGuardPopup();
});

// Escutar mensagens do background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'updateCertificates') {
        // Recarregar certificados
        window.location.reload();
    }
    
    if (message.action === 'showNotification') {
        // Mostrar notificação
        const popup = window.certguardPopup;
        if (popup) {
            popup.showNotification(message.message, message.type);
        }
    }
    
    sendResponse({ success: true });
});

