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

    def _extrair_data_calendario(self, page, mes_ano_text: str) -> str:
        """
        Extrai a data atualmente selecionada no calendário da agenda.
        
        Args:
            page: Página do Playwright
            mes_ano_text: Texto do mês/ano visível (ex: "Mar, 2026")
        
        Returns:
            Data formatada como dd/mm/yyyy
        """
        meses_abrev = {
            "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4, "Mai": 5, "Jun": 6,
            "Jul": 7, "Ago": 8, "Set": 9, "Out": 10, "Nov": 11, "Dez": 12
        }
        
        try:
            # Tentar extrair mês e ano do texto (ex: "Mar, 2026")
            if mes_ano_text:
                match = re.match(r"([A-Za-z]+),?\s*(\d{4})", mes_ano_text)
                if match:
                    mes_str = str(match.group(1)).capitalize()
                    mes_nome = mes_str[:3]
                    ano = int(match.group(2))
                    mes = meses_abrev.get(mes_nome, datetime.now().month)
                    
                    # Tentar encontrar o dia selecionado (highlighted/active)
                    # Na Rede D'Or, o dia selecionado tem classe especial
                    dia = datetime.now().day
                    try:
                        # Buscar elementos com algum estado ativo/selecionado
                        selected = page.query_selector("[class*='selected'], [class*='active'], [class*='highlight'], [aria-selected='true']")
                        if selected:
                            texto_dia = selected.inner_text().strip()
                            if texto_dia.isdigit():
                                dia = int(texto_dia)
                    except:
                        pass
                    
                    return f"{dia:02d}/{mes:02d}/{ano}"
        except:
            pass
        
        return datetime.now().strftime("%d/%m/%Y")

    def buscar(self) -> List[Horario]:
        """
        Busca disponibilidade no site usando automação com seletores
        de Web Components cura-* mapeados manualmente no browser real.

        Returns:
            Lista de horários disponíveis
        """
        logger.info(f"🔍 Iniciando busca por {NOME_MEDICA}...")
        logger.info(f"📱 Acessando URL: {self.url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900},
                locale="pt-BR"
            )
            page = context.new_page()

            try:
                page.set_default_timeout(30000)
                
                logger.info("🌍 Navegando para o site...")
                page.goto(self.url, wait_until="networkidle")
                page.wait_for_timeout(3000)

                # ==================================================================
                # ETAPA 1: MODAL "VAMOS COMEÇAR" - Selecionar Especialidade
                # ==================================================================
                logger.info("🛑 Etapa 1: Modal de Especialidade...")
                
                # Aguardar modal com texto "Vamos começar!"
                try:
                    page.wait_for_selector("text=Vamos começar!", timeout=10000)
                    logger.info("  ✅ Modal 'Vamos começar!' detectado")
                except:
                    logger.warning("  ⚠️ Modal não detectado, tentando continuar mesmo assim...")

                # Clicar no dropdown de especialidade (cura-select)
                # O input interno tem placeholder "Selecione a especialidade"
                dropdown_sel = "input[placeholder='Selecione a especialidade']"
                try:
                    page.click(dropdown_sel)
                    logger.info("  ✓ Dropdown de especialidade clicado")
                    page.wait_for_timeout(1000)
                except:
                    # Fallback: tentar role=combobox
                    page.click("[role='combobox']")
                    logger.info("  ✓ Dropdown clicado via [role='combobox']")
                    page.wait_for_timeout(1000)
                
                # Selecionar "Endocrinologia Geral" (aparece como cura-select-option)
                try:
                    page.click(f"text={ESPECIALIDADE}")
                    logger.info(f"  ✓ Especialidade '{ESPECIALIDADE}' selecionada!")
                except:
                    # Tentar opção em cura-select-option
                    page.click("cura-select-option >> nth=0")
                    logger.info("  ✓ Primeira opção de especialidade selecionada")
                
                page.wait_for_timeout(1000)
                
                # Clicar no botão "CONTINUE O AGENDAMENTO" (cura-button, NÃO button nativo!)
                try:
                    page.click("cura-button >> text=CONTINUE O AGENDAMENTO")
                    logger.info("  ✓ Botão 'CONTINUE O AGENDAMENTO' clicado via cura-button")
                except:
                    # Fallback: tentar pelo texto direto
                    try:
                        page.click("text=CONTINUE O AGENDAMENTO")
                        logger.info("  ✓ Botão 'CONTINUE O AGENDAMENTO' clicado via text")
                    except:
                        logger.error("  ❌ Botão 'CONTINUE O AGENDAMENTO' NÃO encontrado!")
                        page.screenshot(path="error_step1_continue.png")
                        browser.close()
                        return []
                
                # Aguardar navegação para /paciente
                logger.info("  ⏳ Aguardando navegação para página do paciente...")
                try:
                    page.wait_for_url("**/paciente**", timeout=15000)
                    logger.info("  ✅ Navegou para página do paciente!")
                except:
                    logger.warning("  ⚠️ Timeout esperando navegação, verificando estado atual...")
                    page.wait_for_timeout(3000)
                
                # ==================================================================
                # ETAPA 2: DADOS DO PACIENTE (Data Nascimento + Sexo Biológico)
                # ==================================================================
                logger.info("👤 Etapa 2: Dados do Paciente...")
                page.wait_for_timeout(2000)
                
                # Preencher Data de Nascimento
                # O campo é cura-input-text com input placeholder="dd/mm/aaaa"
                data_nasc_sel = "input[placeholder='dd/mm/aaaa']"
                try:
                    page.wait_for_selector(data_nasc_sel, timeout=10000)
                    page.click(data_nasc_sel)
                    page.fill(data_nasc_sel, "")
                    # Digitar sem barras - a máscara do campo adiciona automaticamente
                    page.type(data_nasc_sel, "06051995", delay=80)
                    page.press(data_nasc_sel, "Tab")
                    logger.info("  ✍️ Data de nascimento preenchida: 06/05/1995")
                except Exception as e:
                    logger.error(f"  ❌ Erro ao preencher data de nascimento: {e}")
                    page.screenshot(path="error_step2_birthdate.png")
                
                page.wait_for_timeout(500)
                
                # Selecionar Sexo Biológico  
                # O campo é cura-select com input placeholder="Selecione o sexo biológico"
                sexo_sel = "input[placeholder='Selecione o sexo biológico']"
                try:
                    page.click(sexo_sel)
                    logger.info("  🚹 Dropdown de sexo aberto")
                    page.wait_for_timeout(500)
                    
                    # Clicar em MASCULINO (cura-select-option)
                    page.click("text=MASCULINO")
                    logger.info("  ✓ Sexo MASCULINO selecionado")
                except:
                    try:
                        # Fallback: tentar Masculino com M minúsculo
                        page.click("text=Masculino")
                        logger.info("  ✓ Sexo Masculino selecionado")
                    except Exception as e:
                        logger.error(f"  ❌ Erro ao selecionar sexo: {e}")
                
                page.wait_for_timeout(500)
                
                # Clicar em PROSSIGA (cura-button)
                try:
                    page.click("cura-button >> text=PROSSIGA")
                    logger.info("  ➡️ Clicou em PROSSIGA (Dados Paciente)")
                except:
                    try:
                        page.click("text=PROSSIGA")
                        logger.info("  ➡️ Clicou em PROSSIGA via text")
                    except:
                        logger.error("  ❌ Botão PROSSIGA não encontrado!")
                        page.screenshot(path="error_step2_prossiga.png")
                
                # Aguardar navegação para /pagamento
                logger.info("  ⏳ Aguardando navegação para página de pagamento...")
                try:
                    page.wait_for_url("**/pagamento**", timeout=15000)
                    logger.info("  ✅ Navegou para página de pagamento!")
                except:
                    logger.warning("  ⚠️ Timeout esperando pagamento, verificando estado atual...")
                    page.wait_for_timeout(3000)
                
                # ==================================================================
                # ETAPA 3: PAGAMENTO (Selecionar Particular)
                # ==================================================================
                logger.info("💰 Etapa 3: Pagamento...")
                page.wait_for_timeout(2000)
                
                # Clicar no dropdown de forma de pagamento
                # cura-select com placeholder "Selecione..."
                pagamento_sel = "input[placeholder='Selecione...']"
                try:
                    page.click(pagamento_sel)
                    logger.info("  Dropdown de pagamento aberto")
                    page.wait_for_timeout(500)
                    
                    # Selecionar "Particular"
                    page.click("text=Particular")
                    logger.info("  ✓ Selecionado: Particular")
                except Exception as e:
                    logger.error(f"  ❌ Erro ao selecionar pagamento: {e}")
                    page.screenshot(path="error_step3_pagamento.png")
                
                page.wait_for_timeout(1000)
                
                # Clicar em PROSSIGA (cura-button)
                try:
                    page.click("cura-button >> text=PROSSIGA")
                    logger.info("  ➡️ Clicou em PROSSIGA (Pagamento)")
                except:
                    try:
                        page.click("text=PROSSIGA")
                        logger.info("  ➡️ Clicou em PROSSIGA via text")
                    except:
                        logger.error("  ❌ Botão PROSSIGA não encontrado na etapa de pagamento!")
                        page.screenshot(path="error_step3_prossiga.png")
                
                # ==================================================================
                # ETAPA 4: AGENDA - Capturar datas e horários
                # ==================================================================
                logger.info("📅 Etapa 4: Agenda - Capturando horários...")
                
                # A agenda pode abrir em nova aba ou na mesma página
                page.wait_for_timeout(5000)
                
                # Verificar se abriu nova aba
                all_pages = context.pages
                agenda_page = page
                if len(all_pages) > 1:
                    agenda_page = all_pages[-1]  # Pegar última aba aberta
                    logger.info(f"  📑 Nova aba detectada! URL: {agenda_page.url}")
                    agenda_page.wait_for_load_state("networkidle")
                else:
                    # Aguardar na mesma página
                    try:
                        page.wait_for_url("**/agenda**", timeout=10000)
                        logger.info(f"  ✅ Navegou para agenda: {page.url}")
                    except:
                        logger.info(f"  📌 URL atual: {page.url}")
                
                agenda_page.wait_for_timeout(3000)
                
                # Salvar screenshot da agenda para debug
                agenda_page.screenshot(path="debug_agenda.png")
                logger.info("  📸 Screenshot da agenda salvo em debug_agenda.png")
                
                # CAPTURAR HORÁRIOS da agenda
                # Os horários são exibidos como cura-button-outline com texto "HH:MM"
                horarios_encontrados: List[Horario] = []
                
                # Primeiro, verificar qual data está selecionada no calendário
                # O mês/ano é mostrado como texto (ex: "Mar, 2026")
                mes_ano_text = ""
                try:
                    # Buscar o texto do mês/ano visível
                    mes_elements = agenda_page.query_selector_all("text=/[A-Z][a-z]{2},\\s*\\d{4}/")
                    if mes_elements:
                        mes_ano_text = mes_elements[0].inner_text().strip()
                        logger.info(f"  📆 Mês atual no calendário: {mes_ano_text}")
                except:
                    pass
                
                # Capturar datas disponíveis no calendário
                # Datas disponíveis são divs clicáveis com números
                # Vamos buscar todos os botões de horário (cura-button-outline)
                horarios_btns = agenda_page.query_selector_all("cura-button-outline")
                
                if horarios_btns:
                    logger.info(f"  🎯 Encontrados {len(horarios_btns)} slots de horário!")
                    
                    # Extrair a data selecionada atualmente
                    data_selecionada = self._extrair_data_calendario(agenda_page, mes_ano_text)
                    
                    for btn in horarios_btns:
                        try:
                            texto = btn.inner_text().strip()
                            # Verificar se parece com horário (HH:MM)
                            hora_match = re.search(r"(\d{2}:\d{2})", texto)
                            if hora_match:
                                hora = hora_match.group(1)
                                is_encaixe = "(E)" in texto or "E" in texto.replace(hora, "").strip()
                                
                                horario = Horario(
                                    data=data_selecionada,
                                    hora=hora,
                                    texto_original=f"{data_selecionada} {hora}" + (" (Encaixe)" if is_encaixe else ""),
                                )
                                horarios_encontrados.append(horario)
                                logger.info(f"    ⏰ {data_selecionada} às {hora}" + (" (Encaixe)" if is_encaixe else ""))
                        except:
                            continue
                else:
                    logger.warning("  ⚠️ Nenhum cura-button-outline encontrado. Tentando scraping visual...")
                    
                    # Fallback: buscar qualquer elemento com padrão HH:MM
                    all_text = agenda_page.inner_text("body")
                    hora_matches = re.findall(r"\b(\d{2}:\d{2})\b", all_text)
                    if hora_matches:
                        logger.info(f"  🔍 Encontrados {len(hora_matches)} padrões HH:MM via texto")
                        for hora in hora_matches:
                            horario = Horario(
                                data=datetime.now().strftime("%d/%m/%Y"),
                                hora=hora,
                                texto_original=f"Horário: {hora}",
                            )
                            horarios_encontrados.append(horario)
                            logger.info(f"    ⏰ Horário encontrado: {hora}")
                
                if horarios_encontrados:
                    logger.info(f"✅ Total: {len(horarios_encontrados)} horários encontrados!")
                else:
                    logger.warning("⚠️ Nenhum horário encontrado na agenda.")
                    # Log do conteúdo da página para debug
                    try:
                        page_text = agenda_page.inner_text("body")[:500]
                        logger.info(f"  📄 Conteúdo visível (primeiros 500 chars): {page_text}")
                    except:
                        pass
                
                browser.close()
                return horarios_encontrados

            except Exception as e:
                logger.error(f"❌ Erro crítico: {str(e)}")
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
