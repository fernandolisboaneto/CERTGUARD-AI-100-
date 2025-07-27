// Content Script para automação de tribunais - CertGuard AI

class CertGuardContentScript {
    constructor() {
        this.currentSite = this.detectSite();
        this.isInjected = false;
        this.certificates = [];
        
        this.init();
    }
    
    init() {
        if (this.isInjected) return;
        this.isInjected = true;
        
        console.log('CertGuard AI Content Script carregado em:', this.currentSite.name);
        
        this.setupMessageListener();
        this.injectUI();
        this.observePageChanges();
        
        // Notificar background script
        chrome.runtime.sendMessage({
            action: 'pageLoaded',
            site: this.currentSite
        });
    }
    
    detectSite() {
        const url = window.location.href;
        const hostname = window.location.hostname;
        
        const sites = {
            'tjrj.jus.br': {
                name: 'TJ-RJ',
                fullName: 'Tribunal de Justiça do Rio de Janeiro',
                loginSelectors: {
                    certificateButton: 'input[value*="Certificado"], button[title*="certificado"], .certificado',
                    usernameField: 'input[name="usuario"], input[name="login"], #usuario, #login',
                    passwordField: 'input[name="senha"], input[type="password"], #senha, #password',
                    submitButton: 'input[type="submit"], button[type="submit"], .btn-login'
                }
            },
            'tjsp.jus.br': {
                name: 'TJSP',
                fullName: 'Tribunal de Justiça de São Paulo',
                loginSelectors: {
                    certificateButton: '.certificado-digital, input[value*="Certificado"]',
                    usernameField: '#usuario, input[name="usuario"]',
                    passwordField: '#senha, input[name="senha"]',
                    submitButton: '#entrar, .btn-entrar'
                }
            },
            'esaj.tjsp.jus.br': {
                name: 'E-SAJ',
                fullName: 'Sistema de Automação da Justiça',
                loginSelectors: {
                    certificateButton: '.certificado, input[value*="Certificado Digital"]',
                    usernameField: '#nuUsuario, input[name="nuUsuario"]',
                    passwordField: '#deSenha, input[name="deSenha"]',
                    submitButton: '#pbEntrar, .pbEntrar'
                }
            },
            'trf2.jus.br': {
                name: 'TRF-2',
                fullName: 'Tribunal Regional Federal da 2ª Região',
                loginSelectors: {
                    certificateButton: 'input[value*="Certificado"], .cert-login',
                    usernameField: 'input[name="j_username"], #j_username',
                    passwordField: 'input[name="j_password"], #j_password',
                    submitButton: 'input[value="Entrar"], .login-submit'
                }
            },
            'pje.jus.br': {
                name: 'PJe',
                fullName: 'Processo Judicial Eletrônico',
                loginSelectors: {
                    certificateButton: '#certificadoDigital, .certificado-digital',
                    usernameField: '#username, input[name="username"]',
                    passwordField: '#password, input[name="password"]',
                    submitButton: '#kc-login, .btn-login'
                }
            },
            'projudi.tjrj.jus.br': {
                name: 'PROJUDI',
                fullName: 'Processo Judicial Digital',
                loginSelectors: {
                    certificateButton: 'input[value*="Certificado"], .certificado',
                    usernameField: '#login, input[name="login"]',
                    passwordField: '#senha, input[name="senha"]',
                    submitButton: '.botao-entrar, input[value="Entrar"]'
                }
            }
        };
        
        for (const [domain, siteInfo] of Object.entries(sites)) {
            if (hostname.includes(domain)) {
                return { ...siteInfo, domain, detected: true };
            }
        }
        
        return {
            name: 'Site Desconhecido',
            fullName: 'Site não reconhecido',
            detected: false
        };
    }
    
    setupMessageListener() {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Manter canal aberto
        });
    }
    
    async handleMessage(message, sender, sendResponse) {
        try {
            switch (message.action) {
                case 'autoLogin':
                    const loginResult = await this.performAutoLogin(message.certificates);
                    sendResponse(loginResult);
                    break;
                    
                case 'performAutoLogin':
                    const result = await this.performAutoLogin();
                    sendResponse(result);
                    break;
                    
                case 'getCertificates':
                    sendResponse({ certificates: this.certificates });
                    break;
                    
                case 'highlightLoginElements':
                    this.highlightLoginElements();
                    sendResponse({ success: true });
                    break;
                    
                case 'fillForm':
                    const fillResult = this.fillLoginForm(message.data);
                    sendResponse(fillResult);
                    break;
                    
                default:
                    sendResponse({ success: false, error: 'Ação não reconhecida' });
            }
        } catch (error) {
            console.error('Erro ao processar mensagem:', error);
            sendResponse({ success: false, error: error.message });
        }
    }
    
    injectUI() {
        if (!this.currentSite.detected) return;
        
        // Criar botão flutuante do CertGuard
        const floatingButton = document.createElement('div');
        floatingButton.id = 'certguard-floating-btn';
        floatingButton.innerHTML = `
            <div class="certguard-btn-content">
                <div class="certguard-icon">🛡️</div>
                <div class="certguard-text">CertGuard AI</div>
            </div>
        `;
        
        // Estilos do botão flutuante
        const styles = `
            #certguard-floating-btn {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 12px;
                padding: 12px 16px;
                cursor: pointer;
                box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
                transition: all 0.3s ease;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                user-select: none;
            }
            
            #certguard-floating-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
            }
            
            .certguard-btn-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .certguard-icon {
                font-size: 16px;
            }
            
            .certguard-text {
                font-weight: 500;
            }
            
            .certguard-highlight {
                outline: 3px solid #667eea !important;
                outline-offset: 2px !important;
                background-color: rgba(102, 126, 234, 0.1) !important;
                transition: all 0.3s ease !important;
            }
            
            .certguard-tooltip {
                position: absolute;
                background: #333;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                white-space: nowrap;
                z-index: 10001;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .certguard-tooltip.show {
                opacity: 1;
            }
        `;
        
        // Injetar estilos
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
        
        // Adicionar botão à página
        document.body.appendChild(floatingButton);
        
        // Event listener do botão
        floatingButton.addEventListener('click', () => {
            this.showQuickActions();
        });
        
        // Detectar elementos de login automaticamente
        setTimeout(() => {
            this.detectLoginElements();
        }, 2000);
    }
    
    showQuickActions() {
        // Criar menu de ações rápidas
        const existingMenu = document.getElementById('certguard-quick-menu');
        if (existingMenu) {
            existingMenu.remove();
            return;
        }
        
        const quickMenu = document.createElement('div');
        quickMenu.id = 'certguard-quick-menu';
        quickMenu.innerHTML = `
            <div class="certguard-menu-content">
                <div class="certguard-menu-header">
                    <div class="certguard-menu-title">CertGuard AI</div>
                    <div class="certguard-menu-subtitle">${this.currentSite.name}</div>
                </div>
                <div class="certguard-menu-actions">
                    <button class="certguard-menu-btn" data-action="auto-login">
                        🔐 Auto Login
                    </button>
                    <button class="certguard-menu-btn" data-action="highlight-elements">
                        🎯 Destacar Elementos
                    </button>
                    <button class="certguard-menu-btn" data-action="capture-screen">
                        📸 Capturar Tela
                    </button>
                    <button class="certguard-menu-btn" data-action="open-dashboard">
                        📊 Dashboard
                    </button>
                </div>
            </div>
        `;
        
        // Estilos do menu
        const menuStyles = `
            #certguard-quick-menu {
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 10001;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                min-width: 250px;
                overflow: hidden;
                animation: certguardSlideIn 0.3s ease;
            }
            
            @keyframes certguardSlideIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .certguard-menu-content {
                padding: 0;
            }
            
            .certguard-menu-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 16px;
                text-align: center;
            }
            
            .certguard-menu-title {
                font-weight: 600;
                font-size: 16px;
                margin-bottom: 4px;
            }
            
            .certguard-menu-subtitle {
                font-size: 12px;
                opacity: 0.9;
            }
            
            .certguard-menu-actions {
                padding: 12px;
            }
            
            .certguard-menu-btn {
                width: 100%;
                padding: 12px 16px;
                border: none;
                background: #f8fafc;
                color: #334155;
                border-radius: 8px;
                margin-bottom: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 14px;
                text-align: left;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .certguard-menu-btn:hover {
                background: #e2e8f0;
                transform: translateY(-1px);
            }
            
            .certguard-menu-btn:last-child {
                margin-bottom: 0;
            }
        `;
        
        // Adicionar estilos do menu
        const menuStyleSheet = document.createElement('style');
        menuStyleSheet.textContent = menuStyles;
        document.head.appendChild(menuStyleSheet);
        
        document.body.appendChild(quickMenu);
        
        // Event listeners dos botões
        quickMenu.querySelectorAll('.certguard-menu-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.executeQuickAction(action);
                quickMenu.remove();
            });
        });
        
        // Fechar menu ao clicar fora
        setTimeout(() => {
            document.addEventListener('click', (e) => {
                if (!quickMenu.contains(e.target) && !document.getElementById('certguard-floating-btn').contains(e.target)) {
                    quickMenu.remove();
                }
            }, { once: true });
        }, 100);
    }
    
    async executeQuickAction(action) {
        switch (action) {
            case 'auto-login':
                await this.performAutoLogin();
                break;
                
            case 'highlight-elements':
                this.highlightLoginElements();
                break;
                
            case 'capture-screen':
                chrome.runtime.sendMessage({ action: 'captureScreen' });
                break;
                
            case 'open-dashboard':
                window.open('https://8081-ick1rotydcjwas9kzjqp5-50bdaabf.manusvm.computer', '_blank');
                break;
        }
    }
    
    detectLoginElements() {
        if (!this.currentSite.detected || !this.currentSite.loginSelectors) return;
        
        const selectors = this.currentSite.loginSelectors;
        const elements = {
            certificateButton: this.findElement(selectors.certificateButton),
            usernameField: this.findElement(selectors.usernameField),
            passwordField: this.findElement(selectors.passwordField),
            submitButton: this.findElement(selectors.submitButton)
        };
        
        // Contar elementos encontrados
        const foundElements = Object.values(elements).filter(el => el !== null).length;
        
        if (foundElements > 0) {
            console.log(`CertGuard: ${foundElements} elementos de login detectados`);
            
            // Adicionar tooltips aos elementos
            Object.entries(elements).forEach(([type, element]) => {
                if (element) {
                    this.addTooltip(element, this.getElementDescription(type));
                }
            });
        }
    }
    
    findElement(selectors) {
        if (!selectors) return null;
        
        const selectorList = selectors.split(', ');
        
        for (const selector of selectorList) {
            const element = document.querySelector(selector.trim());
            if (element) {
                return element;
            }
        }
        
        return null;
    }
    
    getElementDescription(type) {
        const descriptions = {
            certificateButton: 'Botão de Certificado Digital',
            usernameField: 'Campo de Usuário',
            passwordField: 'Campo de Senha',
            submitButton: 'Botão de Login'
        };
        
        return descriptions[type] || 'Elemento de Login';
    }
    
    addTooltip(element, description) {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'certguard-tooltip show';
            tooltip.textContent = `CertGuard: ${description}`;
            
            const rect = element.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.top - 35) + 'px';
            
            document.body.appendChild(tooltip);
            
            element.addEventListener('mouseleave', () => {
                tooltip.remove();
            }, { once: true });
        });
    }
    
    highlightLoginElements() {
        // Remover highlights anteriores
        document.querySelectorAll('.certguard-highlight').forEach(el => {
            el.classList.remove('certguard-highlight');
        });
        
        if (!this.currentSite.detected || !this.currentSite.loginSelectors) {
            this.showNotification('Site não suportado para destacar elementos', 'warning');
            return;
        }
        
        const selectors = this.currentSite.loginSelectors;
        let highlightedCount = 0;
        
        Object.values(selectors).forEach(selector => {
            const element = this.findElement(selector);
            if (element) {
                element.classList.add('certguard-highlight');
                highlightedCount++;
            }
        });
        
        if (highlightedCount > 0) {
            this.showNotification(`${highlightedCount} elementos destacados`, 'success');
            
            // Remover highlights após 5 segundos
            setTimeout(() => {
                document.querySelectorAll('.certguard-highlight').forEach(el => {
                    el.classList.remove('certguard-highlight');
                });
            }, 5000);
        } else {
            this.showNotification('Nenhum elemento de login encontrado', 'warning');
        }
    }
    
    async performAutoLogin(certificates = null) {
        if (!this.currentSite.detected) {
            this.showNotification('Site não suportado para auto login', 'error');
            return { success: false, error: 'Site não suportado' };
        }
        
        try {
            this.showNotification('Iniciando auto login...', 'info');
            
            const selectors = this.currentSite.loginSelectors;
            
            // Tentar clicar no botão de certificado digital primeiro
            const certButton = this.findElement(selectors.certificateButton);
            if (certButton) {
                certButton.click();
                this.showNotification('Botão de certificado clicado', 'success');
                
                // Aguardar possível redirecionamento ou modal
                await this.sleep(2000);
                
                // Verificar se apareceu seletor de certificado
                await this.handleCertificateSelection();
                
                return { success: true, method: 'certificate' };
            }
            
            // Se não encontrou botão de certificado, tentar login tradicional
            const usernameField = this.findElement(selectors.usernameField);
            const passwordField = this.findElement(selectors.passwordField);
            const submitButton = this.findElement(selectors.submitButton);
            
            if (usernameField && passwordField && submitButton) {
                // Preencher campos com dados de teste
                usernameField.value = 'admin';
                usernameField.dispatchEvent(new Event('input', { bubbles: true }));
                
                passwordField.value = 'admin123';
                passwordField.dispatchEvent(new Event('input', { bubbles: true }));
                
                await this.sleep(500);
                
                submitButton.click();
                
                this.showNotification('Formulário preenchido e enviado', 'success');
                
                return { success: true, method: 'form' };
            }
            
            this.showNotification('Elementos de login não encontrados', 'warning');
            return { success: false, error: 'Elementos não encontrados' };
            
        } catch (error) {
            console.error('Erro no auto login:', error);
            this.showNotification('Erro no auto login: ' + error.message, 'error');
            return { success: false, error: error.message };
        }
    }
    
    async handleCertificateSelection() {
        // Aguardar possível modal ou lista de certificados
        await this.sleep(1000);
        
        // Procurar por seletores comuns de certificados
        const certSelectors = [
            'select[name*="certificado"]',
            '.certificado-lista option',
            '.cert-select option',
            'input[type="radio"][name*="cert"]'
        ];
        
        for (const selector of certSelectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                // Selecionar primeiro certificado disponível
                if (elements[0].tagName === 'OPTION') {
                    elements[0].selected = true;
                    elements[0].parentElement.dispatchEvent(new Event('change', { bubbles: true }));
                } else if (elements[0].type === 'radio') {
                    elements[0].checked = true;
                    elements[0].dispatchEvent(new Event('change', { bubbles: true }));
                }
                
                this.showNotification('Certificado selecionado', 'success');
                
                // Procurar botão de confirmação
                const confirmButtons = document.querySelectorAll('button[type="submit"], input[value*="Confirmar"], .btn-confirmar');
                if (confirmButtons.length > 0) {
                    await this.sleep(500);
                    confirmButtons[0].click();
                }
                
                break;
            }
        }
    }
    
    fillLoginForm(data) {
        try {
            const selectors = this.currentSite.loginSelectors;
            
            if (data.username) {
                const usernameField = this.findElement(selectors.usernameField);
                if (usernameField) {
                    usernameField.value = data.username;
                    usernameField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
            
            if (data.password) {
                const passwordField = this.findElement(selectors.passwordField);
                if (passwordField) {
                    passwordField.value = data.password;
                    passwordField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
            
            return { success: true };
            
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    observePageChanges() {
        // Observar mudanças na página para detectar novos elementos
        const observer = new MutationObserver((mutations) => {
            let shouldRedetect = false;
            
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Verificar se foram adicionados elementos de formulário
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.tagName === 'FORM' || node.querySelector('form, input, button')) {
                                shouldRedetect = true;
                            }
                        }
                    });
                }
            });
            
            if (shouldRedetect) {
                setTimeout(() => {
                    this.detectLoginElements();
                }, 1000);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    showNotification(message, type = 'info') {
        // Remover notificação anterior
        const existingNotification = document.getElementById('certguard-notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        const notification = document.createElement('div');
        notification.id = 'certguard-notification';
        notification.className = `certguard-notification ${type}`;
        notification.textContent = message;
        
        // Estilos da notificação
        const notificationStyles = `
            .certguard-notification {
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 10002;
                padding: 12px 20px;
                border-radius: 8px;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                font-weight: 500;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                animation: certguardNotificationSlide 0.3s ease;
            }
            
            .certguard-notification.success {
                background: #10b981;
            }
            
            .certguard-notification.error {
                background: #ef4444;
            }
            
            .certguard-notification.warning {
                background: #f59e0b;
            }
            
            .certguard-notification.info {
                background: #3b82f6;
            }
            
            @keyframes certguardNotificationSlide {
                from {
                    opacity: 0;
                    transform: translateX(-50%) translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
            }
        `;
        
        // Adicionar estilos se não existirem
        if (!document.getElementById('certguard-notification-styles')) {
            const styleSheet = document.createElement('style');
            styleSheet.id = 'certguard-notification-styles';
            styleSheet.textContent = notificationStyles;
            document.head.appendChild(styleSheet);
        }
        
        document.body.appendChild(notification);
        
        // Remover após 4 segundos
        setTimeout(() => {
            notification.remove();
        }, 4000);
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Inicializar content script
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new CertGuardContentScript();
    });
} else {
    new CertGuardContentScript();
}

