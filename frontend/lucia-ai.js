// LucIA - Assistente Jurídica com IA
// Sistema avançado de inteligência artificial para análise jurídica

class LuciaAI {
    constructor() {
        this.isActive = false;
        this.conversationHistory = [];
        this.currentAnalysis = null;
        this.knowledgeBase = this.initializeKnowledgeBase();
        this.init();
    }

    init() {
        console.log('LucIA - Assistente Jurídica iniciada');
        this.setupEventListeners();
        this.loadConversationHistory();
    }

    // Base de conhecimento jurídico
    initializeKnowledgeBase() {
        return {
            // Códigos e Leis
            laws: {
                'CPC': 'Código de Processo Civil',
                'CPP': 'Código de Processo Penal',
                'CC': 'Código Civil',
                'CLT': 'Consolidação das Leis do Trabalho',
                'CF': 'Constituição Federal',
                'LGPD': 'Lei Geral de Proteção de Dados',
                'ICP-Brasil': 'Infraestrutura de Chaves Públicas Brasileira'
            },

            // Tribunais
            tribunals: {
                'STF': 'Supremo Tribunal Federal',
                'STJ': 'Superior Tribunal de Justiça',
                'TST': 'Tribunal Superior do Trabalho',
                'TJ-RJ': 'Tribunal de Justiça do Rio de Janeiro',
                'TJSP': 'Tribunal de Justiça de São Paulo',
                'TRF-2': 'Tribunal Regional Federal da 2ª Região'
            },

            // Tipos de processo
            processTypes: [
                'Ação de Cobrança',
                'Ação de Despejo',
                'Ação Trabalhista',
                'Mandado de Segurança',
                'Habeas Corpus',
                'Ação Civil Pública',
                'Execução Fiscal',
                'Inventário',
                'Divórcio',
                'Usucapião'
            ],

            // Prazos processuais
            deadlines: {
                'contestacao': '15 dias',
                'apelacao': '15 dias',
                'embargos': '15 dias',
                'recurso_especial': '15 dias',
                'recurso_extraordinario': '15 dias',
                'agravo': '10 dias',
                'impugnacao': '15 dias'
            }
        };
    }

    // Configurar event listeners
    setupEventListeners() {
        // Escutar comandos de voz (simulado)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'L') {
                this.toggleVoiceMode();
            }
        });
    }

    // Carregar histórico de conversas
    loadConversationHistory() {
        const saved = localStorage.getItem('lucia_conversation_history');
        if (saved) {
            this.conversationHistory = JSON.parse(saved);
        }
    }

    // Salvar histórico de conversas
    saveConversationHistory() {
        localStorage.setItem('lucia_conversation_history', JSON.stringify(this.conversationHistory));
    }

    // Processar pergunta do usuário
    async processQuestion(question, context = {}) {
        const timestamp = new Date().toISOString();
        
        // Adicionar pergunta ao histórico
        this.conversationHistory.push({
            type: 'user',
            content: question,
            timestamp: timestamp,
            context: context
        });

        // Simular processamento de IA
        const response = await this.generateResponse(question, context);

        // Adicionar resposta ao histórico
        this.conversationHistory.push({
            type: 'lucia',
            content: response,
            timestamp: new Date().toISOString(),
            confidence: response.confidence || 0.95
        });

        this.saveConversationHistory();
        return response;
    }

    // Gerar resposta inteligente
    async generateResponse(question, context) {
        // Simular delay de processamento
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

        const lowerQuestion = question.toLowerCase();
        
        // Análise de documentos
        if (lowerQuestion.includes('analisar') || lowerQuestion.includes('documento')) {
            return this.analyzeDocument(question, context);
        }

        // Consulta de processos
        if (lowerQuestion.includes('processo') || lowerQuestion.includes('consultar')) {
            return this.consultProcess(question, context);
        }

        // Prazos processuais
        if (lowerQuestion.includes('prazo')) {
            return this.checkDeadlines(question, context);
        }

        // Jurisprudência
        if (lowerQuestion.includes('jurisprudencia') || lowerQuestion.includes('precedente')) {
            return this.searchJurisprudence(question, context);
        }

        // Certificados digitais
        if (lowerQuestion.includes('certificado') || lowerQuestion.includes('assinatura')) {
            return this.helpWithCertificates(question, context);
        }

        // Petições
        if (lowerQuestion.includes('peticao') || lowerQuestion.includes('modelo')) {
            return this.generatePetition(question, context);
        }

        // Resposta geral
        return this.generateGeneralResponse(question, context);
    }

    // Analisar documento
    analyzeDocument(question, context) {
        const analyses = [
            {
                type: 'Contrato de Prestação de Serviços',
                summary: 'Documento analisado com sucesso. Identifiquei 3 cláusulas que podem necessitar revisão.',
                issues: [
                    'Cláusula 5.2: Prazo de pagamento muito extenso (45 dias)',
                    'Cláusula 8.1: Falta especificação de multa por atraso',
                    'Cláusula 12: Foro de eleição pode ser questionado'
                ],
                suggestions: [
                    'Reduzir prazo de pagamento para 30 dias',
                    'Incluir multa de 2% + juros de 1% ao mês',
                    'Considerar foro do domicílio do contratante'
                ],
                confidence: 0.92
            },
            {
                type: 'Petição Inicial',
                summary: 'Petição analisada. Estrutura adequada, mas alguns pontos podem ser melhorados.',
                issues: [
                    'Fundamentação jurídica pode ser mais robusta',
                    'Faltam precedentes do STJ sobre o tema',
                    'Pedido liminar precisa de melhor justificativa'
                ],
                suggestions: [
                    'Incluir artigos 186 e 927 do CC',
                    'Citar REsp 1.234.567/SP',
                    'Demonstrar periculum in mora'
                ],
                confidence: 0.88
            }
        ];

        return analyses[Math.floor(Math.random() * analyses.length)];
    }

    // Consultar processo
    consultProcess(question, context) {
        const processes = [
            {
                number: '1234567-89.2024.8.19.0001',
                court: 'TJ-RJ',
                status: 'Aguardando julgamento',
                lastMovement: 'Conclusos para julgamento',
                date: '2025-01-20',
                nextDeadline: 'Não há prazos pendentes',
                parties: {
                    plaintiff: 'João Silva Santos',
                    defendant: 'Empresa XYZ Ltda'
                },
                confidence: 0.96
            },
            {
                number: '9876543-21.2024.5.02.0001',
                court: 'TRT-2',
                status: 'Sentença proferida',
                lastMovement: 'Sentença de procedência parcial',
                date: '2025-01-15',
                nextDeadline: 'Prazo para recurso: até 30/01/2025',
                parties: {
                    plaintiff: 'Maria Costa Oliveira',
                    defendant: 'Construtora ABC S/A'
                },
                confidence: 0.94
            }
        ];

        return {
            type: 'Consulta Processual',
            results: processes,
            summary: `Encontrei ${processes.length} processos relacionados à sua consulta.`,
            confidence: 0.95
        };
    }

    // Verificar prazos
    checkDeadlines(question, context) {
        const deadlines = [
            {
                process: '1234567-89.2024.8.19.0001',
                type: 'Contestação',
                deadline: '2025-02-05',
                daysLeft: 10,
                priority: 'Alta',
                status: 'Pendente'
            },
            {
                process: '9876543-21.2024.5.02.0001',
                type: 'Recurso Ordinário',
                deadline: '2025-01-30',
                daysLeft: 4,
                priority: 'Crítica',
                status: 'Pendente'
            },
            {
                process: '5555555-55.2024.8.19.0002',
                type: 'Tríplica',
                deadline: '2025-02-15',
                daysLeft: 20,
                priority: 'Média',
                status: 'Pendente'
            }
        ];

        return {
            type: 'Controle de Prazos',
            deadlines: deadlines,
            summary: `Você tem ${deadlines.length} prazos pendentes. ${deadlines.filter(d => d.daysLeft <= 5).length} são críticos.`,
            recommendations: [
                'Priorize o recurso ordinário (4 dias restantes)',
                'Prepare a contestação com antecedência',
                'Configure alertas automáticos'
            ],
            confidence: 0.98
        };
    }

    // Buscar jurisprudência
    searchJurisprudence(question, context) {
        const jurisprudence = [
            {
                court: 'STJ',
                number: 'REsp 1.234.567/SP',
                date: '2024-11-15',
                summary: 'Responsabilidade civil. Dano moral. Critérios para fixação do quantum indenizatório.',
                relevance: 'Alta',
                keywords: ['dano moral', 'quantum', 'responsabilidade civil']
            },
            {
                court: 'STF',
                number: 'RE 987.654/RJ',
                date: '2024-10-20',
                summary: 'Direito constitucional. Devido processo legal. Ampla defesa e contraditório.',
                relevance: 'Média',
                keywords: ['devido processo', 'ampla defesa', 'contraditório']
            },
            {
                court: 'TST',
                number: 'RR 555.666/MG',
                date: '2024-12-01',
                summary: 'Direito do trabalho. Horas extras. Cálculo e incidência de adicionais.',
                relevance: 'Alta',
                keywords: ['horas extras', 'adicional', 'cálculo']
            }
        ];

        return {
            type: 'Pesquisa Jurisprudencial',
            results: jurisprudence,
            summary: `Encontrei ${jurisprudence.length} precedentes relevantes para sua consulta.`,
            filters: {
                courts: ['STJ', 'STF', 'TST'],
                dateRange: 'Últimos 6 meses',
                relevance: 'Alta e Média'
            },
            confidence: 0.91
        };
    }

    // Ajuda com certificados
    helpWithCertificates(question, context) {
        const tips = [
            {
                topic: 'Instalação de Certificado A1',
                steps: [
                    'Baixe o arquivo .pfx do seu certificado',
                    'Clique duas vezes no arquivo para iniciar a instalação',
                    'Digite a senha do certificado quando solicitado',
                    'Selecione "Repositório de Certificados Pessoais"',
                    'Conclua a instalação e teste no navegador'
                ]
            },
            {
                topic: 'Configuração de Token A3',
                steps: [
                    'Instale os drivers do fabricante do token',
                    'Conecte o token na porta USB',
                    'Digite o PIN quando solicitado',
                    'Verifique se o certificado aparece no navegador',
                    'Configure o token como padrão para assinaturas'
                ]
            },
            {
                topic: 'Resolução de Problemas',
                solutions: [
                    'Certificado não reconhecido: Verifique se está na validade',
                    'Erro de PIN: Confirme se não está bloqueado',
                    'Token não detectado: Reinstale os drivers',
                    'Assinatura inválida: Verifique a cadeia de certificação'
                ]
            }
        ];

        return {
            type: 'Suporte a Certificados Digitais',
            tips: tips,
            summary: 'Aqui estão as orientações para resolver problemas com certificados digitais.',
            quickActions: [
                'Testar certificado atual',
                'Verificar validade',
                'Configurar backup',
                'Agendar renovação'
            ],
            confidence: 0.97
        };
    }

    // Gerar petição
    generatePetition(question, context) {
        const templates = [
            {
                type: 'Ação de Cobrança',
                structure: [
                    'Qualificação das partes',
                    'Dos fatos',
                    'Do direito',
                    'Dos pedidos',
                    'Do valor da causa',
                    'Das provas',
                    'Requerimentos finais'
                ],
                estimatedTime: '2-3 horas',
                complexity: 'Média'
            },
            {
                type: 'Mandado de Segurança',
                structure: [
                    'Impetrante e autoridade coatora',
                    'Do direito líquido e certo',
                    'Do ato coator',
                    'Da ilegalidade/abuso de poder',
                    'Da liminar',
                    'Dos pedidos',
                    'Notificação da autoridade'
                ],
                estimatedTime: '3-4 horas',
                complexity: 'Alta'
            }
        ];

        return {
            type: 'Geração de Petições',
            templates: templates,
            summary: 'Posso ajudar você a estruturar diferentes tipos de petições.',
            features: [
                'Modelos pré-formatados',
                'Fundamentação jurídica automática',
                'Verificação de prazos',
                'Sugestões de jurisprudência'
            ],
            confidence: 0.89
        };
    }

    // Resposta geral
    generateGeneralResponse(question, context) {
        const responses = [
            {
                content: 'Posso ajudar você com análise de documentos, consulta de processos, controle de prazos, pesquisa jurisprudencial e muito mais. Como posso auxiliá-lo hoje?',
                suggestions: [
                    'Analisar um documento',
                    'Consultar processo',
                    'Verificar prazos',
                    'Buscar jurisprudência'
                ]
            },
            {
                content: 'Sou especializada em direito brasileiro e posso auxiliar com questões processuais, análise de contratos, petições e certificados digitais. O que você gostaria de saber?',
                suggestions: [
                    'Ajuda com certificados',
                    'Modelos de petição',
                    'Cálculos processuais',
                    'Orientações práticas'
                ]
            }
        ];

        const response = responses[Math.floor(Math.random() * responses.length)];
        return {
            type: 'Resposta Geral',
            ...response,
            confidence: 0.85
        };
    }

    // Análise OCR de documento
    async performOCR(imageData) {
        // Simular processamento OCR
        await new Promise(resolve => setTimeout(resolve, 3000));

        return {
            text: `TRIBUNAL DE JUSTIÇA DO ESTADO DO RIO DE JANEIRO
            
PROCESSO Nº 1234567-89.2024.8.19.0001

AUTOR: João Silva Santos
RÉU: Empresa XYZ Ltda

SENTENÇA

Vistos, etc.

Trata-se de ação de cobrança proposta por João Silva Santos em face de Empresa XYZ Ltda, objetivando o recebimento da quantia de R$ 15.000,00 (quinze mil reais), decorrente de prestação de serviços advocatícios.

[...resto do documento...]`,
            confidence: 0.94,
            pages: 3,
            words: 1247,
            processingTime: '2.8 segundos'
        };
    }

    // Insights preditivos
    generatePredictiveInsights(processData) {
        const insights = [
            {
                type: 'Probabilidade de Sucesso',
                value: '78%',
                factors: [
                    'Jurisprudência favorável (85%)',
                    'Documentação completa (90%)',
                    'Histórico do magistrado (65%)'
                ]
            },
            {
                type: 'Tempo Estimado',
                value: '8-12 meses',
                factors: [
                    'Complexidade média',
                    'Vara com movimento normal',
                    'Possibilidade de acordo (40%)'
                ]
            },
            {
                type: 'Valor Provável',
                value: 'R$ 12.000 - R$ 18.000',
                factors: [
                    'Precedentes similares',
                    'Critérios do tribunal',
                    'Margem de negociação'
                ]
            }
        ];

        return {
            insights: insights,
            confidence: 0.82,
            lastUpdate: new Date().toISOString(),
            dataSource: 'Análise de 15.000+ processos similares'
        };
    }

    // Modo de voz (simulado)
    toggleVoiceMode() {
        this.isVoiceMode = !this.isVoiceMode;
        
        if (this.isVoiceMode) {
            this.showVoiceInterface();
        } else {
            this.hideVoiceInterface();
        }
    }

    showVoiceInterface() {
        // Criar interface de voz
        const voiceUI = document.createElement('div');
        voiceUI.id = 'lucia-voice-ui';
        voiceUI.innerHTML = `
            <div style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 50px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                z-index: 10000;
                display: flex;
                align-items: center;
                animation: pulse 2s infinite;
            ">
                <div style="margin-right: 12px; font-size: 24px;">🎤</div>
                <div>
                    <div style="font-weight: 600; font-size: 14px;">LucIA Escutando...</div>
                    <div style="font-size: 12px; opacity: 0.8;">Fale sua pergunta</div>
                </div>
            </div>
            <style>
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
            </style>
        `;

        document.body.appendChild(voiceUI);

        // Simular reconhecimento de voz
        setTimeout(() => {
            this.hideVoiceInterface();
            this.processVoiceCommand("Como está o andamento do processo 1234567?");
        }, 3000);
    }

    hideVoiceInterface() {
        const voiceUI = document.getElementById('lucia-voice-ui');
        if (voiceUI) {
            voiceUI.remove();
        }
    }

    async processVoiceCommand(command) {
        const response = await this.processQuestion(command, { source: 'voice' });
        this.speakResponse(response);
    }

    speakResponse(response) {
        // Simular síntese de voz
        console.log('LucIA falando:', response.content || response.summary);
        
        // Mostrar resposta visual
        const speechUI = document.createElement('div');
        speechUI.innerHTML = `
            <div style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: white;
                border: 2px solid #667eea;
                padding: 16px;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                z-index: 10000;
                max-width: 300px;
                animation: slideUp 0.3s ease-out;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="margin-right: 8px; font-size: 20px;">🤖</div>
                    <div style="font-weight: 600; color: #667eea;">LucIA</div>
                </div>
                <div style="color: #374151; font-size: 14px; line-height: 1.4;">
                    ${response.content || response.summary}
                </div>
            </div>
            <style>
                @keyframes slideUp {
                    from { transform: translateY(100%); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
            </style>
        `;

        document.body.appendChild(speechUI);

        setTimeout(() => {
            speechUI.remove();
        }, 5000);
    }

    // Exportar dados
    exportConversation() {
        const data = {
            conversation: this.conversationHistory,
            timestamp: new Date().toISOString(),
            version: '1.0.0'
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `lucia-conversation-${Date.now()}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
    }

    // Limpar histórico
    clearHistory() {
        this.conversationHistory = [];
        this.saveConversationHistory();
    }

    // Obter estatísticas
    getStatistics() {
        return {
            totalQuestions: this.conversationHistory.filter(m => m.type === 'user').length,
            totalResponses: this.conversationHistory.filter(m => m.type === 'lucia').length,
            averageConfidence: this.conversationHistory
                .filter(m => m.type === 'lucia' && m.confidence)
                .reduce((acc, m) => acc + m.confidence, 0) / 
                this.conversationHistory.filter(m => m.type === 'lucia' && m.confidence).length,
            topicsDiscussed: [...new Set(this.conversationHistory.map(m => m.context?.topic).filter(Boolean))],
            firstInteraction: this.conversationHistory[0]?.timestamp,
            lastInteraction: this.conversationHistory[this.conversationHistory.length - 1]?.timestamp
        };
    }
}

// Inicializar LucIA
window.LuciaAI = LuciaAI;

// Exportar para uso global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LuciaAI;
}

