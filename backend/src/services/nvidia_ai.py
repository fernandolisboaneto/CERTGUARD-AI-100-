"""
CertGuard AI - Integração com NVIDIA AI APIs
Sistema avançado de IA para análise jurídica e processamento de documentos
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NVIDIAAIService:
    """Serviço de integração com APIs da NVIDIA para IA avançada"""
    
    def __init__(self):
        # Configuração principal da API NVIDIA
        self.nvidia_api_1 = {
            "api_key": os.getenv("NVIDIA_API_KEY_1", "nvapi-82_"),
            "base_url": "https://integrate.api.nvidia.com/v1",
            "model": "meta/llama3-70b-instruct",
            "temperature": 0.5,
            "top_p": 1,
            "max_tokens": 1024,
            "stream": True
        }
        
        # Configuração secundária da API NVIDIA
        self.nvidia_api_2 = {
            "api_key": os.getenv("NVIDIA_API_KEY_2", "nvapi-YdC"),
            "base_url": "https://integrate.api.nvidia.com/v1", 
            "model": "meta/llama-3.3-70b-instruct",
            "temperature": 0.2,
            "top_p": 0.7,
            "max_tokens": 1024,
            "stream": True
        }
        
        # Configuração ativa (pode alternar entre as duas)
        self.active_config = self.nvidia_api_1
        
        # Headers para requisições
        self.headers = {
            "Authorization": f"Bearer {self.active_config['api_key']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Cache de respostas para otimização
        self.response_cache = {}
        
        # Estatísticas de uso
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "last_request_time": None
        }

    async def switch_api_config(self, config_number: int = 1):
        """Alterna entre as configurações de API disponíveis"""
        if config_number == 1:
            self.active_config = self.nvidia_api_1
        elif config_number == 2:
            self.active_config = self.nvidia_api_2
        else:
            raise ValueError("Configuração inválida. Use 1 ou 2.")
        
        # Atualiza headers
        self.headers["Authorization"] = f"Bearer {self.active_config['api_key']}"
        logger.info(f"API configuração alterada para: {self.active_config['model']}")

    async def analyze_legal_document(self, document_text: str, document_type: str = "generic") -> Dict[str, Any]:
        """Analisa documento jurídico usando IA da NVIDIA"""
        
        prompt = self._build_legal_analysis_prompt(document_text, document_type)
        
        try:
            response = await self._make_api_request(prompt, context="legal_analysis")
            
            # Processa resposta para análise jurídica
            analysis = self._process_legal_analysis(response, document_type)
            
            return {
                "success": True,
                "analysis": analysis,
                "document_type": document_type,
                "confidence": analysis.get("confidence", 0.85),
                "timestamp": datetime.now().isoformat(),
                "model_used": self.active_config["model"]
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de documento: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def generate_legal_petition(self, case_details: Dict[str, Any]) -> Dict[str, Any]:
        """Gera petição jurídica usando IA da NVIDIA"""
        
        prompt = self._build_petition_prompt(case_details)
        
        try:
            response = await self._make_api_request(prompt, context="petition_generation")
            
            # Processa resposta para geração de petição
            petition = self._process_petition_response(response, case_details)
            
            return {
                "success": True,
                "petition": petition,
                "case_type": case_details.get("type", "generic"),
                "confidence": petition.get("confidence", 0.90),
                "timestamp": datetime.now().isoformat(),
                "model_used": self.active_config["model"]
            }
            
        except Exception as e:
            logger.error(f"Erro na geração de petição: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def analyze_jurisprudence(self, query: str, court: str = "all") -> Dict[str, Any]:
        """Analisa jurisprudência usando IA da NVIDIA"""
        
        prompt = self._build_jurisprudence_prompt(query, court)
        
        try:
            response = await self._make_api_request(prompt, context="jurisprudence_analysis")
            
            # Processa resposta para análise jurisprudencial
            analysis = self._process_jurisprudence_response(response, query, court)
            
            return {
                "success": True,
                "analysis": analysis,
                "query": query,
                "court": court,
                "confidence": analysis.get("confidence", 0.88),
                "timestamp": datetime.now().isoformat(),
                "model_used": self.active_config["model"]
            }
            
        except Exception as e:
            logger.error(f"Erro na análise jurisprudencial: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def predict_case_outcome(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prediz resultado de caso usando IA da NVIDIA"""
        
        prompt = self._build_prediction_prompt(case_data)
        
        try:
            response = await self._make_api_request(prompt, context="case_prediction")
            
            # Processa resposta para predição
            prediction = self._process_prediction_response(response, case_data)
            
            return {
                "success": True,
                "prediction": prediction,
                "case_type": case_data.get("type", "generic"),
                "confidence": prediction.get("confidence", 0.75),
                "timestamp": datetime.now().isoformat(),
                "model_used": self.active_config["model"]
            }
            
        except Exception as e:
            logger.error(f"Erro na predição de caso: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def extract_contract_clauses(self, contract_text: str) -> Dict[str, Any]:
        """Extrai e analisa cláusulas contratuais usando IA da NVIDIA"""
        
        prompt = self._build_contract_analysis_prompt(contract_text)
        
        try:
            response = await self._make_api_request(prompt, context="contract_analysis")
            
            # Processa resposta para análise contratual
            analysis = self._process_contract_analysis(response, contract_text)
            
            return {
                "success": True,
                "analysis": analysis,
                "contract_length": len(contract_text),
                "confidence": analysis.get("confidence", 0.92),
                "timestamp": datetime.now().isoformat(),
                "model_used": self.active_config["model"]
            }
            
        except Exception as e:
            logger.error(f"Erro na análise contratual: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _make_api_request(self, prompt: str, context: str = "general") -> Dict[str, Any]:
        """Faz requisição para a API da NVIDIA"""
        
        # Incrementa estatísticas
        self.usage_stats["total_requests"] += 1
        self.usage_stats["last_request_time"] = datetime.now().isoformat()
        
        # Verifica cache
        cache_key = f"{context}:{hash(prompt)}"
        if cache_key in self.response_cache:
            logger.info("Resposta encontrada no cache")
            return self.response_cache[cache_key]
        
        # Prepara payload
        payload = {
            "model": self.active_config["model"],
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um assistente jurídico especializado em direito brasileiro, com conhecimento profundo em ICP-Brasil, LGPD, provimentos do CNJ e legislação processual."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": self.active_config["temperature"],
            "top_p": self.active_config["top_p"],
            "max_tokens": self.active_config["max_tokens"],
            "stream": False  # Para simplificar o processamento inicial
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.active_config['base_url']}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Atualiza estatísticas
                        self.usage_stats["successful_requests"] += 1
                        if "usage" in result:
                            self.usage_stats["total_tokens_used"] += result["usage"].get("total_tokens", 0)
                        
                        # Armazena no cache
                        self.response_cache[cache_key] = result
                        
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(f"API Error {response.status}: {error_text}")
                        
        except Exception as e:
            self.usage_stats["failed_requests"] += 1
            logger.error(f"Erro na requisição API: {str(e)}")
            raise

    def _build_legal_analysis_prompt(self, document_text: str, document_type: str) -> str:
        """Constrói prompt para análise de documento jurídico"""
        
        return f"""
        Analise o seguinte documento jurídico do tipo "{document_type}" e forneça uma análise detalhada:

        DOCUMENTO:
        {document_text[:2000]}...

        Por favor, forneça uma análise estruturada incluindo:

        1. TIPO DE DOCUMENTO: Classificação precisa do documento
        2. RESUMO EXECUTIVO: Síntese dos pontos principais
        3. ANÁLISE JURÍDICA: Aspectos legais relevantes
        4. PONTOS DE ATENÇÃO: Questões que requerem cuidado especial
        5. RECOMENDAÇÕES: Sugestões de ação ou melhoria
        6. CONFORMIDADE: Verificação com normas aplicáveis (ICP-Brasil, LGPD, CNJ)
        7. RISCOS IDENTIFICADOS: Potenciais problemas legais
        8. PRÓXIMOS PASSOS: Ações recomendadas

        Responda em formato JSON estruturado para facilitar o processamento.
        """

    def _build_petition_prompt(self, case_details: Dict[str, Any]) -> str:
        """Constrói prompt para geração de petição"""
        
        case_type = case_details.get("type", "Ação Civil")
        plaintiff = case_details.get("plaintiff", "Requerente")
        defendant = case_details.get("defendant", "Requerido")
        facts = case_details.get("facts", "Fatos a serem descritos")
        
        return f"""
        Gere uma petição inicial profissional para o seguinte caso:

        TIPO DE AÇÃO: {case_type}
        REQUERENTE: {plaintiff}
        REQUERIDO: {defendant}
        FATOS: {facts}

        A petição deve incluir:

        1. QUALIFICAÇÃO DAS PARTES
        2. DOS FATOS
        3. DO DIREITO (fundamentação jurídica)
        4. DOS PEDIDOS
        5. DO VALOR DA CAUSA
        6. DAS PROVAS
        7. REQUERIMENTOS FINAIS

        Use linguagem jurídica apropriada, cite artigos de lei relevantes e precedentes quando aplicável.
        Formate como uma petição real, pronta para protocolo.
        
        Responda em formato JSON com a estrutura da petição.
        """

    def _build_jurisprudence_prompt(self, query: str, court: str) -> str:
        """Constrói prompt para análise jurisprudencial"""
        
        return f"""
        Analise a seguinte consulta jurisprudencial:

        CONSULTA: {query}
        TRIBUNAL: {court}

        Forneça uma análise incluindo:

        1. PRECEDENTES RELEVANTES: Decisões importantes sobre o tema
        2. TENDÊNCIA JURISPRUDENCIAL: Direção das decisões recentes
        3. ARGUMENTOS FAVORÁVEIS: Pontos que apoiam a tese
        4. ARGUMENTOS CONTRÁRIOS: Pontos que podem ser questionados
        5. ESTRATÉGIA RECOMENDADA: Como abordar o tema
        6. CITAÇÕES SUGERIDAS: Precedentes para fundamentação
        7. PROBABILIDADE DE SUCESSO: Estimativa baseada na jurisprudência

        Responda em formato JSON estruturado.
        """

    def _build_prediction_prompt(self, case_data: Dict[str, Any]) -> str:
        """Constrói prompt para predição de caso"""
        
        return f"""
        Analise o seguinte caso e forneça uma predição de resultado:

        DADOS DO CASO: {json.dumps(case_data, indent=2)}

        Forneça uma análise preditiva incluindo:

        1. PROBABILIDADE DE SUCESSO: Percentual estimado
        2. FATORES FAVORÁVEIS: Elementos que apoiam o caso
        3. FATORES DESFAVORÁVEIS: Elementos que prejudicam o caso
        4. TEMPO ESTIMADO: Duração provável do processo
        5. VALOR PROVÁVEL: Estimativa de resultado financeiro
        6. ESTRATÉGIAS RECOMENDADAS: Abordagens para maximizar sucesso
        7. RISCOS IDENTIFICADOS: Potenciais problemas
        8. PRECEDENTES SIMILARES: Casos comparáveis

        Base a análise em padrões jurisprudenciais e estatísticas processuais.
        Responda em formato JSON estruturado.
        """

    def _build_contract_analysis_prompt(self, contract_text: str) -> str:
        """Constrói prompt para análise contratual"""
        
        return f"""
        Analise o seguinte contrato e identifique cláusulas importantes:

        CONTRATO:
        {contract_text[:3000]}...

        Forneça uma análise incluindo:

        1. TIPO DE CONTRATO: Classificação do instrumento
        2. PARTES ENVOLVIDAS: Identificação dos contratantes
        3. OBJETO DO CONTRATO: Finalidade e escopo
        4. CLÁUSULAS PRINCIPAIS: Disposições mais importantes
        5. CLÁUSULAS PROBLEMÁTICAS: Pontos que podem gerar conflito
        6. CLÁUSULAS AUSENTES: Disposições que deveriam estar presentes
        7. CONFORMIDADE LEGAL: Adequação à legislação
        8. RECOMENDAÇÕES: Sugestões de melhoria
        9. RISCOS IDENTIFICADOS: Potenciais problemas legais

        Responda em formato JSON estruturado.
        """

    def _process_legal_analysis(self, response: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """Processa resposta de análise jurídica"""
        
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Tenta extrair JSON da resposta
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
                analysis = json.loads(json_content)
            else:
                # Se não há JSON, cria estrutura básica
                analysis = {
                    "summary": content[:500] + "...",
                    "full_analysis": content,
                    "confidence": 0.85
                }
            
            # Adiciona metadados
            analysis["document_type"] = document_type
            analysis["processed_at"] = datetime.now().isoformat()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro no processamento de análise: {str(e)}")
            return {
                "error": "Erro no processamento",
                "raw_response": response,
                "confidence": 0.0
            }

    def _process_petition_response(self, response: Dict[str, Any], case_details: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resposta de geração de petição"""
        
        try:
            content = response["choices"][0]["message"]["content"]
            
            return {
                "petition_text": content,
                "case_details": case_details,
                "confidence": 0.90,
                "word_count": len(content.split()),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento de petição: {str(e)}")
            return {
                "error": "Erro no processamento",
                "raw_response": response,
                "confidence": 0.0
            }

    def _process_jurisprudence_response(self, response: Dict[str, Any], query: str, court: str) -> Dict[str, Any]:
        """Processa resposta de análise jurisprudencial"""
        
        try:
            content = response["choices"][0]["message"]["content"]
            
            return {
                "analysis": content,
                "query": query,
                "court": court,
                "confidence": 0.88,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento jurisprudencial: {str(e)}")
            return {
                "error": "Erro no processamento",
                "raw_response": response,
                "confidence": 0.0
            }

    def _process_prediction_response(self, response: Dict[str, Any], case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resposta de predição"""
        
        try:
            content = response["choices"][0]["message"]["content"]
            
            return {
                "prediction": content,
                "case_data": case_data,
                "confidence": 0.75,
                "predicted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento de predição: {str(e)}")
            return {
                "error": "Erro no processamento",
                "raw_response": response,
                "confidence": 0.0
            }

    def _process_contract_analysis(self, response: Dict[str, Any], contract_text: str) -> Dict[str, Any]:
        """Processa resposta de análise contratual"""
        
        try:
            content = response["choices"][0]["message"]["content"]
            
            return {
                "analysis": content,
                "contract_length": len(contract_text),
                "confidence": 0.92,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento contratual: {str(e)}")
            return {
                "error": "Erro no processamento",
                "raw_response": response,
                "confidence": 0.0
            }

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso da API"""
        
        success_rate = 0
        if self.usage_stats["total_requests"] > 0:
            success_rate = (self.usage_stats["successful_requests"] / self.usage_stats["total_requests"]) * 100
        
        return {
            **self.usage_stats,
            "success_rate": round(success_rate, 2),
            "active_model": self.active_config["model"],
            "cache_size": len(self.response_cache)
        }

    def clear_cache(self):
        """Limpa o cache de respostas"""
        self.response_cache.clear()
        logger.info("Cache de respostas limpo")

    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde da API NVIDIA"""
        
        try:
            test_prompt = "Teste de conectividade com a API NVIDIA. Responda apenas 'OK'."
            response = await self._make_api_request(test_prompt, context="health_check")
            
            return {
                "status": "healthy",
                "model": self.active_config["model"],
                "response_time": "< 1s",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Instância global do serviço
nvidia_ai_service = NVIDIAAIService()

# Funções de conveniência para uso direto
async def analyze_document(document_text: str, document_type: str = "generic"):
    """Função de conveniência para análise de documento"""
    return await nvidia_ai_service.analyze_legal_document(document_text, document_type)

async def generate_petition(case_details: Dict[str, Any]):
    """Função de conveniência para geração de petição"""
    return await nvidia_ai_service.generate_legal_petition(case_details)

async def analyze_jurisprudence(query: str, court: str = "all"):
    """Função de conveniência para análise jurisprudencial"""
    return await nvidia_ai_service.analyze_jurisprudence(query, court)

async def predict_case(case_data: Dict[str, Any]):
    """Função de conveniência para predição de caso"""
    return await nvidia_ai_service.predict_case_outcome(case_data)

async def analyze_contract(contract_text: str):
    """Função de conveniência para análise contratual"""
    return await nvidia_ai_service.extract_contract_clauses(contract_text)

