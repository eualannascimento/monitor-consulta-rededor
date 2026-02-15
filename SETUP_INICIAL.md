# ⚡ Setup Inicial - Ações Necessárias

## 🔐 1. Configurar GitHub Secrets (OBRIGATÓRIO)

O workflow **NÃO VAI FUNCIONAR** sem esses secrets configurados!

### Passos:

1. Acesse: https://github.com/eualannascimento/monitor-consulta-rededor/settings/secrets/actions

2. Clique em **"New repository secret"**

3. Crie o primeiro secret:
   - **Name:** `EMAIL_SENDER`
   - **Value:** `seu-email@gmail.com` (seu email Gmail)
   - Clique em **"Add secret"**

4. Crie o segundo secret:
   - **Name:** `EMAIL_PASSWORD`
   - **Value:** Senha de aplicativo do Gmail (veja abaixo)
   - Clique em **"Add secret"**

### 📧 Como Obter Senha de Aplicativo do Gmail

1. Acesse: https://myaccount.google.com/security
2. Ative **"Verificação em duas etapas"** (se ainda não tiver)
3. Acesse: https://myaccount.google.com/apppasswords
4. Selecione:
   - **App:** Email
   - **Dispositivo:** Outro (digite "GitHub Monitor")
5. Clique em **"Gerar"**
6. Copie a senha de 16 caracteres (sem espaços)
7. Use essa senha no secret `EMAIL_PASSWORD`

---

## ✏️ 2. Editar Configurações no Código (OBRIGATÓRIO)

Você precisa personalizar o código com seus dados:

1. Acesse: https://github.com/eualannascimento/monitor-consulta-rededor/blob/main/check_availability.py

2. Clique no ícone de **lápis** (Edit)

3. Localize as linhas (próximo do topo):
   ```python
   # ========== CONFIGURAÇÕES (EDITE AQUI) ==========
   NOME_MEDICA = "Isadora Leda Braga"  
   ESPECIALIDADE = "Endocrinologia Geral"
   LOCAL_ATENDIMENTO = "Hospital Villa Lobos"
   DATA_CONSULTA_ATUAL = "2026-03-11"  # ← ALTERE PARA SUA DATA
   EMAIL_DESTINO = "seu-email@exemplo.com"  # ← ALTERE PARA SEU EMAIL
   MEDICA_ID = "725717342"
   ```

4. **Altere:**
   - `DATA_CONSULTA_ATUAL` → Data da sua consulta atual (formato: YYYY-MM-DD)
   - `EMAIL_DESTINO` → Seu email onde quer receber notificações
   - (Opcional) Outros dados se for para outra médica

5. Clique em **"Commit changes"**

---

## ⚙️ 3. Ativar GitHub Actions (OBRIGATÓRIO)

1. Acesse: https://github.com/eualannascimento/monitor-consulta-rededor/actions

2. Se aparecer "Workflows aren't being run on this repository", clique em:
   **"I understand my workflows, go ahead and enable them"**

---

## 🧪 4. Testar Primeira Execução (RECOMENDADO)

Antes de deixar rodando automaticamente, teste manualmente:

1. Acesse: https://github.com/eualannascimento/monitor-consulta-rededor/actions

2. Clique em **"Verificar Disponibilidade Consulta"** (lado esquerdo)

3. Clique no botão **"Run workflow"** (lado direito)

4. Clique em **"Run workflow"** novamente (botão verde)

5. Aguarde 1-2 minutos

6. Clique na execução que apareceu

7. Veja os logs para verificar se está funcionando

### 🐛 Se Der Erro:

- **Email error:** Verifique secrets configurados corretamente
- **Médica não encontrada:** Veja screenshots em "Artifacts" no final da execução
- **Sem horários:** Normal se não houver disponibilidade no momento

---

## ✅ Pronto! Depois disso:

- O workflow executará **automaticamente a cada 15 minutos**
- Você receberá email quando houver horários antes da sua consulta
- Não precisa fazer mais nada!

---

## 🔧 (Opcional) Ajustar Frequência

Por padrão executa a cada 15 minutos, mas isso pode **exceder o limite gratuito do GitHub Actions**.

**Recomendado:** Limitar para horário comercial:

1. Edite: `.github/workflows/check_availability.yml`
2. Altere a linha do `cron`:
   ```yaml
   # Atual:
   - cron: '*/15 * * * *'  # A cada 15 min (24h/dia)
   
   # Recomendado:
   - cron: '*/15 8-18 * * 1-5'  # A cada 15 min, Seg-Sex, 8h-18h
   ```

---

## 📞 Problemas?

- Ver logs: https://github.com/eualannascimento/monitor-consulta-rededor/actions
- Documentação completa: [`README.md`](./README.md)
- Ajustar seletores: [`docs/GUIA_AJUSTE_SELETORES.md`](./docs/GUIA_AJUSTE_SELETORES.md)
