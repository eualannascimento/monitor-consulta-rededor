#!/usr/bin/env python3
"""
Script para verificar disponibilidade de consultas médicas na Rede D'Or São Luiz.

Este script monitora automaticamente a disponibilidade de horários de consulta
e envia notificações por email quando encontra horários antes da data agendada.
"""
import logging
import os
import re
import smtplib
import sys
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from playwright.sync_api import Page, sync_playwright

# ========== CONFIGURAÇÕES (EDITE AQUI) ==========
NOME_MEDICA = "Isadora Leda Braga"  # Nome completo da médica
ESPECIALIDADE = "Endocrinologia Geral"  # Especialidade
LOCAL_ATENDIMENTO = "Hospital Villa Lobos"  # Local de atendimento
DATA_CONSULTA_ATUAL = "2026-03-11"  # Data da consulta já agendada (formato YYYY-MM-DD)
EMAIL_DESTINO = "oquealan@gmail.com"  # Seu email para receber notificações

# ID da médica no sistema (obtido do site)
MEDICA_ID = "725717342"  # ID da Dra. Isadora no sistema

# Configurações de Email (usando Gmail como exemplo)
EMAIL_REMETENTE = os.getenv("EMAIL_SENDER")  # Configure no GitHub Secrets
SENHA_EMAIL = os.getenv("EMAIL_PASSWORD")  # Configure no GitHub Secrets (use App Password)
# =================================================

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class Horario:
    """Representa um horário disponível para consulta."""

    data: str
    hora: str
    texto_original: str


class ConfigValidator:
    """Validador de configurações do sistema."""

    @staticmethod
    def validar_email(email: Optional[str]) -> bool:
        """Valida formato de email."""
        if not email:
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validar_data(data: str) -> bool:
        """Valida formato de data (YYYY-MM-DD)."""
        try:
            datetime.strptime(data, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def validar_configuracoes() -> bool:
        """Valida todas as configurações necessárias."""
        erros = []

        if not EMAIL_REMETENTE:
            erros.append("EMAIL_SENDER não configurado nas variáveis de ambiente")
        elif not ConfigValidator.validar_email(EMAIL_REMETENTE):
            erros.append(f"EMAIL_SENDER inválido: {EMAIL_REMETENTE}")

        if not SENHA_EMAIL:
            erros.append("EMAIL_PASSWORD não configurado nas variáveis de ambiente")

        if not ConfigValidator.validar_email(EMAIL_DESTINO):
            erros.append(f"EMAIL_DESTINO inválido: {EMAIL_DESTINO}")

        if not ConfigValidator.validar_data(DATA_CONSULTA_ATUAL):
            erros.append(
                f"DATA_CONSULTA_ATUAL em formato inválido: {DATA_CONSULTA_ATUAL} (use YYYY-MM-DD)"
            )

        if erros:
            for erro in erros:
                logger.error(f"❌ {erro}")
            return False

        return True


class EmailNotifier:
    """Gerenciador de notificações por email."""

    def __init__(
        self,
        remetente: str,
        senha: str,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
    ):
        """
        Inicializa o notificador de email.

        Args:
            remetente: Email do remetente
            senha: Senha ou senha de aplicativo
            smtp_host: Servidor SMTP
            smtp_port: Porta SMTP
        """
        self.remetente = remetente
        self.senha = senha
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def criar_corpo_email(self, horarios: List[Horario]) -> str:
        """
        Cria o corpo HTML do email de notificação.

        Args:
            horarios: Lista de horários disponíveis

        Returns:
            String HTML formatada
        """
        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #4CAF50;">🎯 Horário(s) Disponível(is) Encontrado(s)!</h2>
            <p><strong>Médica:</strong> {NOME_MEDICA}</p>
            <p><strong>Especialidade:</strong> {ESPECIALIDADE}</p>
            <p><strong>Local:</strong> {LOCAL_ATENDIMENTO}</p>
            <p><strong>Sua consulta atual:</strong> {DATA_CONSULTA_ATUAL}</p>
            
            <h3 style="color: #2196F3;">📅 Horários disponíveis ANTES da sua consulta:</h3>
            <ul style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
        """

        for horario in horarios:
            corpo += f'<li style="margin: 8px 0;"><strong>{horario.data}</strong> às <strong>{horario.hora}</strong></li>\n'

        corpo += """
            </ul>
            <p style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107;">
                ⚡ <strong>Acesse o site rapidamente para fazer a marcação!</strong>
            </p>
            <p>
                <a href="https://www.rededorsaoluiz.com.br/paciente/marcar-consulta" 
                   style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Marcar Consulta Agora
                </a>
            </p>
        </body>
        </html>
        """

        return corpo

    def enviar(self, destinatario: str, horarios: List[Horario]) -> bool:
        """
        Envia email de notificação com horários disponíveis.

        Args:
            destinatario: Email do destinatário
            horarios: Lista de horários disponíveis

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.remetente
            msg["To"] = destinatario
            msg["Subject"] = f"🏥 Nova Disponibilidade - {NOME_MEDICA}"

            corpo_email = self.criar_corpo_email(horarios)
            msg.attach(MIMEText(corpo_email, "html"))

            logger.info(f"📧 Conectando ao servidor SMTP {self.smtp_host}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.remetente, self.senha)
                server.send_message(msg)

            logger.info(f"✅ Email enviado com sucesso para {destinatario}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Erro de autenticação SMTP. Verifique EMAIL_SENDER e EMAIL_PASSWORD")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ Erro SMTP ao enviar email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao enviar email: {str(e)}")
            return False


class DisponibilidadeScraper:
    """Scraper para verificar disponibilidade de consultas."""

    def __init__(self, medica_id: str, timeout: int = 60000):
        """
        Inicializa o scraper.

        Args:
            medica_id: ID da médica no sistema
            timeout: Timeout em milissegundos para operações
        """
        self.medica_id = medica_id
        self.timeout = timeout
        self.url = f"https://www.rededorsaoluiz.com.br/paciente/marcar-consulta/?medicom={medica_id}"

    def _extrair_data_hora(self, elemento, texto: str) -> Optional[tuple]:
        """
        Extrai data e hora de um elemento ou texto.

        Args:
            elemento: Elemento da página para buscar subelementos
            texto: Texto para parsing com regex

        Returns:
            Tupla (data, hora) ou None se não encontrado
        """
        try:
            # Tentar buscar elementos filhos específicos
            data_elem = elemento.query_selector('[class*="data"], [class*="date"], [class*="dia"]')
            hora_elem = elemento.query_selector('[class*="hora"], [class*="time"], [class*="horario"]')

            if data_elem and hora_elem:
                return data_elem.inner_text().strip(), hora_elem.inner_text().strip()

            # Se não encontrou elementos separados, usar regex
            date_match = re.search(r"(\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?)", texto)
            time_match = re.search(r"(\d{1,2}:\d{2})", texto)

            if date_match and time_match:
                return date_match.group(1), time_match.group(1)

        except Exception as e:
            logger.debug(f"Erro ao extrair data/hora: {e}")

        return None

    def _buscar_horarios_na_pagina(self, page: Page) -> List[Horario]:
        """
        Busca horários disponíveis na página.

        Args:
            page: Página do Playwright (pode ser iframe)

        Returns:
            Lista de horários encontrados
        """
        # Seletores comuns para horários em sites de agendamento
        selectors_horarios = [
            'div[class*="horario"]',
            'div[class*="hora"]',
            'button[class*="horario"]',
            'button[class*="schedule"]',
            'div[class*="disponivel"]',
            'div[class*="available"]',
            'div[class*="slot"]',
            'div[class*="appointment"]',
            'li[class*="time"]',
            '[data-time]',
            '[data-slot]',
            '[data-horario]',
            '.time-slot',
            '.available-time',
            '.schedule-item',
        ]

        horarios_encontrados = []

        for selector in selectors_horarios:
            try:
                elementos = page.query_selector_all(selector)
                if elementos and len(elementos) > 0:
                    logger.info(f"  ✓ Encontrados {len(elementos)} elementos com: {selector}")

                    for elem in elementos:
                        try:
                            texto = elem.inner_text().strip()

                            # Verificar se há números (indicativo de data/hora)
                            if any(char.isdigit() for char in texto):
                                resultado = self._extrair_data_hora(elem, texto)

                                if resultado:
                                    data_text, hora_text = resultado
                                    horarios_encontrados.append(
                                        Horario(
                                            data=data_text,
                                            hora=hora_text,
                                            texto_original=texto,
                                        )
                                    )
                                    logger.info(f"    ⏰ Horário: {data_text} às {hora_text}")
                        except Exception:
                            continue

                    if horarios_encontrados:
                        break  # Se encontrou horários, não precisa tentar outros seletores

            except Exception:
                continue

        return horarios_encontrados

    def buscar(self) -> List[Horario]:
        """
        Busca disponibilidade no site usando interceptação de rede e automação.

        Returns:
            Lista de horários disponíveis
        """
        logger.info(f"🔍 Iniciando busca por {NOME_MEDICA}...")
        logger.info(f"📱 Acessando URL: {self.url}")

        horarios_encontrados = []
        
        # Variável para armazenar dados da API interceptados
        api_data_captured = []

        def handle_response(response):
            """Callback para interceptar respostas da API."""
            try:
                # Filtrar apenas respostas JSON que podem conter horários
                if "application/json" in response.headers.get("content-type", ""):
                    # Tentar capturar URLs suspeitas de ter disponibilidade
                    if "disponibilidade" in response.url or "schedule" in response.url or "slot" in response.url:
                        try:
                            data = response.json()
                            logger.info(f"🎣 JSON interceptado da URL: {response.url}")
                            api_data_captured.append(data)
                        except:
                            pass
            except:
                pass

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="pt-BR"
            )
            page = context.new_page()

            # Ativar interceptação
            page.on("response", handle_response)

            try:
                # Aumentar timeout padrão para 60s
                page.set_default_timeout(60000)
                
                logger.info("🌍 Navegando para o site...")
                page.goto(self.url, wait_until="networkidle")

                # ==================================================================
                # TRATAMENTO DO MODAL "VAMOS COMEÇAR"
                # ==================================================================
                logger.info("🛑 Verificando modais iniciais...")
                
                # Aguardar um pouco para garantir que modais carreguem
                page.wait_for_timeout(5000)
                
                # Tentar identificar o modal "Vamos começar"
                # Seletores baseados na imagem e estrutura comum
                selectors_modal = [
                    "text=Vamos começar!",
                    "text=Selecione a especialidade",
                    "div[role='dialog']",
                    ".modal-content"
                ]
                
                modal_found = False
                for sel in selectors_modal:
                    if page.is_visible(sel):
                        logger.info(f"✅ Modal detectado: {sel}")
                        modal_found = True
                        break
                
                if modal_found:
                    logger.info("👉 Tentando selecionar especialidade...")
                    
                    # Tentar clicar no dropdown
                    # Procurar por "Selecione a especialidade" ou "Select"
                    dropdown_clicked = False
                    for dropdown_sel in ["text=Selecione a especialidade", "[role='combobox']", "select", ".css-control"]:
                        if page.is_visible(dropdown_sel):
                            page.click(dropdown_sel)
                            logger.info(f"  ✓ Dropdown clicado: {dropdown_sel}")
                            dropdown_clicked = True
                            break
                    
                    if dropdown_clicked:
                        page.wait_for_timeout(1000)
                        # Tentar selecionar a especialidade definida
                        # Primeiro tenta pelo texto exato, depois por partes
                        if page.is_visible(f"text={ESPECIALIDADE}"):
                            page.click(f"text={ESPECIALIDADE}")
                            logger.info(f"  ✓ Especialidade '{ESPECIALIDADE}' selecionada!")
                        else:
                            # Tentar clicar na primeira opção se não achar o texto exato
                            logger.warning(f"  ⚠️ Especialidade '{ESPECIALIDADE}' não encontrada textualmente. Tentando primeira opção...")
                            page.keyboard.press("Enter")
                        
                        # Clicar em "CONTINUE O AGENDAMENTO"
                        page.wait_for_timeout(1000)
                        btn_continue = "text=CONTINUE O AGENDAMENTO"
                        if page.is_visible(btn_continue):
                            page.click(btn_continue)
                            logger.info("  ✓ Botão Continuar clicado")
                        else:
                            page.keyboard.press("Enter")
                
                # ==================================================================
                # NAVEGAÇÃO - DADOS DO PACIENTE
                # ==================================================================
                
                logger.info("👤 Verificando se precisa preencher dados do paciente...")
                page.wait_for_timeout(3000)
                
                # Preencher Data de Nascimento
                if page.is_visible("text=Data de nascimento") or page.is_visible("input[placeholder*='nascimento']"):
                    logger.info("  ✍️ Preenchendo data de nascimento: 06/05/1995")
                    inputs_data = page.query_selector_all("input[type='tel'], input[placeholder*='nascimento'], input[name*='birth']")
                    if inputs_data:
                        # Tenta limpar e preencher
                        inputs_data[0].click()
                        inputs_data[0].fill("06/05/1995")
                    else:
                        # Tenta digitar diretamente se não achar input específico
                        page.keyboard.type("06051995")
                
                # Selecionar Sexo
                if page.is_visible("text=Sexo") or page.is_visible("text=Gênero") or page.is_visible("text=MASCULINO"):
                     logger.info("  🚹 Selecionando sexo MASCULINO...")
                     # Tenta clicar no dropdown se necessário
                     if page.is_visible("text=Selecione") or page.is_visible("[role='combobox']"):
                         page.click("[role='combobox']")
                         page.wait_for_timeout(500)
                     
                     # Clica na opção Masculino
                     if page.is_visible("text=MASCULINO"):
                         page.click("text=MASCULINO")
                     elif page.is_visible("text=Masculino"):
                         page.click("text=Masculino")

                # Clicar em "PROSSIGA" ou "Continuar" após dados
                if page.is_visible("text=PROSSIGA"):
                    page.click("text=PROSSIGA")
                    logger.info("  ➡️ Clicou em PROSSIGA (Dados Paciente)")
                    page.wait_for_timeout(2000)

                # ==================================================================
                # NAVEGAÇÃO - PAGAMENTO
                # ==================================================================
                
                logger.info("💰 Verificando seleção de pagamento...")
                page.wait_for_timeout(2000)
                
                # Selecionar "PARTICULAR"
                # O site costuma ter um dropdown ou botões para convênio/particular
                if page.is_visible("text=Selecione a forma de pagamento") or page.is_visible("text=Particular"):
                    logger.info("  Selecioando pagamento PARTICULAR...")
                    
                    # Se tiver dropdown, clica nele
                    if page.is_visible("text=Selecione a forma de pagamento"):
                        page.click("text=Selecione a forma de pagamento")
                        page.wait_for_timeout(500)
                    
                    # Clica em Particular
                    if page.is_visible("text=PARTICULAR"):
                        page.click("text=PARTICULAR")
                        logger.info("  ✓ Selecionado PARTICULAR")
                    elif page.is_visible("text=Particular"):
                        page.click("text=Particular")
                        logger.info("  ✓ Selecionado Particular")
                
                # Clicar em "PROSSIGA" ou "Continuar" após pagamento
                if page.is_visible("text=PROSSIGA"):
                    page.click("text=PROSSIGA")
                    logger.info("  ➡️ Clicou em PROSSIGA (Pagamento)")
                    page.wait_for_timeout(2000)
                
                # Tentar avançar genérico se houver outros botões
                logger.info("➡️ Tentando avançar fluxo final...")
                for btn_text in ["Continuar", "Próximo", "Confirmar", "Buscar", "Pesquisar", "PROSSIGA"]:
                    try:
                        # Tenta clicar apenas se visível e habilitado
                        if page.is_visible(f"text={btn_text}"):
                            page.click(f"text={btn_text}")
                            page.wait_for_timeout(1000)
                    except:
                        pass

                # Aguardar carregamento final da agenda
                logger.info("⏳ Aguardando carregamento da agenda (10s)...")
                page.wait_for_timeout(10000)
                
                # Salvar screenshot final para debug
                page.screenshot(path="debug_final_state.png")

                # ==================================================================
                # PROCESSAR DADOS
                # ==================================================================
                
                # 1. Tentar extrair de JSONs interceptados (Método Preferencial)
                if api_data_captured:
                    logger.info(f"📊 Processando {len(api_data_captured)} respostas de API interceptadas...")
                    for data in api_data_captured:
                        # Procurar recursivamente por chaves de data/hora
                        def find_slots(obj):
                            if isinstance(obj, dict):
                                for k, v in obj.items():
                                    # Padrões comuns de chaves de horário
                                    if k in ["time", "hora", "slot", "start", "date"] and isinstance(v, str):
                                        # Tentar parsear se parece horário
                                        if re.search(r"\d{2}:\d{2}", v):
                                            return [(v, obj)]
                                    elif isinstance(v, (dict, list)):
                                        res = find_slots(v)
                                        if res: return res
                            elif isinstance(obj, list):
                                res = []
                                for item in obj:
                                    r = find_slots(item)
                                    if r: res.extend(r)
                                return res
                            return []

                        # Tentar implementar lógica específica se descobrirmos a estrutura
                        # Por enquanto, vamos logar que capturamos e tentar extrair se óbvio
                        logger.debug(f"JSON data content keys: {str(data.keys()) if isinstance(data, dict) else 'list'}")

                # 2. Método Fallback: Scraping Visual (Mantido e Melhorado)
                logger.info("👀 Realizando scraping visual da página...")
                
                # Verificar iframes
                iframe_agendamento = None
                for frame in page.frames:
                    if any(x in frame.url.lower() for x in ["agenda", "schedule", "booking"]):
                        iframe_agendamento = frame
                        break
                
                page_to_search = iframe_agendamento if iframe_agendamento else page
                
                # Extrair horários visualmente
                horarios = self._buscar_horarios_na_pagina(page_to_search)
                
                if horarios:
                    logger.info(f"✅ Encontrados {len(horarios)} horários via scraping visual!")
                    return horarios
                
                logger.warning("⚠️ Nenhum horário encontrado via visual ou API.")
                return []

            except Exception as e:
                logger.error(f"❌ Erro crítico: {str(e)}")
                # Tentar tirar screenshot apenas se página estiver ativa
                try:
                    page.screenshot(path="error_fatal.png")
                except:
                    pass
                return []
            finally:
                try:
                    browser.close()
                except:
                    pass
        
        return []


class MonitorConsulta:
    """Classe principal que orquestra a verificação e notificação."""

    def __init__(self):
        """Inicializa o monitor de consultas."""
        self.scraper = DisponibilidadeScraper(MEDICA_ID)
        # Type check - garantir que variáveis de ambiente estão definidas
        if not EMAIL_REMETENTE or not SENHA_EMAIL:
            raise ValueError("EMAIL_SENDER e EMAIL_PASSWORD devem estar configurados")
        self.notifier = EmailNotifier(EMAIL_REMETENTE, SENHA_EMAIL)

    def filtrar_horarios_anteriores(
        self, horarios: List[Horario], data_limite: str
    ) -> List[Horario]:
        """
        Filtra horários que são anteriores à data limite.

        Args:
            horarios: Lista de horários para filtrar
            data_limite: Data limite no formato YYYY-MM-DD

        Returns:
            Lista de horários anteriores à data limite
        """
        try:
            data_consulta_obj = datetime.strptime(data_limite, "%Y-%m-%d")
        except ValueError:
            logger.error(f"❌ Data limite inválida: {data_limite}")
            return []

        horarios_antes = []
        
        # Mapeamento de meses em português
        meses_pt = {
            "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
            "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
            "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
            "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
        }

        logger.info(f"🔎 Verificando {len(horarios)} horários encontrados contra data limite: {data_limite}")

        for horario in horarios:
            try:
                data_horario: Optional[datetime] = None
                data_str = horario.data.lower().strip()
                
                # 1. Tentar parser numérico direto
                formatos = ["%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y", "%Y-%m-%d"]
                for formato in formatos:
                    try:
                        data_horario = datetime.strptime(data_str, formato)
                        break
                    except ValueError:
                        continue
                
                # 2. Se falhar, tentar parser textual (ex: "20 de outubro")
                if data_horario is None:
                    # Remover dia da semana se houver (ex: "segunda, 20 de...")
                    if "," in data_str:
                        data_str = data_str.split(",", 1)[1].strip()
                    
                    # Procurar padrão "dia de mês"
                    match = re.search(r"(\d{1,2})\s+(?:de\s+)?([a-zçã]+)", data_str)
                    if match:
                        dia = int(match.group(1))
                        mes_nome = match.group(2)
                        # Tentar mapear nome do mês
                        mes_num = next((v for k, v in meses_pt.items() if k in mes_nome), None)
                        
                        if mes_num:
                            # Assumir ano atual ou próximo (logica simples)
                            ano_atual = datetime.now().year
                            mes_atual = datetime.now().month
                            
                            # Se o mês encontrado for menor que o mês atual, provavelmente é ano que vem
                            ano = ano_atual
                            if mes_num < mes_atual: 
                                ano += 1
                                
                            data_horario = datetime(ano, mes_num, dia)

                # Verificação final
                if data_horario:
                    # Comparação
                    if data_horario.date() < data_consulta_obj.date():
                        horarios_antes.append(horario)
                        logger.info(
                            f"  ✅ ENCONTRADO! {data_horario.strftime('%d/%m/%Y')} é ANTES de {data_consulta_obj.strftime('%d/%m/%Y')}"
                        )
                    else:
                        logger.info(
                            f"  ❌ Ignorado: {data_horario.strftime('%d/%m/%Y')} não é antes de {data_consulta_obj.strftime('%d/%m/%Y')}"
                        )
                else:
                    logger.warning(f"  ⚠️ Não foi possível converter data: '{horario.data}'")

            except Exception as e:
                logger.debug(f"Erro ao processar horário {horario.data}: {e}")
                continue

        return horarios_antes

    def executar(self) -> None:
        """Executa o processo completo de verificação e notificação."""
        logger.info("\n" + "=" * 60)
        logger.info(f"🏥 VERIFICAÇÃO DE DISPONIBILIDADE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60 + "\n")

        # Validar configurações antes de começar
        if not ConfigValidator.validar_configuracoes():
            logger.error("❌ Configurações inválidas. Abortando execução.")
            sys.exit(1)

        # Buscar horários disponíveis
        horarios = self.scraper.buscar()

        if not horarios:
            logger.info("ℹ️ Nenhum horário disponível encontrado no momento.")
            return

        # Filtrar horários antes da data atual da consulta
        horarios_antes = self.filtrar_horarios_anteriores(horarios, DATA_CONSULTA_ATUAL)

        # Se houver horários antes, enviar email
        if horarios_antes:
            logger.info(
                f"\n🎯 {len(horarios_antes)} horário(s) encontrado(s) antes de {DATA_CONSULTA_ATUAL}!"
            )
            logger.info("📧 Enviando email de notificação...")
            self.notifier.enviar(EMAIL_DESTINO, horarios_antes)
        else:
            logger.info(f"\nℹ️ Não há horários disponíveis antes de {DATA_CONSULTA_ATUAL}")


def main() -> None:
    """Função principal."""
    try:
        monitor = MonitorConsulta()
        monitor.executar()
    except KeyboardInterrupt:
        logger.info("\n⚠️ Execução interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
