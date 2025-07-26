// CertGuard AI - Background Service Worker
// Gerencia eventos da extensão e comunicação entre componentes

class CertGuardBackground {
    constructor() {
        this.certificates = [];
        this.settings = {
            autoLogin: false,
            autoCapture: true,
            notifications: true
        };
        this.init();
    }

    init() {
        console.log('CertGuard AI Background Service Worker iniciado');
        this.loadSettings();
        this.setupEventListeners();
    }

    // Carregar configurações salvas
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

    // Salvar configurações
    async saveSettings() {
        try {
            await chrome.storage.sync.set({ certguard_settings: this.settings });
        } catch (error) {
            console.error('Erro ao salvar configurações:', error);
        }
    }

    // Configurar event listeners
    setupEventListeners() {
        // Quando a extensão é instalada
        chrome.runtime.onInstalled.addListener((details) => {
            if (details.reason === 'install') {
                this.showWelcomeNotification();
                this.openDashboard();
            }
        });

        // Quando uma aba é atualizada
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete' && tab.url) {
                this.checkTribunalSite(tab);
            }
        });

        // Mensagens do content script
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleMessage(request, sender, sendResponse);
            return true; // Manter canal aberto para resposta assíncrona
        });

        // Atalhos de teclado
        chrome.commands.onCommand.addListener((command) => {
            this.handleCommand(command);
        });

        // Clique no ícone da extensão
        chrome.action.onClicked.addListener((tab) => {
            this.handleActionClick(tab);
        });
    }

    // Verificar se é um site de tribunal
    checkTribunalSite(tab) {
        const tribunalDomains = [
            'tjrj.jus.br',
            'tjsp.jus.br',
            'trf2.jus.br',
            'pje.jus.br',
            'esaj.tjsp.jus.br',
            'projudi.tjrj.jus.br'
        ];

        const url = new URL(tab.url);
        const isTribunal = tribunalDomains.some(domain => url.hostname.includes(domain));

        if (isTribunal && this.settings.notifications) {
            this.showTribunalDetectedNotification(tab);
        }
    }

    // Mostrar notificação de tribunal detectado
    showTribunalDetectedNotification(tab) {
        if (this.settings.notifications) {
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'CertGuard AI - Tribunal Detectado',
                message: `Tribunal detectado: ${new URL(tab.url).hostname}\nClique para ações rápidas.`,
                buttons: [
                    { title: 'Auto Login' },
                    { title: 'Selecionar Certificado' }
                ]
            });
        }
    }

    // Mostrar notificação de boas-vindas
    showWelcomeNotification() {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: 'CertGuard AI Instalado!',
            message: 'Extensão instalada com sucesso. Clique para acessar o dashboard.',
            buttons: [
                { title: 'Abrir Dashboard' },
                { title: 'Ver Tutorial' }
            ]
        });
    }

    // Abrir dashboard
    openDashboard() {
        chrome.tabs.create({
            url: 'https://8080-ick1rotydcjwas9kzjqp5-50bdaabf.manusvm.computer'
        });
    }

    // Lidar com mensagens
    async handleMessage(request, sender, sendResponse) {
        switch (request.action) {
            case 'getCertificates':
                sendResponse({ certificates: this.certificates });
                break;

            case 'getSettings':
                sendResponse({ settings: this.settings });
                break;

            case 'updateSettings':
                this.settings = { ...this.settings, ...request.settings };
                await this.saveSettings();
                sendResponse({ success: true });
                break;

            case 'performAutoLogin':
                this.performAutoLogin(sender.tab);
                sendResponse({ success: true });
                break;

            case 'captureScreen':
                this.captureScreen(sender.tab);
                sendResponse({ success: true });
                break;

            case 'logActivity':
                this.logActivity(request.activity, sender.tab);
                sendResponse({ success: true });
                break;

            default:
                sendResponse({ error: 'Ação não reconhecida' });
        }
    }

    // Lidar com comandos de teclado
    async handleCommand(command) {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        switch (command) {
            case 'auto-login':
                this.performAutoLogin(tab);
                break;

            case 'select-certificate':
                this.injectScript(tab, 'showCertificateSelector');
                break;

            case 'capture-screen':
                this.captureScreen(tab);
                break;

            case 'open-dashboard':
                this.openDashboard();
                break;
        }
    }

    // Lidar com clique no ícone
    handleActionClick(tab) {
        // O popup será aberto automaticamente
        // Este método pode ser usado para ações alternativas
    }

    // Realizar auto login
    async performAutoLogin(tab) {
        try {
            await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: () => {
                    if (window.CertGuardExtension) {
                        const extension = new window.CertGuardExtension();
                        extension.performAutoLogin();
                    }
                }
            });

            if (this.settings.notifications) {
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: 'icons/icon48.png',
                    title: 'CertGuard AI',
                    message: 'Auto login iniciado...'
                });
            }
        } catch (error) {
            console.error('Erro no auto login:', error);
        }
    }

    // Capturar tela
    async captureScreen(tab) {
        try {
            const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, {
                format: 'png',
                quality: 90
            });

            // Salvar captura
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `certguard-capture-${timestamp}.png`;

            // Criar download
            chrome.downloads.download({
                url: dataUrl,
                filename: filename,
                saveAs: false
            });

            if (this.settings.notifications) {
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: 'icons/icon48.png',
                    title: 'CertGuard AI',
                    message: `Captura salva: ${filename}`
                });
            }
        } catch (error) {
            console.error('Erro na captura:', error);
        }
    }

    // Injetar script
    async injectScript(tab, functionName) {
        try {
            await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: (funcName) => {
                    if (window.CertGuardExtension) {
                        const extension = new window.CertGuardExtension();
                        if (extension[funcName]) {
                            extension[funcName]();
                        }
                    }
                },
                args: [functionName]
            });
        } catch (error) {
            console.error('Erro ao injetar script:', error);
        }
    }

    // Registrar atividade
    logActivity(activity, tab) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            activity: activity,
            url: tab.url,
            title: tab.title
        };

        // Salvar no storage local
        chrome.storage.local.get(['certguard_logs'], (result) => {
            const logs = result.certguard_logs || [];
            logs.push(logEntry);
            
            // Manter apenas os últimos 1000 logs
            if (logs.length > 1000) {
                logs.splice(0, logs.length - 1000);
            }

            chrome.storage.local.set({ certguard_logs: logs });
        });
    }
}

// Inicializar background service
const certguardBackground = new CertGuardBackground();

// Lidar com cliques em notificações
chrome.notifications.onClicked.addListener((notificationId) => {
    certguardBackground.openDashboard();
});

chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const tab = tabs[0];
        
        if (buttonIndex === 0) {
            // Primeiro botão - Auto Login
            certguardBackground.performAutoLogin(tab);
        } else if (buttonIndex === 1) {
            // Segundo botão - Selecionar Certificado ou Dashboard
            if (notificationId.includes('welcome')) {
                certguardBackground.openDashboard();
            } else {
                certguardBackground.injectScript(tab, 'showCertificateSelector');
            }
        }
    });
});

