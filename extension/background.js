// Background Service Worker para CertGuard AI Extension

class CertGuardBackground {
    constructor() {
        this.apiBase = 'https://8081-ick1rotydcjwas9kzjqp5-50bdaabf.manusvm.computer';
        this.tribunalDomains = [
            'tjrj.jus.br',
            'tjsp.jus.br',
            'trf2.jus.br',
            'pje.jus.br',
            'esaj.tjsp.jus.br',
            'projudi.tjrj.jus.br'
        ];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupContextMenus();
        this.setupAlarms();
    }
    
    setupEventListeners() {
        // Quando extensão é instalada
        chrome.runtime.onInstalled.addListener((details) => {
            if (details.reason === 'install') {
                this.onFirstInstall();
            } else if (details.reason === 'update') {
                this.onUpdate(details.previousVersion);
            }
        });
        
        // Quando tab é atualizada
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete' && tab.url) {
                this.onTabUpdated(tabId, tab);
            }
        });
        
        // Mensagens de content scripts e popup
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Manter canal aberto para resposta assíncrona
        });
        
        // Comandos de teclado
        chrome.commands.onCommand.addListener((command) => {
            this.handleCommand(command);
        });
        
        // Downloads completados
        chrome.downloads.onChanged.addListener((downloadDelta) => {
            if (downloadDelta.state && downloadDelta.state.current === 'complete') {
                this.onDownloadComplete(downloadDelta);
            }
        });
        
        // Notificações clicadas
        chrome.notifications.onClicked.addListener((notificationId) => {
            this.onNotificationClicked(notificationId);
        });
    }
    
    setupContextMenus() {
        chrome.contextMenus.removeAll(() => {
            // Menu principal
            chrome.contextMenus.create({
                id: 'certguard-main',
                title: 'CertGuard AI',
                contexts: ['page']
            });
            
            // Submenu - Auto Login
            chrome.contextMenus.create({
                id: 'auto-login',
                parentId: 'certguard-main',
                title: 'Login Automático',
                contexts: ['page']
            });
            
            // Submenu - Capturar Tela
            chrome.contextMenus.create({
                id: 'capture-screen',
                parentId: 'certguard-main',
                title: 'Capturar Tela',
                contexts: ['page']
            });
            
            // Submenu - Abrir Dashboard
            chrome.contextMenus.create({
                id: 'open-dashboard',
                parentId: 'certguard-main',
                title: 'Abrir Dashboard',
                contexts: ['page']
            });
            
            // Separador
            chrome.contextMenus.create({
                id: 'separator1',
                parentId: 'certguard-main',
                type: 'separator',
                contexts: ['page']
            });
            
            // Submenu - Baixar Certificados
            chrome.contextMenus.create({
                id: 'download-certificates',
                parentId: 'certguard-main',
                title: 'Baixar Certificados',
                contexts: ['page']
            });
        });
        
        // Listener para cliques no menu
        chrome.contextMenus.onClicked.addListener((info, tab) => {
            this.handleContextMenuClick(info, tab);
        });
    }
    
    setupAlarms() {
        // Verificar certificados a cada hora
        chrome.alarms.create('check-certificates', {
            delayInMinutes: 1,
            periodInMinutes: 60
        });
        
        // Sincronizar dados a cada 30 minutos
        chrome.alarms.create('sync-data', {
            delayInMinutes: 5,
            periodInMinutes: 30
        });
        
        chrome.alarms.onAlarm.addListener((alarm) => {
            this.handleAlarm(alarm);
        });
    }
    
    async onFirstInstall() {
        console.log('CertGuard AI Extension instalada');
        
        // Configurações padrão
        await chrome.storage.sync.set({
            certguard_settings: {
                autoLogin: false,
                autoCapture: false,
                notifications: true,
                firstRun: true
            }
        });
        
        // Abrir página de boas-vindas
        chrome.tabs.create({
            url: `${this.apiBase}/welcome`
        });
        
        // Notificação de boas-vindas
        chrome.notifications.create('welcome', {
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: 'CertGuard AI Instalado!',
            message: 'Extensão pronta para uso. Clique para configurar.'
        });
    }
    
    async onUpdate(previousVersion) {
        console.log(`CertGuard AI atualizada de ${previousVersion} para 2.0.0`);
        
        // Notificação de atualização
        chrome.notifications.create('updated', {
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: 'CertGuard AI Atualizada!',
            message: 'Nova versão 2.0.0 com melhorias de segurança.'
        });
    }
    
    async onTabUpdated(tabId, tab) {
        const url = tab.url;
        
        // Verificar se é um tribunal
        const isTribunal = this.tribunalDomains.some(domain => url.includes(domain));
        
        if (isTribunal) {
            // Injetar content script se necessário
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ['content-script.js']
                });
                
                // Atualizar badge
                chrome.action.setBadgeText({
                    tabId: tabId,
                    text: '✓'
                });
                
                chrome.action.setBadgeBackgroundColor({
                    tabId: tabId,
                    color: '#10b981'
                });
                
                // Verificar configurações de auto-ação
                const result = await chrome.storage.sync.get(['certguard_settings']);
                const settings = result.certguard_settings || {};
                
                if (settings.notifications) {
                    chrome.notifications.create(`tribunal-${tabId}`, {
                        type: 'basic',
                        iconUrl: 'icons/icon48.png',
                        title: 'Tribunal Detectado',
                        message: `CertGuard AI ativo em ${this.getTribunalName(url)}`
                    });
                }
                
            } catch (error) {
                console.error('Erro ao injetar content script:', error);
            }
        } else {
            // Limpar badge
            chrome.action.setBadgeText({
                tabId: tabId,
                text: ''
            });
        }
    }
    
    getTribunalName(url) {
        const tribunals = {
            'tjrj.jus.br': 'TJ-RJ',
            'tjsp.jus.br': 'TJSP',
            'trf2.jus.br': 'TRF-2',
            'pje.jus.br': 'PJe',
            'esaj.tjsp.jus.br': 'E-SAJ',
            'projudi.tjrj.jus.br': 'PROJUDI'
        };
        
        for (const [domain, name] of Object.entries(tribunals)) {
            if (url.includes(domain)) {
                return name;
            }
        }
        
        return 'Tribunal';
    }
    
    async handleMessage(message, sender, sendResponse) {
        try {
            switch (message.action) {
                case 'getCertificates':
                    const certificates = await this.getCertificates();
                    sendResponse({ success: true, certificates });
                    break;
                    
                case 'downloadCertificate':
                    const result = await this.downloadCertificate(message.certificateId);
                    sendResponse(result);
                    break;
                    
                case 'logSecurityEvent':
                    await this.logSecurityEvent(message.event);
                    sendResponse({ success: true });
                    break;
                    
                case 'autoLoginComplete':
                    await this.onAutoLoginComplete(message.result, sender.tab);
                    sendResponse({ success: true });
                    break;
                    
                case 'getSettings':
                    const settings = await this.getSettings();
                    sendResponse({ success: true, settings });
                    break;
                    
                default:
                    sendResponse({ success: false, error: 'Ação não reconhecida' });
            }
        } catch (error) {
            console.error('Erro ao processar mensagem:', error);
            sendResponse({ success: false, error: error.message });
        }
    }
    
    async handleCommand(command) {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        switch (command) {
            case 'auto-login':
                await this.performAutoLogin(tab);
                break;
                
            case 'capture-screen':
                await this.captureScreen(tab);
                break;
                
            case 'open-dashboard':
                chrome.tabs.create({ url: this.apiBase });
                break;
        }
    }
    
    async handleContextMenuClick(info, tab) {
        switch (info.menuItemId) {
            case 'auto-login':
                await this.performAutoLogin(tab);
                break;
                
            case 'capture-screen':
                await this.captureScreen(tab);
                break;
                
            case 'open-dashboard':
                chrome.tabs.create({ url: this.apiBase });
                break;
                
            case 'download-certificates':
                chrome.action.openPopup();
                break;
        }
    }
    
    async handleAlarm(alarm) {
        switch (alarm.name) {
            case 'check-certificates':
                await this.checkCertificateUpdates();
                break;
                
            case 'sync-data':
                await this.syncData();
                break;
        }
    }
    
    async getCertificates() {
        try {
            // Simular busca de certificados (em produção, usar API real)
            return [
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
                }
            ];
        } catch (error) {
            console.error('Erro ao buscar certificados:', error);
            return [];
        }
    }
    
    async downloadCertificate(certificateId) {
        try {
            // Simular download (em produção, usar API real)
            const downloadUrl = `${this.apiBase}/api/certificates/download/${certificateId}`;
            
            const downloadId = await chrome.downloads.download({
                url: downloadUrl,
                filename: `certificate_${certificateId}.pfx`,
                saveAs: true
            });
            
            return { success: true, downloadId };
            
        } catch (error) {
            console.error('Erro ao baixar certificado:', error);
            return { success: false, error: error.message };
        }
    }
    
    async performAutoLogin(tab) {
        try {
            await chrome.tabs.sendMessage(tab.id, {
                action: 'performAutoLogin'
            });
            
            chrome.notifications.create('auto-login', {
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'Auto Login',
                message: 'Tentativa de login automático iniciada'
            });
            
        } catch (error) {
            console.error('Erro no auto login:', error);
        }
    }
    
    async captureScreen(tab) {
        try {
            const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, {
                format: 'png',
                quality: 90
            });
            
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `CertGuard_${timestamp}.png`;
            
            await chrome.downloads.download({
                url: dataUrl,
                filename: filename,
                saveAs: false
            });
            
            chrome.notifications.create('capture', {
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'Captura Realizada',
                message: `Tela salva como ${filename}`
            });
            
        } catch (error) {
            console.error('Erro ao capturar tela:', error);
        }
    }
    
    async logSecurityEvent(event) {
        try {
            // Em produção, enviar para API
            console.log('Security event:', event);
            
            // Salvar localmente também
            const events = await chrome.storage.local.get(['security_events']) || { security_events: [] };
            events.security_events.push({
                ...event,
                timestamp: new Date().toISOString()
            });
            
            // Manter apenas últimos 1000 eventos
            if (events.security_events.length > 1000) {
                events.security_events = events.security_events.slice(-1000);
            }
            
            await chrome.storage.local.set({ security_events: events.security_events });
            
        } catch (error) {
            console.error('Erro ao registrar evento:', error);
        }
    }
    
    async onAutoLoginComplete(result, tab) {
        if (result.success) {
            chrome.notifications.create('login-success', {
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'Login Realizado',
                message: 'Login automático concluído com sucesso'
            });
        } else {
            chrome.notifications.create('login-error', {
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'Erro no Login',
                message: result.error || 'Falha no login automático'
            });
        }
    }
    
    async getSettings() {
        const result = await chrome.storage.sync.get(['certguard_settings']);
        return result.certguard_settings || {
            autoLogin: false,
            autoCapture: false,
            notifications: true
        };
    }
    
    async checkCertificateUpdates() {
        try {
            // Verificar se há novos certificados disponíveis
            console.log('Verificando atualizações de certificados...');
            
            // Em produção, fazer chamada para API
            // const response = await fetch(`${this.apiBase}/api/certificates/check-updates`);
            
        } catch (error) {
            console.error('Erro ao verificar atualizações:', error);
        }
    }
    
    async syncData() {
        try {
            console.log('Sincronizando dados...');
            
            // Sincronizar eventos de segurança, configurações, etc.
            
        } catch (error) {
            console.error('Erro na sincronização:', error);
        }
    }
    
    onDownloadComplete(downloadDelta) {
        // Verificar se é um certificado CertGuard
        if (downloadDelta.filename && downloadDelta.filename.current.includes('certificate_')) {
            chrome.notifications.create('download-complete', {
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'Download Concluído',
                message: 'Certificado baixado com sucesso'
            });
        }
    }
    
    onNotificationClicked(notificationId) {
        switch (notificationId) {
            case 'welcome':
                chrome.tabs.create({ url: `${this.apiBase}/welcome` });
                break;
                
            case 'updated':
                chrome.tabs.create({ url: `${this.apiBase}/changelog` });
                break;
                
            default:
                // Abrir popup por padrão
                chrome.action.openPopup();
        }
        
        chrome.notifications.clear(notificationId);
    }
}

// Inicializar background script
new CertGuardBackground();

