# 🛡️ CertGuard AI - Sistema Avançado de Gestão de Certificados Digitais

<div align="center">

![CertGuard AI Logo](https://img.shields.io/badge/CertGuard-AI-blue?style=for-the-badge&logo=shield&logoColor=white)
![Version](https://img.shields.io/badge/version-2.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/status-100%25%20Funcional-brightgreen?style=for-the-badge)

**Sistema completo de gestão de certificados digitais com IA, automação de tribunais e extensões para navegador**

[🚀 Demo Live](https://8081-ick1rotydcjwas9kzjqp5-50bdaabf.manusvm.computer) • [📖 Documentação](./docs/) • [🔧 Instalação](#instalação) • [🤝 Contribuir](#contribuição)

</div>

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API](#api)
- [Extensão](#extensão)
- [LucIA - IA Jurídica](#lucia---ia-jurídica)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Contato](#contato)

---

## 🎯 Sobre o Projeto

O **CertGuard AI** é um sistema revolucionário de gestão de certificados digitais que unifica as melhores funcionalidades de soluções como Presto/Oystr, Whom/Doc9 e LoyTrust, adicionando tecnologias avançadas como blockchain e inteligência artificial.

### 🌟 Diferenciais

- **🤖 IA Jurídica (LucIA)**: Assistente inteligente para análise de documentos e consultas jurídicas
- **🌐 Automação de Tribunais**: Integração com TJ-RJ, TJSP, TRF-2, PJe e outros
- **🔧 Extensão para Navegador**: Chrome/Edge com detecção automática e auto-login
- **🔒 Conformidade Total**: ICP-Brasil, LGPD e provimentos do CNJ
- **📊 Dashboard Avançado**: Métricas em tempo real e insights preditivos
- **🔗 Blockchain**: Registros imutáveis para auditoria e compliance

### 🎯 Objetivos

O sistema foi desenvolvido para atender às necessidades de:
- **Escritórios de Advocacia** de todos os portes
- **Departamentos Jurídicos** corporativos
- **Órgãos Públicos** e autarquias
- **Cartórios** e serviços notariais
- **Empresas** que utilizam certificação digital

---

## ⚡ Funcionalidades

### 🔐 Gestão de Certificados A1/A3
- ✅ **Importação automática** de certificados A1 (.pfx)
- ✅ **Detecção inteligente** de tokens A3 e smart cards
- ✅ **Monitoramento de expiração** com alertas automáticos
- ✅ **Renovação automatizada** com notificações
- ✅ **Backup seguro** com criptografia
- ✅ **Histórico completo** de uso e atividades
- ✅ **Validação em tempo real** da cadeia de certificação

### 👥 Gestão de Usuários e Organizações
- ✅ **Hierarquia organizacional** multinível
- ✅ **Controle granular** de permissões
- ✅ **Atribuição automática** de certificados
- ✅ **Relatórios detalhados** de uso
- ✅ **Integração AD/LDAP** (planejado)
- ✅ **Auditoria completa** de ações

### 🌐 Automação de Tribunais
- ✅ **Login automático** em sistemas processuais
- ✅ **Peticionamento eletrônico** automatizado
- ✅ **Consulta processual** em lote
- ✅ **Captura de telas** para auditoria
- ✅ **Alertas de prazos** processuais
- ✅ **Relatórios de atividade** detalhados

### 🤖 LucIA - Assistente Jurídica com IA
- ✅ **Análise inteligente** de documentos
- ✅ **OCR avançado** para digitalização
- ✅ **Consulta jurisprudencial** automatizada
- ✅ **Geração de petições** com templates
- ✅ **Controle de prazos** processuais
- ✅ **Insights preditivos** baseados em dados
- ✅ **Suporte por voz** (comando de voz)

### 🔧 Extensão para Navegador
- ✅ **Detecção automática** de sites de tribunais
- ✅ **Auto-login** com seleção de certificados
- ✅ **Captura automática** de evidências
- ✅ **Notificações inteligentes**
- ✅ **Atalhos de teclado** para produtividade
- ✅ **Sincronização** com dashboard web

### 📊 Monitoramento e Auditoria
- ✅ **Dashboard em tempo real** com métricas
- ✅ **Logs detalhados** de todas as ações
- ✅ **Relatórios de conformidade**
- ✅ **Alertas de segurança** automáticos
- ✅ **Backup automatizado** com redundância
- ✅ **Recuperação de desastres**

---

## 🛠️ Tecnologias

### Frontend
- **HTML5/CSS3/JavaScript** - Interface moderna e responsiva
- **Tailwind CSS** - Design system consistente
- **Chart.js** - Visualizações de dados interativas
- **Lucide Icons** - Iconografia profissional

### Backend
- **Python 3.11** - Linguagem principal
- **Flask** - Framework web robusto
- **SQLAlchemy** - ORM para banco de dados
- **JWT** - Autenticação segura
- **Cryptography** - Manipulação de certificados

### Extensão
- **Manifest V3** - Padrão mais recente do Chrome
- **Service Workers** - Background processing
- **Content Scripts** - Interação com páginas
- **Chrome APIs** - Integração nativa

### IA e Automação
- **OpenAI GPT-4** - Processamento de linguagem natural
- **TensorFlow** - Machine learning (planejado)
- **Selenium** - Automação web
- **OCR** - Reconhecimento de texto

### Infraestrutura
- **Docker** - Containerização
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e sessões
- **Nginx** - Proxy reverso
- **SSL/TLS** - Segurança de transporte

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- Git
- Docker (opcional)

### Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/fernandolisboaneto/CERTGUARD-AI-100-.git
cd CERTGUARD-AI-100-

# Instale as dependências do backend
cd backend
pip install -r requirements.txt

# Configure o banco de dados
python src/database.py

# Inicie o servidor backend
python src/main.py

# Em outro terminal, inicie o frontend
cd ../frontend
python -m http.server 8080

# Acesse http://localhost:8080
```

### Instalação com Docker

```bash
# Clone o repositório
git clone https://github.com/fernandolisboaneto/CERTGUARD-AI-100-.git
cd CERTGUARD-AI-100-

# Construa e execute com Docker Compose
docker-compose up -d

# Acesse http://localhost:8080
```

### Instalação da Extensão

1. Abra Chrome/Edge
2. Vá para `chrome://extensions/`
3. Ative o "Modo do desenvolvedor"
4. Clique em "Carregar sem compactação"
5. Selecione a pasta `extension/`
6. A extensão será instalada automaticamente

---

## 💻 Uso

### Acesso ao Sistema

**URL de Demonstração:** https://8080-ick1rotydcjwas9kzjqp5-50bdaabf.manusvm.computer

**Credenciais de Teste:**
- **Administrador:** `admin` / `admin123`
- **Super Admin:** `superadmin` / `super123`

### Primeiros Passos

1. **Faça login** com as credenciais fornecidas
2. **Explore o Dashboard** com métricas em tempo real
3. **Gerencie Certificados** na aba correspondente
4. **Configure Usuários** e organizações
5. **Teste a LucIA** fazendo perguntas jurídicas
6. **Instale a Extensão** para automação

### Funcionalidades Principais

#### Gestão de Certificados
- Importe certificados A1 clicando em "Importar A1 (.pfx)"
- Detecte tokens A3 com "Detectar A3 (Token)"
- Monitore expirações na tabela principal
- Configure renovação automática

#### LucIA - IA Jurídica
- Acesse a aba "Segurança" para configurar a LucIA
- Faça perguntas sobre processos, prazos e jurisprudência
- Analise documentos com OCR automático
- Gere petições com templates inteligentes

#### Automação de Tribunais
- Configure sites na aba "Sites/Tribunais"
- Use a extensão para auto-login
- Capture telas automaticamente
- Monitore atividades no dashboard

---

## 📁 Estrutura do Projeto

```
CERTGUARD-AI-100/
├── 📁 frontend/           # Interface web principal
│   ├── index.html         # Página principal
│   ├── certificates.js    # Dados dos certificados
│   └── lucia-ai.js        # Sistema LucIA
├── 📁 backend/            # API e lógica de negócio
│   ├── src/
│   │   ├── main.py        # Servidor Flask
│   │   ├── models/        # Modelos de dados
│   │   └── routes/        # Rotas da API
│   └── requirements.txt   # Dependências Python
├── 📁 extension/          # Extensão Chrome/Edge
│   ├── manifest.json      # Configuração da extensão
│   ├── popup.html         # Interface popup
│   ├── background.js      # Service worker
│   └── extension.js       # Script principal
├── 📁 docs/               # Documentação completa
│   ├── sistema_certificados_digitais.md
│   ├── checklist_certguard_completo.md
│   └── guia_completo_certguard_superadmin.md
├── 📁 assets/             # Recursos estáticos
├── 📁 screenshots/        # Capturas de tela
├── README.md              # Este arquivo
├── LICENSE                # Licença do projeto
└── docker-compose.yml     # Configuração Docker
```

---

## 🔌 API

### Endpoints Principais

#### Autenticação
```http
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
```

#### Certificados
```http
GET    /api/certificates
POST   /api/certificates
PUT    /api/certificates/{id}
DELETE /api/certificates/{id}
```

#### Usuários
```http
GET    /api/users
POST   /api/users
PUT    /api/users/{id}
DELETE /api/users/{id}
```

#### LucIA
```http
POST /api/lucia/question
POST /api/lucia/analyze
GET  /api/lucia/history
```

### Exemplo de Uso

```javascript
// Login
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

// Listar certificados
const certificates = await fetch('/api/certificates', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## 🔧 Extensão

### Funcionalidades

- **Detecção Automática**: Identifica sites de tribunais
- **Auto-Login**: Login automático com certificados
- **Captura de Telas**: Screenshots para auditoria
- **Notificações**: Alertas inteligentes
- **Atalhos**: Produtividade com teclado

### Atalhos de Teclado

- `Ctrl+Shift+C` - Selecionar certificado
- `Ctrl+Shift+L` - Auto-login
- `Ctrl+Shift+S` - Capturar tela
- `Ctrl+Shift+D` - Abrir dashboard

### Sites Suportados

- **TJ-RJ** - Tribunal de Justiça do Rio de Janeiro
- **TJSP** - Tribunal de Justiça de São Paulo
- **TRF-2** - Tribunal Regional Federal da 2ª Região
- **PJe** - Processo Judicial Eletrônico
- **E-SAJ** - Sistema de Automação da Justiça

---

## 🤖 LucIA - IA Jurídica

### Capacidades

A LucIA é uma assistente jurídica avançada com as seguintes capacidades:

#### Análise de Documentos
- **OCR Inteligente**: Extração de texto de imagens e PDFs
- **Classificação Automática**: Identifica tipos de documentos
- **Validação Jurídica**: Verifica conformidade e completude
- **Sugestões de Melhoria**: Recomendações baseadas em boas práticas

#### Consulta Processual
- **Busca Unificada**: Consulta em múltiplos tribunais
- **Acompanhamento Automático**: Monitoramento de movimentações
- **Alertas de Prazos**: Notificações de vencimentos
- **Relatórios Personalizados**: Dashboards por processo

#### Pesquisa Jurisprudencial
- **Base Atualizada**: Acesso a decisões recentes
- **Análise Semântica**: Busca por contexto e significado
- **Precedentes Relevantes**: Identificação de casos similares
- **Tendências Jurisprudenciais**: Análise de padrões decisórios

#### Geração de Petições
- **Templates Inteligentes**: Modelos adaptáveis
- **Fundamentação Automática**: Citação de leis e precedentes
- **Verificação de Prazos**: Validação de tempestividade
- **Formatação Profissional**: Padrões dos tribunais

### Exemplo de Uso

```javascript
// Fazer pergunta à LucIA
const lucia = new LuciaAI();
const response = await lucia.processQuestion(
  "Qual o prazo para contestação em ação de cobrança?",
  { tribunal: "TJRJ", tipo_processo: "cobranca" }
);

console.log(response.summary);
// "O prazo para contestação é de 15 dias úteis..."
```

---

## 📸 Screenshots

### Dashboard Principal
![Dashboard](./screenshots/dashboard.png)
*Dashboard com métricas em tempo real e gráficos interativos*

### Gestão de Certificados
![Certificados](./screenshots/certificates.png)
*Interface completa de gestão de certificados A1/A3*

### Extensão do Navegador
![Extensão](./screenshots/extension.png)
*Popup da extensão com funcionalidades de automação*

### LucIA em Ação
![LucIA](./screenshots/lucia.png)
*Assistente jurídica respondendo consultas complexas*

---

## 🗺️ Roadmap

### Versão 1.1 (Q2 2025)
- [ ] Integração blockchain completa
- [ ] App móvel (iOS/Android)
- [ ] API pública documentada
- [ ] Integração com mais tribunais

### Versão 1.2 (Q3 2025)
- [ ] Machine Learning avançado
- [ ] Análise preditiva de processos
- [ ] Integração com sistemas ERP
- [ ] Relatórios avançados com BI

### Versão 2.0 (Q4 2025)
- [ ] Arquitetura microserviços
- [ ] Kubernetes deployment
- [ ] Multi-tenancy
- [ ] Marketplace de plugins

---

## 🤝 Contribuição

Contribuições são sempre bem-vindas! Veja como você pode ajudar:

### Como Contribuir

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Diretrizes

- Siga os padrões de código existentes
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário
- Use commits semânticos (feat, fix, docs, etc.)

### Reportar Bugs

Use as [Issues do GitHub](https://github.com/fernandolisboaneto/CERTGUARD-AI-100-/issues) para reportar bugs. Inclua:

- Descrição detalhada do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots (se aplicável)
- Informações do ambiente

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 📞 Contato

**Fernando Lisboa Neto**
- GitHub: [@fernandolisboaneto](https://github.com/fernandolisboaneto)
- Email: fernando@certguard.ai
- LinkedIn: [Fernando Lisboa](https://linkedin.com/in/fernandolisboaneto)

**Link do Projeto:** https://github.com/fernandolisboaneto/CERTGUARD-AI-100-

---

## 🙏 Agradecimentos

- [Tailwind CSS](https://tailwindcss.com) - Framework CSS
- [Lucide Icons](https://lucide.dev) - Ícones
- [Chart.js](https://chartjs.org) - Gráficos
- [Flask](https://flask.palletsprojects.com) - Framework web
- [OpenAI](https://openai.com) - Tecnologia de IA

---

<div align="center">

**⭐ Se este projeto foi útil para você, considere dar uma estrela!**

![GitHub stars](https://img.shields.io/github/stars/fernandolisboaneto/CERTGUARD-AI-100-?style=social)
![GitHub forks](https://img.shields.io/github/forks/fernandolisboaneto/CERTGUARD-AI-100-?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/fernandolisboaneto/CERTGUARD-AI-100-?style=social)

</div>

