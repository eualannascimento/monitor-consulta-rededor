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
EMAIL_DESTINO = "seu-email@exemplo.com"  # Seu email para receber notificações

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
        Busca disponibilidade no site.

        Returns:
            Lista de horários disponíveis
        """
        logger.info(f"🔍 Iniciando busca por {NOME_MEDICA}...")
        logger.info(f"📱 Acessando URL: {self.url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            try:
                page.goto(self.url, wait_until="domcontentloaded", timeout=self.timeout)

                logger.info("⏳ Aguardando carregamento completo...")
                page.wait_for_timeout(8000)

                # Salvar screenshot para debug
                page.screenshot(path="debug_screenshot.png", full_page=True)
                logger.info("📸 Screenshot salva: debug_screenshot.png")

                # Verificar se há iframe de agendamento
                logger.info("🔍 Verificando iframes...")
                iframe_agendamento = None

                for frame in page.frames:
                    frame_url = frame.url.lower()
                    keywords = ["agenda", "schedule", "appointment", "medcloud", "booking"]

                    if any(keyword in frame_url for keyword in keywords):
                        logger.info(f"✅ Iframe de agendamento encontrado: {frame.url}")
                        iframe_agendamento = frame
                        break

                # Decidir qual página usar (iframe ou principal)
                page_to_use = iframe_agendamento if iframe_agendamento else page
                context_msg = "iframe" if iframe_agendamento else "página principal"
                logger.info(f"📝 Trabalhando na {context_msg}...")

                # Buscar horários disponíveis
                logger.info("📆 Buscando horários disponíveis...")
                horarios = self._buscar_horarios_na_pagina(page_to_use)

                # Se não encontrou horários, salvar HTML para análise
                if not horarios:
                    logger.warning("⚠️ Não foi possível encontrar horários automaticamente.")
                    logger.info("💾 Salvando HTML para análise manual...")

                    html_content = page_to_use.content()
                    with open("page_html.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    logger.info("✓ HTML salvo em: page_html.html")

                logger.info(f"✅ Total de horários encontrados: {len(horarios)}")

                browser.close()
                return horarios

            except Exception as e:
                logger.error(f"❌ Erro durante busca: {str(e)}")
                try:
                    page.screenshot(path="error_screenshot.png", full_page=True)
                    logger.info("📸 Screenshot de erro salva: error_screenshot.png")
                except Exception:
                    pass
                browser.close()
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
            logger.error(f"❌ Data inválida: {data_limite}")
            return []

        horarios_antes = []

        for horario in horarios:
            try:
                # Tentar converter data do horário (diferentes formatos possíveis)
                formatos = ["%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y"]

                data_horario: Optional[datetime] = None
                for formato in formatos:
                    try:
                        data_horario = datetime.strptime(horario.data, formato)
                        break
                    except ValueError:
                        continue

                if data_horario is not None and data_horario < data_consulta_obj:
                    horarios_antes.append(horario)
                    logger.info(
                        f"✨ Horário anterior encontrado: {horario.data} às {horario.hora}"
                    )

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
