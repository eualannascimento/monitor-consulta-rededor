# 📦 Como Fazer Upload deste Projeto no GitHub

Você tem este projeto com todos os arquivos já organizados na estrutura correta!

## 🚀 Método Mais Fácil - Upload via Interface Web

### 1. Criar Repositório

1. Acesse: https://github.com/new (faça login se necessário)

2. Configure o repositório:
   - **Repository name:** `monitor-consulta-rededor`
   - **Description:** `Monitor de disponibilidade de consultas Rede D'Or`
   - **Privado:** ✅ (RECOMENDADO - para proteger seus dados)
   - **NÃO** marque "Add a README file" (já temos um)
   - Clique em "Create repository"

### 2. Upload dos Arquivos

Na página que abrir:

1. Procure: _"...or create a new repository on the command line"_
   
   > [!TIP]
   > **IGNORE** os comandos por enquanto!

2. Em vez disso, clique em: **"uploading an existing file"** (link pequeno no meio da página)

3. Arraste **TODOS** os arquivos desta pasta para a área de upload:
   
   - ✓ `check_availability.py`
   - ✓ `requirements.txt`
   - ✓ `README.md`
   - ✓ `.gitignore`
   - ✓ `.github/workflows/check_availability.yml` ← IMPORTANTE: manter estrutura de pastas!
   
   > [!TIP]
   > Você pode arrastar a pasta `.github` inteira!

4. Escreva mensagem de commit: `"Configuração inicial do monitor de consultas"`

5. Clique em **"Commit changes"**

✅ **Repositório criado com sucesso!**

---

## 🔐 Configurar Secrets (ESSENCIAL!)

> [!CAUTION]
> Sem isso o script **NÃO FUNCIONA**!

### 1. Acessar Configurações

No repositório, vá em: `Settings` → `Secrets and variables` → `Actions`

### 2. Criar Secrets

Clique em **"New repository secret"** e crie:

**Secret #1:**
- Name: `EMAIL_SENDER`
- Value: `seu-email@gmail.com`
- Add secret

**Secret #2:**
- Name: `EMAIL_PASSWORD`
- Value: `[senha de app do Gmail - 16 dígitos]`
- Add secret

### 📧 Como obter senha de app do Gmail

1. https://myaccount.google.com/security
2. Ative "Verificação em duas etapas"
3. https://myaccount.google.com/apppasswords
4. App: **Email** | Dispositivo: **Outro**
5. Nome: "GitHub Monitor"
6. Copie os 16 dígitos
7. Use no secret `EMAIL_PASSWORD`

---

## ⚙️ Ativar GitHub Actions

1. Vá em: `Actions` (aba no topo)
2. Clique: **"I understand my workflows, go ahead and enable them"**

---

## 🧪 Testar Primeira Execução

1. `Actions` → `"Verificar Disponibilidade Consulta"`
2. `Run workflow` → `Run workflow`
3. Aguarde 1-2 minutos
4. Veja os logs

> [!WARNING]
> É **NORMAL** precisar ajustar seletores na primeira vez!  
> Leia [`GUIA_AJUSTE_SELETORES.md`](./GUIA_AJUSTE_SELETORES.md) se não encontrar horários.

---

## 📝 Editar Configurações

Você precisa editar apenas 1 linha:

1. No repositório, abra: `check_availability.py`
2. Clique no ícone de lápis (Edit)
3. Procure por: `EMAIL_DESTINO = "seu-email@exemplo.com"`
4. Altere para seu email real
5. Commit changes

---

## 🎉 Pronto! O Sistema está Funcionando!

A cada 15 minutos ele verificará automaticamente.

Você receberá email quando houver horários disponíveis antes da sua data agendada.

---

## 💡 Dicas Finais

- 📊 Monitore as execuções em: `Actions`
- 📸 Screenshots de debug ficam em: `Artifacts`
- ⚙️ Ajuste a frequência editando: `.github/workflows/check_availability.yml`
  - Linha: `cron: '*/15 * * * *'`

---

## 📞 Precisa de Ajuda?

- Não encontrou horários? → [`GUIA_AJUSTE_SELETORES.md`](./GUIA_AJUSTE_SELETORES.md)
- Dúvidas de configuração? → [`GUIA_RAPIDO.md`](./GUIA_RAPIDO.md)
- Documentação completa? → [`README.md`](../README.md)

**Boa sorte!** 🍀
