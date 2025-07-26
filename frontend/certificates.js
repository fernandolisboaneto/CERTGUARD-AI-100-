// Dados fake para certificados A1/A3
const certificatesData = {
    certificates: [
        {
            id: 1,
            name: "João Silva Santos",
            type: "A3",
            cpf: "123.456.789-01",
            organization: "Escritório Silva & Associados",
            issuer: "Serasa Experian",
            serialNumber: "4A:B2:C3:D4:E5:F6:78:90",
            validFrom: "2024-01-15",
            validTo: "2027-01-15",
            status: "Ativo",
            usage: "Assinatura Digital",
            device: "Token SafeNet",
            lastUsed: "2025-01-26 14:30",
            usageCount: 1247,
            autoRenew: true
        },
        {
            id: 2,
            name: "Maria Costa Oliveira",
            type: "A1",
            cpf: "987.654.321-09",
            organization: "Advocacia Costa",
            issuer: "Certisign",
            serialNumber: "1F:2E:3D:4C:5B:6A:79:88",
            validFrom: "2024-06-10",
            validTo: "2025-06-10",
            status: "Expirando",
            usage: "Peticionamento Eletrônico",
            device: "Arquivo .pfx",
            lastUsed: "2025-01-25 16:45",
            usageCount: 892,
            autoRenew: false
        },
        {
            id: 3,
            name: "Pedro Santos Lima",
            type: "A3",
            cpf: "456.789.123-45",
            organization: "Jurídico Santos",
            issuer: "ICP-Brasil AC",
            serialNumber: "7G:8H:9I:0J:1K:2L:3M:4N",
            validFrom: "2023-11-20",
            validTo: "2026-11-20",
            status: "Suspenso",
            usage: "Consulta Processual",
            device: "Cartão Smart Card",
            lastUsed: "2025-01-20 11:20",
            usageCount: 456,
            autoRenew: false
        },
        {
            id: 4,
            name: "Ana Paula Ferreira",
            type: "A1",
            cpf: "321.654.987-12",
            organization: "Consultoria Ferreira",
            issuer: "Valid Certificadora",
            serialNumber: "5O:6P:7Q:8R:9S:0T:1U:2V",
            validFrom: "2024-03-05",
            validTo: "2025-03-05",
            status: "Ativo",
            usage: "Assinatura de Contratos",
            device: "Arquivo .pfx",
            lastUsed: "2025-01-26 08:15",
            usageCount: 2156,
            autoRenew: true
        },
        {
            id: 5,
            name: "Carlos Eduardo Rocha",
            type: "A3",
            cpf: "789.123.456-78",
            organization: "Rocha Advogados",
            issuer: "Soluti",
            serialNumber: "3W:4X:5Y:6Z:7A:8B:9C:0D",
            validFrom: "2024-08-12",
            validTo: "2027-08-12",
            status: "Ativo",
            usage: "Tribunal Digital",
            device: "Token ePass2003",
            lastUsed: "2025-01-26 12:00",
            usageCount: 678,
            autoRenew: true
        },
        {
            id: 6,
            name: "Luciana Mendes Silva",
            type: "A1",
            cpf: "654.321.987-54",
            organization: "Silva Mendes Advocacia",
            issuer: "AC Certisign",
            serialNumber: "1E:2F:3G:4H:5I:6J:7K:8L",
            validFrom: "2024-02-28",
            validTo: "2025-02-28",
            status: "Expirado",
            usage: "E-SAJ",
            device: "Arquivo .pfx",
            lastUsed: "2025-01-15 09:30",
            usageCount: 234,
            autoRenew: false
        }
    ],
    
    statistics: {
        total: 6,
        active: 3,
        expiring: 1,
        expired: 1,
        suspended: 1,
        a1Count: 3,
        a3Count: 3,
        autoRenewEnabled: 3
    },
    
    recentActivity: [
        {
            id: 1,
            action: "Certificado utilizado",
            certificate: "João Silva Santos",
            timestamp: "2025-01-26 14:30",
            details: "Assinatura digital em contrato.pdf"
        },
        {
            id: 2,
            action: "Certificado instalado",
            certificate: "Carlos Eduardo Rocha",
            timestamp: "2025-01-26 12:00",
            details: "Token ePass2003 detectado e configurado"
        },
        {
            id: 3,
            action: "Alerta de expiração",
            certificate: "Maria Costa Oliveira",
            timestamp: "2025-01-25 16:45",
            details: "Certificado expira em 30 dias"
        },
        {
            id: 4,
            action: "Renovação automática",
            certificate: "Ana Paula Ferreira",
            timestamp: "2025-01-25 10:20",
            details: "Processo de renovação iniciado"
        }
    ],
    
    tribunals: [
        {
            id: 1,
            name: "TJ-RJ",
            fullName: "Tribunal de Justiça do Rio de Janeiro",
            url: "https://www.tjrj.jus.br",
            status: "Conectado",
            lastSync: "2025-01-26 14:00",
            certificatesUsed: 45,
            automationLevel: "Completa"
        },
        {
            id: 2,
            name: "TJSP",
            fullName: "Tribunal de Justiça de São Paulo",
            url: "https://www.tjsp.jus.br",
            status: "Conectado",
            lastSync: "2025-01-26 13:45",
            certificatesUsed: 78,
            automationLevel: "Parcial"
        },
        {
            id: 3,
            name: "TRF-2",
            fullName: "Tribunal Regional Federal da 2ª Região",
            url: "https://www.trf2.jus.br",
            status: "Configurando",
            lastSync: "2025-01-25 16:30",
            certificatesUsed: 12,
            automationLevel: "Básica"
        },
        {
            id: 4,
            name: "PJe",
            fullName: "Processo Judicial Eletrônico",
            url: "https://pje.jus.br",
            status: "Conectado",
            lastSync: "2025-01-26 14:15",
            certificatesUsed: 156,
            automationLevel: "Completa"
        }
    ]
};

// Função para gerar dados fake adicionais
function generateFakeData() {
    return certificatesData;
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.certificatesData = certificatesData;
    window.generateFakeData = generateFakeData;
}

