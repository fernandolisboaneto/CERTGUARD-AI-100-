/**
 * CertGuard AI Extension - Popup Logic
 * Extensão segura e stateless para autenticação com certificados digitais
 */

class CertGuardPopup {
    constructor() {
        this.apiBase = 'https://8081-ick1rotydcjwas9kzjqp5-50bdaabf.manusvm.computer/api';
        this.dashboardUrl = 'https://8081-ick1rotydcjwas9kzjqp5-50bdaabf.manusvm.computer';
        this.currentTab = null;
        this.authToken = null;
        this.userInfo = null;
        this.siteInfo = null;
        
        this.init();
    }
    
    async init() {
        console.log('🚀 CertGuard AI Extension iniciada');
        
        // Verificar se já está logado
        await this.checkAuthStatus();
        
        // Obter informações da aba atual
        await this.getCurrentTab();
        
        // Configurar event listeners
        this.setupEventListeners();
        
        // Atualizar interface
        this.updateUI();
        
        // Verificar site atual
        this.checkCurrentSite();
    }
    
    async checkAuthStatus() {
        try {
            const result = await chrome.storage.local.get(['authToken', 'userInfo']);
            
            if (result.authToken && result.userInfo) {
                this.authToken = result.authToken;
                this.userInfo = result.userInfo;
                
                // Verificar se token ainda é válido
                const isValid = await this.validateToken();
                if (isValid) {
                    this.showLoggedSection();
                } else {
                    await this.logout();
                }
            } else {
                this.showLoginSection();
            }
        } catch (error) {
            console.error('❌ Erro ao verificar status de autenticação:', error);
            this.showLoginSection();
        }
    }
    
    async validateToken() {
        try {
            const response = await fetch(`${this.apiBase}/auth/validate`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            return response.ok;
        } catch (error) {
            console.error('❌ Erro ao validar token:', error);
            return false;
        }
    }
    
    async getCurrentTab() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            this.currentTab = tab;
            
            // Atualizar URL atual na interface
            const urlElement = document.getElementById('currentUrl');
            if (urlElement && tab.url) {
                const url = new URL(tab.url);
                urlElement.textContent = url.hostname;
            }
        } catch (error) {
            console.error('❌ Erro ao obter aba atual:', error);
        }
    }
    
    setupEventListeners() {
        // Login
        document.getElementById('loginBtn').addEventListener('click', () => this.login());
        document.getElementById('username').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.login();
        });
        document.getElementById('password').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.login();
        });
        
        // Dashboard
        document.getElementById('dashboardBtn').addEventListener('click', () => this.openDashboard());
        document.getElementById('dashboardLink').addEventListener('click', () => this.openDashboard());
        
        // Autenticação
        document.getElementById('authenticateBtn').addEventListener('click', () => this.authenticate());
        
        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
    }
    
    async login() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        
        if (!username || !password) {
            this.showError('Por favor, preencha usuário e senha');
            return;
        }
        
        const loginBtn = document.getElementById('loginBtn');
        const originalText = loginBtn.textContent;
        
        try {
            loginBtn.textContent = 'Conectando...';
            loginBtn.disabled = true;
            
            // Simular login (em produção, fazer requisição real)
            await this.delay(1000);
            
            if (username === 'admin' && password === 'admin123') {
                // Login bem-sucedido
                this.authToken = this.generateJWT();
                this.userInfo = {
                    id: 'user-001',
                    username: username,
                    name: 'Administrador',
                    role: 'admin',
                    loginTime: new Date().toISOString()
                };
                
                // Salvar no storage
                await chrome.storage.local.set({
                    authToken: this.authToken,
                    userInfo: this.userInfo
                });
                
                this.showLoggedSection();
                this.updateConnectionStatus('online', 'Conectado ao backend LucIA');
                
                // Verificar site atual após login
                this.checkCurrentSite();
                
            } else {
                throw new Error('Credenciais inválidas');
            }
            
        } catch (error) {
            console.error('❌ Erro no login:', error);
            this.showError('Erro ao fazer login: ' + error.message);
        } finally {
            loginBtn.textContent = originalText;
            loginBtn.disabled = false;
        }
    }
    
    async logout() {
        try {
            // Limpar storage
            await chrome.storage.local.clear();
            
            // Resetar estado
            this.authToken = null;
            this.userInfo = null;
            this.siteInfo = null;
            
            // Mostrar tela de login
            this.showLoginSection();
            
            // Limpar campos
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
            
        } catch (error) {
            console.error('❌ Erro no logout:', error);
        }
    }
    
    async checkCurrentSite() {
        if (!this.currentTab || !this.currentTab.url) {
            this.updateSiteStatus('offline', 'Nenhuma aba ativa');
            return;
        }
        
        try {
            const url = new URL(this.currentTab.url);
            const hostname = url.hostname.toLowerCase();
            
            // Lista de sites homologados
            const homologatedSites = [
                'tjrj.jus.br',
                'tjsp.jus.br',
                'trf2.jus.br',
                'pje.jus.br',
                'esaj.tjsp.jus.br',
                'projudi.tjrj.jus.br'
            ];
            
            const isHomologated = homologatedSites.some(site => hostname.includes(site));
            
            if (isHomologated) {
                this.siteInfo = {
                    hostname: hostname,
                    isHomologated: true,
                    tribunal: this.getTribunalName(hostname),
                    detectedAt: new Date().toISOString()
                };
                
                this.updateSiteStatus('online', `Tribunal detectado: ${this.siteInfo.tribunal}`);
                this.enableAuthentication();
                
                // Notificar background script
                chrome.runtime.sendMessage({
                    action: 'siteDetected',
                    siteInfo: this.siteInfo
                });
                
            } else {
                this.siteInfo = {
                    hostname: hostname,
                    isHomologated: false,
                    detectedAt: new Date().toISOString()
                };
                
                this.updateSiteStatus('offline', 'Site não homologado');
                this.disableAuthentication();
            }
            
        } catch (error) {
            console.error('❌ Erro ao verificar site:', error);
            this.updateSiteStatus('warning', 'Erro ao verificar site');
        }
    }
    
    getTribunalName(hostname) {
        const tribunals = {
            'tjrj.jus.br': 'TJ-RJ',
            'tjsp.jus.br': 'TJSP',
            'trf2.jus.br': 'TRF-2',
            'pje.jus.br': 'PJe',
            'esaj.tjsp.jus.br': 'E-SAJ',
            'projudi.tjrj.jus.br': 'PROJUDI'
        };
        
        for (const [domain, name] of Object.entries(tribunals)) {
            if (hostname.includes(domain)) {
                return name;
            }
        }
        
        return 'Tribunal';
    }
    
    async authenticate() {
        if (!this.siteInfo || !this.siteInfo.isHomologated) {
            this.showError('Site não homologado para autenticação');
            return;
        }
        
        const authBtn = document.getElementById('authenticateBtn');
        const authBtnText = document.getElementById('authBtnText');
        const authLoading = document.getElementById('authLoading');
        
        try {
            authBtn.disabled = true;
            authBtnText.textContent = 'Autenticando...';
            authLoading.classList.remove('hidden');
            
            // Preparar dados para o backend
            const authData = {
                userId: this.userInfo.id,
                siteUrl: this.currentTab.url,
                hostname: this.siteInfo.hostname,
                tribunal: this.siteInfo.tribunal,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                // Geolocalização seria obtida aqui em produção
                location: { lat: -22.9068, lng: -43.1729 } // Rio de Janeiro (exemplo)\n            };\n            \n            // Simular requisição ao backend\n            await this.delay(2000);\n            \n            // Simular resposta do backend\n            const response = {\n                success: true,\n                certificateType: 'A1', // ou 'A3'\n                certificateInfo: {\n                    type: 'A1',\n                    owner: 'João Silva',\n                    expiry: '2025-12-31',\n                    serial: 'CG123456789'\n                },\n                authMethod: 'hsm', // ou 'daemon'\n                sessionId: 'sess-' + Date.now()\n            };\n            \n            if (response.success) {\n                // Mostrar informações do certificado\n                this.showCertificateInfo(response.certificateInfo);\n                \n                // Executar autenticação baseada no tipo\n                if (response.certificateType === 'A1') {\n                    await this.authenticateA1(response);\n                } else {\n                    await this.authenticateA3(response);\n                }\n                \n                authBtnText.textContent = 'Autenticado com sucesso!';\n                \n                // Resetar após 3 segundos\n                setTimeout(() => {\n                    authBtnText.textContent = 'Autenticar no Site';\n                    authBtn.disabled = false;\n                }, 3000);\n                \n            } else {\n                throw new Error('Falha na autenticação');\n            }\n            \n        } catch (error) {\n            console.error('❌ Erro na autenticação:', error);\n            this.showError('Erro na autenticação: ' + error.message);\n            authBtnText.textContent = 'Tentar Novamente';\n            authBtn.disabled = false;\n        } finally {\n            authLoading.classList.add('hidden');\n        }\n    }\n    \n    async authenticateA1(response) {\n        console.log('🔐 Autenticação A1 via HSM');\n        \n        // Em produção, o backend faria a assinatura via HSM\n        // Aqui apenas simulamos o processo\n        \n        // Enviar comando para content script\n        chrome.tabs.sendMessage(this.currentTab.id, {\n            action: 'injectCertificate',\n            certificateData: response.certificateInfo,\n            authMethod: 'A1',\n            sessionId: response.sessionId\n        });\n    }\n    \n    async authenticateA3(response) {\n        console.log('🔐 Autenticação A3 via Daemon Local');\n        \n        // Em produção, iniciaria o daemon local via nativeMessaging\n        try {\n            // Simular comunicação com daemon local\n            const daemonResponse = await this.communicateWithDaemon({\n                action: 'authenticate',\n                siteUrl: this.currentTab.url,\n                certificateSerial: response.certificateInfo.serial\n            });\n            \n            if (daemonResponse.success) {\n                // Enviar resultado para content script\n                chrome.tabs.sendMessage(this.currentTab.id, {\n                    action: 'injectCertificate',\n                    certificateData: response.certificateInfo,\n                    authMethod: 'A3',\n                    sessionId: response.sessionId,\n                    signature: daemonResponse.signature\n                });\n            }\n            \n        } catch (error) {\n            console.error('❌ Erro na comunicação com daemon:', error);\n            throw error;\n        }\n    }\n    \n    async communicateWithDaemon(message) {\n        // Em produção, usaria chrome.runtime.connectNative()\n        // Por ora, simular resposta\n        await this.delay(1000);\n        \n        return {\n            success: true,\n            signature: 'simulated-signature-' + Date.now(),\n            timestamp: new Date().toISOString()\n        };\n    }\n    \n    showCertificateInfo(certInfo) {\n        document.getElementById('certType').textContent = certInfo.type;\n        document.getElementById('certOwner').textContent = certInfo.owner;\n        document.getElementById('certExpiry').textContent = certInfo.expiry;\n        \n        document.getElementById('certificateSection').classList.remove('hidden');\n        document.getElementById('certStatus').className = 'status-indicator';\n    }\n    \n    enableAuthentication() {\n        const authBtn = document.getElementById('authenticateBtn');\n        const authBtnText = document.getElementById('authBtnText');\n        \n        authBtn.disabled = false;\n        authBtnText.textContent = 'Autenticar no Site';\n    }\n    \n    disableAuthentication() {\n        const authBtn = document.getElementById('authenticateBtn');\n        const authBtnText = document.getElementById('authBtnText');\n        \n        authBtn.disabled = true;\n        authBtnText.textContent = 'Aguardando site homologado...';\n        \n        // Ocultar seção de certificado\n        document.getElementById('certificateSection').classList.add('hidden');\n    }\n    \n    updateConnectionStatus(status, message) {\n        const indicator = document.getElementById('connectionStatus');\n        const info = document.getElementById('statusInfo');\n        \n        indicator.className = `status-indicator ${status === 'online' ? '' : status}`;\n        info.textContent = message;\n    }\n    \n    updateSiteStatus(status, message) {\n        const indicator = document.getElementById('siteStatus');\n        const info = document.getElementById('siteInfo');\n        \n        indicator.className = `status-indicator ${status === 'online' ? '' : status}`;\n        info.textContent = message;\n    }\n    \n    showLoginSection() {\n        document.getElementById('loginSection').classList.remove('hidden');\n        document.getElementById('loggedSection').classList.add('hidden');\n    }\n    \n    showLoggedSection() {\n        document.getElementById('loginSection').classList.add('hidden');\n        document.getElementById('loggedSection').classList.remove('hidden');\n    }\n    \n    openDashboard() {\n        chrome.tabs.create({ url: this.dashboardUrl });\n    }\n    \n    updateUI() {\n        // Atualizar informações do usuário se logado\n        if (this.userInfo) {\n            // Pode adicionar nome do usuário na interface se necessário\n        }\n    }\n    \n    generateJWT() {\n        // Em produção, o JWT viria do backend\n        // Aqui apenas simulamos um token\n        const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));\n        const payload = btoa(JSON.stringify({\n            sub: 'user-001',\n            iat: Math.floor(Date.now() / 1000),\n            exp: Math.floor(Date.now() / 1000) + 3600 // 1 hora\n        }));\n        const signature = 'simulated-signature';\n        \n        return `${header}.${payload}.${signature}`;\n    }\n    \n    showError(message) {\n        // Simples notificação de erro\n        console.error('❌', message);\n        \n        // Em produção, poderia mostrar um toast ou modal\n        alert(message);\n    }\n    \n    delay(ms) {\n        return new Promise(resolve => setTimeout(resolve, ms));\n    }\n}\n\n// Inicializar quando o DOM estiver pronto\ndocument.addEventListener('DOMContentLoaded', () => {\n    new CertGuardPopup();\n});

