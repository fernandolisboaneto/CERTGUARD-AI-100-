/**
 * CertGuard AI - LucIA Advanced Features
 * Funcionalidades avançadas de IA, análise comportamental e auditoria
 */

// Configuração da API
const API_BASE_URL = 'http://localhost:5000/api';

// Cache de dados
let securityCache = {
    recentEvents: [],
    userProfiles: {},
    anomalies: [],
    lastUpdate: null
};

/**
 * Faz pergunta avançada à LucIA
 */
async function askAdvancedLucia() {
    const question = document.getElementById('luciaQuestion').value;
    if (!question.trim()) {
        alert('Por favor, digite uma pergunta');
        return;
    }

    const chatContainer = document.getElementById('luciaChat');
    
    // Adiciona pergunta do usuário
    chatContainer.innerHTML += `
        <div class="mb-4 text-right">
            <div class="inline-block bg-blue-500 text-white p-3 rounded-lg max-w-xs">
                ${question}
            </div>
        </div>
    `;

    // Mostra loading
    chatContainer.innerHTML += `
        <div class="mb-4" id="loading">
            <div class="inline-block bg-gray-200 p-3 rounded-lg">
                <div class="flex items-center space-x-2">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                    <span>LucIA está analisando dados em tempo real...</span>
                </div>
            </div>
        </div>
    `;

    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        // Faz análise avançada baseada na pergunta
        const response = await analyzeSecurityQuestion(question);
        
        // Remove loading
        document.getElementById('loading').remove();
        
        // Adiciona resposta da LucIA
        chatContainer.innerHTML += `
            <div class="mb-4">
                <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                        L
                    </div>
                    <div class="bg-gray-100 p-3 rounded-lg max-w-md">
                        <div class="text-sm text-gray-600 mb-1">LucIA - Assistente de Segurança IA</div>
                        <div class="whitespace-pre-line">${response}</div>
                        <div class="text-xs text-gray-500 mt-2">
                            Análise baseada em ${getAnalysisDataSources(question).join(', ')}
                        </div>
                    </div>
                </div>
            </div>
        `;

        chatContainer.scrollTop = chatContainer.scrollHeight;
        document.getElementById('luciaQuestion').value = '';

    } catch (error) {
        document.getElementById('loading').remove();
        chatContainer.innerHTML += `
            <div class="mb-4">
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    Erro ao processar pergunta: ${error.message}
                </div>
            </div>
        `;
    }
}

/**
 * Analisa pergunta de segurança usando dados reais
 */
async function analyzeSecurityQuestion(question) {
    const questionLower = question.toLowerCase();
    
    // Atualiza cache de dados se necessário
    await updateSecurityCache();
    
    // Análise de acessos de usuários
    if (questionLower.includes('quem') && (questionLower.includes('acessou') || questionLower.includes('logou'))) {
        return await analyzeUserAccess(question);
    }
    
    // Análise de IPs suspeitos
    if (questionLower.includes('ip') && (questionLower.includes('diferente') || questionLower.includes('suspeito'))) {
        return await analyzeIPActivity(question);
    }
    
    // Análise de certificados
    if (questionLower.includes('certificado') || questionLower.includes('assinatura')) {
        return await analyzeCertificateUsage(question);
    }
    
    // Análise de horários
    if (questionLower.includes('horário') && (questionLower.includes('estranho') || questionLower.includes('fora'))) {
        return await analyzeTimePatterns(question);
    }
    
    // Análise de performance
    if (questionLower.includes('performance') || questionLower.includes('lento')) {
        return await analyzePerformance(question);
    }
    
    // Relatórios e estatísticas
    if (questionLower.includes('relatório') || questionLower.includes('estatística')) {
        return await generateSecurityReport(question);
    }
    
    // Análise de anomalias
    if (questionLower.includes('anomalia') || questionLower.includes('suspeito')) {
        return await analyzeAnomalies(question);
    }
    
    // Análise geral
    return await generateGeneralAnalysis(question);
}

/**
 * Analisa acessos de usuários
 */
async function analyzeUserAccess(question) {
    const userData = await getUserActivityData();
    
    let response = "🔍 **Análise de Acessos de Usuários**\n\n";
    
    // Últimos acessos
    response += "**Atividade Recente (Últimas 24h):**\n";
    userData.recentActivity.forEach(user => {
        const status = user.suspicious ? "⚠️" : "✅";
        response += `${status} ${user.name} (${user.username})\n`;
        response += `   • ${user.loginCount} acessos de ${user.uniqueIPs} IPs diferentes\n`;
        response += `   • Último acesso: ${user.lastLogin}\n`;
        if (user.suspicious) {
            response += `   • 🚨 ALERTA: ${user.suspiciousReason}\n`;
        }
        response += "\n";
    });
    
    // Alertas de segurança
    const alerts = userData.securityAlerts;
    if (alerts.length > 0) {
        response += "**🚨 Alertas de Segurança:**\n";
        alerts.forEach(alert => {
            response += `• ${alert.severity.toUpperCase()}: ${alert.description}\n`;
        });
        response += "\n";
    }
    
    response += "**Recomendações:**\n";
    response += "• Monitorar usuários com múltiplos IPs\n";
    response += "• Investigar tentativas de login falhadas\n";
    response += "• Implementar MFA para usuários de alto risco";
    
    return response;
}

/**
 * Analisa atividade de IPs
 */
async function analyzeIPActivity(question) {
    const ipData = await getIPAnalysisData();
    
    let response = "🌐 **Análise de Atividade de IPs**\n\n";
    
    // IPs suspeitos
    response += "**IPs com Atividade Suspeita:**\n";
    ipData.suspiciousIPs.forEach(ip => {
        response += `🚨 ${ip.address} (${ip.location})\n`;
        response += `   • ${ip.attempts} tentativas, ${ip.failures} falhas\n`;
        response += `   • Usuários afetados: ${ip.users.join(', ')}\n`;
        response += `   • Risco: ${ip.riskLevel}\n\n`;
    });
    
    // Geolocalização anômala
    if (ipData.geoAnomalies.length > 0) {
        response += "**Anomalias Geográficas:**\n";
        ipData.geoAnomalies.forEach(anomaly => {
            response += `• ${anomaly.user}: Acesso de ${anomaly.country} (incomum)\n`;
        });
        response += "\n";
    }
    
    // Estatísticas
    response += "**Estatísticas:**\n";
    response += `• Total de IPs únicos: ${ipData.totalUniqueIPs}\n`;
    response += `• IPs bloqueados: ${ipData.blockedIPs}\n`;
    response += `• Taxa de sucesso média: ${ipData.successRate}%\n\n`;
    
    response += "**Ações Recomendadas:**\n";
    response += "• Bloquear IPs com alta taxa de falha\n";
    response += "• Implementar geo-blocking para países de risco\n";
    response += "• Configurar alertas para novos IPs por usuário";
    
    return response;
}

/**
 * Analisa uso de certificados
 */
async function analyzeCertificateUsage(question) {
    const certData = await getCertificateAnalysisData();
    
    let response = "📜 **Análise de Uso de Certificados**\n\n";
    
    // Status dos certificados
    response += "**Status dos Certificados:**\n";
    certData.certificates.forEach(cert => {
        const statusIcon = cert.status === 'active' ? '✅' : cert.status === 'expired' ? '⏰' : '❌';
        response += `${statusIcon} ${cert.subjectName}\n`;
        response += `   • Tipo: ${cert.type} | Serial: ${cert.serialNumber}\n`;
        response += `   • Uso recente: ${cert.recentUsage} assinaturas\n`;
        response += `   • Válido até: ${cert.validUntil}\n`;
        if (cert.alerts.length > 0) {
            response += `   • ⚠️ ${cert.alerts.join(', ')}\n`;
        }
        response += "\n";
    });
    
    // Atividade suspeita
    if (certData.suspiciousActivity.length > 0) {
        response += "**🚨 Atividade Suspeita:**\n";
        certData.suspiciousActivity.forEach(activity => {
            response += `• ${activity.description}\n`;
            response += `  Usuário: ${activity.user} | Horário: ${activity.timestamp}\n`;
        });
        response += "\n";
    }
    
    // Métricas de uso
    response += "**Métricas de Uso:**\n";
    response += `• Total de assinaturas hoje: ${certData.metrics.totalSignatures}\n`;
    response += `• Certificado mais usado: ${certData.metrics.mostUsed}\n`;
    response += `• Tempo médio de assinatura: ${certData.metrics.avgSignTime}s\n\n`;
    
    response += "**Recomendações:**\n";
    response += "• Renovar certificados próximos ao vencimento\n";
    response += "• Monitorar uso de certificados revogados\n";
    response += "• Implementar alertas para uso fora do horário";
    
    return response;
}

/**
 * Analisa padrões temporais
 */
async function analyzeTimePatterns(question) {
    const timeData = await getTimeAnalysisData();
    
    let response = "🕐 **Análise de Padrões Temporais**\n\n";
    
    // Atividades fora do horário
    response += "**Atividades Fora do Horário Comercial:**\n";
    timeData.offHoursActivity.forEach(activity => {
        const riskIcon = activity.riskLevel === 'high' ? '🚨' : activity.riskLevel === 'medium' ? '⚠️' : 'ℹ️';
        response += `${riskIcon} ${activity.timestamp} - ${activity.user}\n`;
        response += `   • Ação: ${activity.action}\n`;
        response += `   • IP: ${activity.ip}\n`;
        response += `   • Risco: ${activity.riskLevel}\n\n`;
    });
    
    // Padrões de horário por usuário
    response += "**Padrões de Horário por Usuário:**\n";
    timeData.userPatterns.forEach(pattern => {
        response += `• ${pattern.user}: ${pattern.usualHours}\n`;
        if (pattern.anomalies > 0) {
            response += `  ⚠️ ${pattern.anomalies} acessos fora do padrão\n`;
        }
    });
    response += "\n";
    
    // Estatísticas temporais
    response += "**Estatísticas:**\n";
    response += `• Horário de pico: ${timeData.peakHour}\n`;
    response += `• Atividade noturna: ${timeData.nightActivity}%\n`;
    response += `• Fins de semana: ${timeData.weekendActivity}%\n\n`;
    
    response += "**Recomendações:**\n";
    response += "• Configurar alertas para atividades após 22h\n";
    response += "• Implementar aprovação adicional para fins de semana\n";
    response += "• Monitorar padrões anômalos de usuários";
    
    return response;
}

/**
 * Analisa performance do sistema
 */
async function analyzePerformance(question) {
    const perfData = await getPerformanceData();
    
    let response = "⚡ **Análise de Performance do Sistema**\n\n";
    
    // Métricas gerais
    response += "**Métricas Gerais:**\n";
    response += `• Tempo médio de resposta: ${perfData.avgResponseTime}ms\n`;
    response += `• Uptime: ${perfData.uptime}%\n`;
    response += `• Requests por minuto: ${perfData.requestsPerMinute}\n`;
    response += `• Taxa de erro: ${perfData.errorRate}%\n\n`;
    
    // Operações mais lentas
    response += "**Operações Mais Lentas:**\n";
    perfData.slowOperations.forEach(op => {
        response += `• ${op.operation}: ${op.avgTime}ms (${op.count} execuções)\n`;
    });
    response += "\n";
    
    // Gargalos identificados
    if (perfData.bottlenecks.length > 0) {
        response += "**🚨 Gargalos Identificados:**\n";
        perfData.bottlenecks.forEach(bottleneck => {
            response += `• ${bottleneck.component}: ${bottleneck.description}\n`;
        });
        response += "\n";
    }
    
    // Tendências
    response += "**Tendências:**\n";
    response += `• Performance vs. ontem: ${perfData.trend > 0 ? '📈' : '📉'} ${Math.abs(perfData.trend)}%\n`;
    response += `• Pico de uso: ${perfData.peakUsage}\n\n`;
    
    response += "**Recomendações:**\n";
    response += "• Otimizar operações de assinatura digital\n";
    response += "• Implementar cache para consultas frequentes\n";
    response += "• Monitorar uso de recursos em tempo real";
    
    return response;
}

/**
 * Gera relatório de segurança
 */
async function generateSecurityReport(question) {
    const reportData = await getSecurityReportData();
    
    let response = "📊 **Relatório de Segurança - Últimos 7 Dias**\n\n";
    
    // Resumo executivo
    response += "**📋 Resumo Executivo:**\n";
    response += `• ${reportData.totalEvents} eventos de segurança processados\n`;
    response += `• ${reportData.criticalEvents} incidentes críticos\n`;
    response += `• ${reportData.anomalies} anomalias comportamentais\n`;
    response += `• ${reportData.uptime}% de disponibilidade\n\n`;
    
    // Principais riscos
    response += "**🚨 Principais Riscos Identificados:**\n";
    reportData.topRisks.forEach((risk, index) => {
        response += `${index + 1}. ${risk.description} (${risk.severity})\n`;
    });
    response += "\n";
    
    // Usuários de alto risco
    if (reportData.highRiskUsers.length > 0) {
        response += "**👤 Usuários de Alto Risco:**\n";
        reportData.highRiskUsers.forEach(user => {
            response += `• ${user.name}: ${user.riskFactors.join(', ')}\n`;
        });
        response += "\n";
    }
    
    // Tendências
    response += "**📈 Tendências:**\n";
    response += `• Tentativas de acesso: ${reportData.trends.accessAttempts}\n`;
    response += `• Uso de certificados: ${reportData.trends.certificateUsage}\n`;
    response += `• Atividade suspeita: ${reportData.trends.suspiciousActivity}\n\n`;
    
    // Recomendações estratégicas
    response += "**🎯 Recomendações Estratégicas:**\n";
    reportData.recommendations.forEach(rec => {
        response += `• ${rec}\n`;
    });
    
    return response;
}

/**
 * Analisa anomalias detectadas
 */
async function analyzeAnomalies(question) {
    const anomalyData = await getAnomalyData();
    
    let response = "🔍 **Análise de Anomalias Detectadas**\n\n";
    
    // Anomalias críticas
    if (anomalyData.critical.length > 0) {
        response += "**🚨 ANOMALIAS CRÍTICAS:**\n";
        anomalyData.critical.forEach(anomaly => {
            response += `• ${anomaly.description}\n`;
            response += `  Usuário: ${anomaly.user} | Detectado: ${anomaly.timestamp}\n`;
            response += `  Ação requerida: ${anomaly.action}\n\n`;
        });
    }
    
    // Anomalias comportamentais
    response += "**👤 Anomalias Comportamentais:**\n";
    anomalyData.behavioral.forEach(anomaly => {
        response += `• ${anomaly.user}: ${anomaly.pattern}\n`;
        response += `  Desvio: ${anomaly.deviation} (${anomaly.confidence}% confiança)\n`;
    });
    response += "\n";
    
    // Anomalias de rede
    response += "**🌐 Anomalias de Rede:**\n";
    anomalyData.network.forEach(anomaly => {
        response += `• ${anomaly.type}: ${anomaly.description}\n`;
        response += `  Origem: ${anomaly.source} | Frequência: ${anomaly.frequency}\n`;
    });
    response += "\n";
    
    // Score de risco geral
    response += "**📊 Score de Risco Geral:**\n";
    response += `• Sistema: ${anomalyData.systemRisk}/10\n`;
    response += `• Usuários: ${anomalyData.userRisk}/10\n`;
    response += `• Rede: ${anomalyData.networkRisk}/10\n\n`;
    
    response += "**Próximos Passos:**\n";
    response += "• Investigar anomalias críticas imediatamente\n";
    response += "• Implementar controles adicionais para usuários de risco\n";
    response += "• Atualizar regras de detecção baseadas nos padrões";
    
    return response;
}

/**
 * Gera análise geral
 */
async function generateGeneralAnalysis(question) {
    const generalData = await getGeneralSystemData();
    
    let response = "🤖 **Análise Geral do Sistema CertGuard AI**\n\n";
    
    response += "**📊 Status Atual:**\n";
    response += `• Sistema: ${generalData.systemStatus} (${generalData.uptime}% uptime)\n`;
    response += `• Usuários ativos: ${generalData.activeUsers}/${generalData.totalUsers}\n`;
    response += `• Certificados válidos: ${generalData.validCertificates}\n`;
    response += `• Eventos processados hoje: ${generalData.eventsToday}\n\n`;
    
    response += "**🔒 Segurança:**\n";
    response += `• Nível de ameaça: ${generalData.threatLevel}\n`;
    response += `• Incidentes ativos: ${generalData.activeIncidents}\n`;
    response += `• Score de segurança: ${generalData.securityScore}/100\n\n`;
    
    response += "**📈 Performance:**\n";
    response += `• Tempo médio de resposta: ${generalData.avgResponseTime}ms\n`;
    response += `• Throughput: ${generalData.throughput} req/min\n`;
    response += `• Recursos utilizados: ${generalData.resourceUsage}%\n\n`;
    
    response += "**🎯 Insights Principais:**\n";
    generalData.insights.forEach(insight => {
        response += `• ${insight}\n`;
    });
    response += "\n";
    
    response += "**💡 Recomendações:**\n";
    response += "• Continuar monitoramento em tempo real\n";
    response += "• Revisar políticas de segurança mensalmente\n";
    response += "• Implementar melhorias baseadas em ML\n\n";
    
    response += "Para análises mais específicas, pergunte sobre:\n";
    response += "• Usuários específicos ou atividades\n";
    response += "• Certificados e assinaturas digitais\n";
    response += "• Anomalias e incidentes de segurança\n";
    response += "• Performance e métricas do sistema";
    
    return response;
}

/**
 * Obtém fontes de dados para análise
 */
function getAnalysisDataSources(question) {
    const sources = [];
    const questionLower = question.toLowerCase();
    
    if (questionLower.includes('usuário') || questionLower.includes('login')) {
        sources.push('logs de acesso');
    }
    if (questionLower.includes('ip')) {
        sources.push('análise de rede');
    }
    if (questionLower.includes('certificado')) {
        sources.push('base de certificados');
    }
    if (questionLower.includes('horário') || questionLower.includes('tempo')) {
        sources.push('análise temporal');
    }
    if (questionLower.includes('performance')) {
        sources.push('métricas de sistema');
    }
    
    return sources.length > 0 ? sources : ['análise geral', 'logs de auditoria'];
}

/**
 * Atualiza cache de dados de segurança
 */
async function updateSecurityCache() {
    const now = new Date();
    if (!securityCache.lastUpdate || (now - securityCache.lastUpdate) > 300000) { // 5 minutos
        try {
            // Simula atualização de dados em tempo real
            securityCache = {
                recentEvents: await getRecentSecurityEvents(),
                userProfiles: await getUserProfiles(),
                anomalies: await getRecentAnomalies(),
                lastUpdate: now
            };
        } catch (error) {
            console.error('Erro ao atualizar cache:', error);
        }
    }
}

// Funções de dados simulados (em produção, fariam chamadas para API real)

async function getUserActivityData() {
    return {
        recentActivity: [
            {
                name: "João Silva",
                username: "joao.silva",
                loginCount: 15,
                uniqueIPs: 2,
                lastLogin: "2024-01-27 14:30:00",
                suspicious: false
            },
            {
                name: "Maria Santos",
                username: "maria.santos",
                loginCount: 8,
                uniqueIPs: 1,
                lastLogin: "2024-01-27 16:20:00",
                suspicious: false
            },
            {
                name: "Pedro Hacker",
                username: "pedro.hacker",
                loginCount: 25,
                uniqueIPs: 8,
                lastLogin: "2024-01-27 03:15:00",
                suspicious: true,
                suspiciousReason: "Múltiplos IPs e acesso noturno"
            }
        ],
        securityAlerts: [
            {
                severity: "high",
                description: "15 tentativas de login falhadas do IP 10.0.0.15"
            },
            {
                severity: "medium",
                description: "Acesso fora do horário comercial detectado"
            }
        ]
    };
}

async function getIPAnalysisData() {
    return {
        suspiciousIPs: [
            {
                address: "10.0.0.15",
                location: "Desconhecida",
                attempts: 25,
                failures: 15,
                users: ["pedro.hacker"],
                riskLevel: "Alto"
            },
            {
                address: "203.45.67.89",
                location: "China",
                attempts: 5,
                failures: 5,
                users: ["unknown"],
                riskLevel: "Crítico"
            }
        ],
        geoAnomalies: [
            {
                user: "joao.silva",
                country: "Estados Unidos",
                usual: "Brasil"
            }
        ],
        totalUniqueIPs: 45,
        blockedIPs: 3,
        successRate: 87.5
    };
}

async function getCertificateAnalysisData() {
    return {
        certificates: [
            {
                subjectName: "João Silva",
                type: "A1",
                serialNumber: "2345678901BCDEFG",
                status: "active",
                recentUsage: 89,
                validUntil: "2024-02-01",
                alerts: ["Próximo ao vencimento"]
            },
            {
                subjectName: "Pedro Hacker",
                type: "A1",
                serialNumber: "6789012345FGHIJK",
                status: "revoked",
                recentUsage: 0,
                validUntil: "2025-01-20",
                alerts: ["Certificado revogado", "Tentativa de uso detectada"]
            }
        ],
        suspiciousActivity: [
            {
                description: "Tentativa de uso de certificado revogado",
                user: "pedro.hacker",
                timestamp: "2024-01-27 02:15:00"
            }
        ],
        metrics: {
            totalSignatures: 156,
            mostUsed: "Maria Santos (A3)",
            avgSignTime: 2.8
        }
    };
}

async function getTimeAnalysisData() {
    return {
        offHoursActivity: [
            {
                timestamp: "2024-01-26 23:45:00",
                user: "joao.silva",
                action: "Assinatura de documento",
                ip: "192.168.1.150",
                riskLevel: "low"
            },
            {
                timestamp: "2024-01-27 02:15:00",
                user: "pedro.hacker",
                action: "Tentativa de login",
                ip: "10.0.0.15",
                riskLevel: "high"
            }
        ],
        userPatterns: [
            {
                user: "joao.silva",
                usualHours: "08:00-18:00",
                anomalies: 1
            },
            {
                user: "maria.santos",
                usualHours: "09:00-17:00",
                anomalies: 0
            }
        ],
        peakHour: "14:00",
        nightActivity: 5.2,
        weekendActivity: 12.8
    };
}

async function getPerformanceData() {
    return {
        avgResponseTime: 1200,
        uptime: 99.97,
        requestsPerMinute: 156,
        errorRate: 0.3,
        slowOperations: [
            {
                operation: "Assinatura digital",
                avgTime: 2800,
                count: 89
            },
            {
                operation: "Validação de certificado",
                avgTime: 1500,
                count: 234
            }
        ],
        bottlenecks: [
            {
                component: "Módulo de assinatura",
                description: "Alto tempo de processamento"
            }
        ],
        trend: -5.2,
        peakUsage: "14:00-15:00"
    };
}

async function getSecurityReportData() {
    return {
        totalEvents: 1247,
        criticalEvents: 3,
        anomalies: 15,
        uptime: 99.97,
        topRisks: [
            {
                description: "Tentativas de força bruta",
                severity: "Alto"
            },
            {
                description: "Uso de certificado revogado",
                severity: "Crítico"
            },
            {
                description: "Acesso fora do horário",
                severity: "Médio"
            }
        ],
        highRiskUsers: [
            {
                name: "Pedro Hacker",
                riskFactors: ["Múltiplos IPs", "Horário suspeito", "Certificado revogado"]
            }
        ],
        trends: {
            accessAttempts: "+15%",
            certificateUsage: "+8%",
            suspiciousActivity: "+25%"
        },
        recommendations: [
            "Implementar bloqueio automático de IPs suspeitos",
            "Configurar alertas para atividades noturnas",
            "Revisar políticas de renovação de certificados",
            "Implementar MFA para usuários de alto risco"
        ]
    };
}

async function getAnomalyData() {
    return {
        critical: [
            {
                description: "Tentativa de acesso com certificado revogado",
                user: "pedro.hacker",
                timestamp: "2024-01-27 02:15:00",
                action: "Bloquear usuário imediatamente"
            }
        ],
        behavioral: [
            {
                user: "pedro.hacker",
                pattern: "Acesso em horários anômalos",
                deviation: "3.2σ",
                confidence: "95%"
            }
        ],
        network: [
            {
                type: "IP suspeito",
                description: "Múltiplas tentativas de acesso falhadas",
                source: "10.0.0.15",
                frequency: "15 tentativas/hora"
            }
        ],
        systemRisk: 6,
        userRisk: 8,
        networkRisk: 7
    };
}

async function getGeneralSystemData() {
    return {
        systemStatus: "Operacional",
        uptime: 99.97,
        activeUsers: 5,
        totalUsers: 6,
        validCertificates: 5,
        eventsToday: 156,
        threatLevel: "Médio",
        activeIncidents: 1,
        securityScore: 85,
        avgResponseTime: 1200,
        throughput: 156,
        resourceUsage: 68,
        insights: [
            "Sistema operando dentro dos parâmetros normais",
            "1 usuário suspenso por atividade suspeita",
            "Performance estável nas últimas 24h",
            "Aumento de 15% em tentativas de acesso não autorizado"
        ]
    };
}

// Funções auxiliares para dados em tempo real
async function getRecentSecurityEvents() {
    // Simula eventos recentes
    return [];
}

async function getUserProfiles() {
    // Simula perfis de usuário
    return {};
}

async function getRecentAnomalies() {
    // Simula anomalias recentes
    return [];
}

// Exporta funções principais
window.askAdvancedLucia = askAdvancedLucia;
window.analyzeSecurityQuestion = analyzeSecurityQuestion;

