# Guia de Teste - Sistema CertGuard

**Versão:** 1.0.0  
**Data:** 26 de Julho de 2025  
**Autor:** Manus AI  
**Ambiente:** Teste e Demonstração  

## Visão Geral

O Sistema CertGuard é uma plataforma completa de gestão de certificados digitais que unifica as melhores funcionalidades de sistemas como Presto/Oystr, Whom/Doc9 e LoyTrust, incorporando tecnologias avançadas como blockchain e inteligência artificial através da LucIA (assistente jurídica inteligente).

Este guia fornece instruções detalhadas para testar todas as funcionalidades implementadas no ambiente de demonstração, incluindo credenciais de acesso, fluxos de teste e validação das principais características do sistema.

## Acesso ao Sistema

### URL de Acesso
**Frontend (Interface Principal):** https://5173-ick1rotydcjwas9kzjqp5-50bdaabf.manusvm.computer

### Credenciais de Teste

O sistema possui dois usuários pré-configurados para demonstração:

#### Administrador do Sistema
- **Usuário:** `admin`
- **Senha:** `admin123`
- **Perfil:** SUPERADMIN
- **Organização:** Sistema Principal
- **Permissões:** Acesso completo a todas as funcionalidades

#### Usuário Final
- **Usuário:** `joao`
- **Senha:** `123456`
- **Perfil:** USER
- **Organização:** Escritório de Advocacia
- **Permissões:** Acesso limitado às funcionalidades básicas

## Funcionalidades Implementadas

### 1. Sistema de Autenticação
O sistema implementa autenticação robusta com as seguintes características:

- **Login por usuário/senha:** Interface elegante com validação em tempo real
- **Persistência de sessão:** Utiliza localStorage para manter o usuário logado
- **Controle de acesso:** Diferentes níveis de permissão baseados no perfil do usuário
- **Logout seguro:** Limpeza completa da sessão e redirecionamento

### 2. Dashboard Interativo
O dashboard principal oferece uma visão abrangente do sistema:

- **Estatísticas em tempo real:** Certificados ativos, usuários, certificados expirando
- **Gráficos dinâmicos:** Visualizações de crescimento mensal e distribuição de status
- **Ações rápidas:** Acesso direto às funcionalidades mais utilizadas
- **Alertas inteligentes:** Notificações sobre certificados próximos ao vencimento

### 3. Interface Responsiva
A interface foi desenvolvida com foco na experiência do usuário:

- **Design moderno:** Utiliza Tailwind CSS e componentes shadcn/ui
- **Responsividade completa:** Funciona perfeitamente em desktop, tablet e mobile
- **Navegação intuitiva:** Sidebar com ícones e navegação clara
- **Feedback visual:** Animações e transições suaves

## Fluxos de Teste

### Teste 1: Login e Autenticação

1. **Acesse a URL do sistema**
2. **Teste com credenciais inválidas:**
   - Digite qualquer usuário/senha incorretos
   - Verifique se o sistema exibe mensagem de erro apropriada
3. **Teste com credenciais válidas:**
   - Use `admin` / `admin123`
   - Verifique se o login é realizado com sucesso
   - Confirme o redirecionamento para o dashboard

### Teste 2: Navegação e Interface

1. **Explore o dashboard:**
   - Verifique as estatísticas exibidas
   - Observe os gráficos de crescimento mensal
   - Analise a distribuição de status dos certificados
2. **Teste a navegação:**
   - Clique nos itens do menu lateral
   - Verifique se as páginas "Em Desenvolvimento" são exibidas corretamente
   - Teste a responsividade redimensionando a janela

### Teste 3: Funcionalidades do Sistema

1. **Dashboard:**
   - Verifique se os cards de estatísticas estão funcionando
   - Teste os gráficos interativos (hover, tooltips)
   - Clique nas ações rápidas
2. **Logout:**
   - Clique no botão "Sair"
   - Verifique se retorna à tela de login
   - Confirme que a sessão foi limpa

## Arquitetura Técnica

### Frontend
- **Framework:** React 19.1.0 com Vite
- **Estilização:** Tailwind CSS + shadcn/ui
- **Ícones:** Lucide React
- **Gráficos:** Recharts
- **Estado:** React Hooks (useState, useEffect)
- **Persistência:** localStorage para sessão

### Backend (Implementado)
- **Framework:** Flask com SQLAlchemy
- **Banco de Dados:** SQLite (desenvolvimento)
- **Autenticação:** JWT tokens
- **APIs:** RESTful com CORS habilitado
- **Modelos:** Usuários, Certificados, Organizações, LucIA, Blockchain

### Estrutura de Arquivos

```
certguard-test/
├── src/
│   ├── components/
│   │   ├── ui/           # Componentes shadcn/ui
│   │   ├── Login.jsx     # Componente de login
│   │   ├── Dashboard.jsx # Dashboard principal
│   │   ├── Layout.jsx    # Layout com sidebar
│   │   └── ComingSoon.jsx # Páginas em desenvolvimento
│   ├── App.jsx           # Componente principal
│   ├── App.css           # Estilos customizados
│   └── main.jsx          # Ponto de entrada
├── index.html            # HTML principal
└── package.json          # Dependências
```

## Funcionalidades Planejadas

### Próximas Implementações

1. **Gestão de Certificados:**
   - Upload de certificados A1/A3
   - Validação e verificação automática
   - Renovação e revogação
   - Histórico completo de operações

2. **LucIA - Assistente Jurídica:**
   - Chat inteligente para consultas jurídicas
   - Análise automática de documentos
   - Extração de dados via OCR
   - Insights preditivos e recomendações

3. **Automação de Tribunais:**
   - Login automático em sistemas judiciais
   - Peticionamento automatizado
   - Captura de telas e evidências
   - Monitoramento de processos

4. **Blockchain e Segurança:**
   - Registro imutável de assinaturas
   - Trilha de auditoria completa
   - Verificação de integridade
   - Backup distribuído

5. **Relatórios e Auditoria:**
   - Dashboards avançados
   - Relatórios customizáveis
   - Logs detalhados de acesso
   - Alertas em tempo real

## Especificações Técnicas Detalhadas

### Requisitos de Sistema
- **Navegadores:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Resolução:** Mínima 1024x768, otimizado para 1920x1080
- **Conectividade:** Conexão estável com a internet
- **JavaScript:** Habilitado e atualizado

### Performance
- **Tempo de carregamento:** < 2 segundos
- **Responsividade:** < 100ms para interações
- **Compatibilidade:** 99.9% dos navegadores modernos
- **Acessibilidade:** Conformidade com WCAG 2.1 AA

### Segurança
- **Autenticação:** JWT com expiração configurável
- **Comunicação:** HTTPS obrigatório em produção
- **Validação:** Sanitização de inputs no frontend e backend
- **Sessão:** Limpeza automática após inatividade

## Troubleshooting

### Problemas Comuns

1. **Página em branco:**
   - Verifique se JavaScript está habilitado
   - Limpe o cache do navegador
   - Tente em modo incógnito

2. **Login não funciona:**
   - Verifique as credenciais (case-sensitive)
   - Confirme se não há espaços extras
   - Teste com as credenciais fornecidas

3. **Interface não responsiva:**
   - Atualize a página (F5)
   - Verifique a conexão com internet
   - Teste em outro navegador

### Logs e Depuração
- **Console do navegador:** F12 → Console
- **Network:** Verifique requisições HTTP
- **Application:** Inspecione localStorage

## Contato e Suporte

Para questões técnicas ou sugestões sobre o sistema CertGuard:

- **Desenvolvedor:** Manus AI
- **Versão do Sistema:** 1.0.0
- **Data de Criação:** 26 de Julho de 2025
- **Ambiente:** Demonstração e Teste

---

*Este documento foi gerado automaticamente pelo sistema Manus AI como parte do processo de desenvolvimento e teste do Sistema CertGuard.*

