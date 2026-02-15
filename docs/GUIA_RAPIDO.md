# 🚀 Guia Rápido de Configuração

## 📋 Checklist de Configuração

### ✅ 1. Criar repositório no GitHub
- Criar novo repositório (pode ser privado)
- Fazer upload dos arquivos deste projeto

### ✅ 2. Configurar Secrets no GitHub

Vá em: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Criar 2 secrets:

| Nome | Valor |
|------|-------|
| `EMAIL_SENDER` | `seu-email@gmail.com` |
| `EMAIL_PASSWORD` | Senha de app do Gmail (16 dígitos) |

### ✅ 3. Obter senha de aplicativo do Gmail

1. Acesse: https://myaccount.google.com/apppasswords
2. Crie nova senha de app
3. Copie os 16 caracteres (sem espaços)
4. Use no secret `EMAIL_PASSWORD`

### ✅ 4. Editar arquivo check_availability.py

Localizar e editar as linhas:

```python
NOME_MEDICA = "Isadora Leda Braga"
ESPECIALIDADE = "Endocrinologia Geral"
LOCAL_ATENDIMENTO = "Hospital Villa Lobos"
DATA_CONSULTA_ATUAL = "2026-03-11"  # Formato: YYYY-MM-DD
EMAIL_DESTINO = "seu-email@exemplo.com"

# ID já configurado para Dra. Isadora:
MEDICA_ID = "725717342"
```

### ✅ 5. Fazer commit e push

```bash
git add .
git commit -m "Configuração inicial"
git push
```

### ✅ 6. Ativar GitHub Actions

- Ir em `Actions` no repositório
- Clicar em "I understand my workflows, go ahead and enable them"

### ✅ 7. Testar execução manual

1. `Actions` → `Verificar Disponibilidade Consulta`
2. `Run workflow` → `Run workflow`
3. Aguardar 1-2 minutos
4. Verificar logs

### ✅ 8. Confirmar recebimento de email

- Checar caixa de entrada
- Verificar spam/lixo eletrônico

---

## ⚡ Frequência de Verificação

**Por padrão:** a cada 15 minutos

Para alterar, edite `.github/workflows/check_availability.yml`:

```yaml
cron: '*/15 * * * *'  # A cada 15 minutos
cron: '*/30 * * * *'  # A cada 30 minutos
cron: '0 * * * *'     # A cada hora
cron: '0 8-18 * * *'  # De hora em hora, das 8h às 18h
```

---

## 🔧 Ajustes Necessários

> [!WARNING]
> O script usa seletores genéricos do site.

Se o script não encontrar a médica, você precisará ajustar os seletores CSS:

1. Execute o workflow manualmente
2. Baixe os screenshots de debug (Actions → Artifacts)
3. Abra o site da Rede D'Or em modo desenvolvedor (F12)
4. Identifique os seletores corretos
5. Ajuste as linhas em `check_availability.py`

Exemplo de ajustes comuns:
```python
search_field = page.wait_for_selector('input[id="campo-busca"]')
page.click('button.btn-buscar')
horarios = page.query_selector_all('div.card-horario')
```

---

## 📊 Monitoramento

### Acompanhe execuções
- GitHub → Actions → Ver histórico de execuções
- Cada execução fica salva por 90 dias

### Verificar logs
- Clicar na execução específica
- Ver detalhes de cada step

---

## ⚠️ Limites

### GitHub Actions (plano gratuito)
- **2.000 minutos/mês**
- Cada execução leva ~2 minutos
- Com 15 min de intervalo: ~192 execuções/dia = ~384 min/dia
- **Total mensal:** ~11.520 min (EXCEDE O LIMITE!)

> [!IMPORTANT]
> **Solução:** Ajustar frequência ou limitar horário

Exemplo - apenas horário comercial (8h-18h):
```yaml
cron: '*/15 8-18 * * 1-5'  # Seg-Sex, 8h-18h, a cada 15 min
```

### Gmail
- Limite de 500 emails/dia (mais que suficiente)

---

## 🆘 Problemas Comuns

### 1. "Email não enviado"
→ Verificar secrets configurados  
→ Usar senha de APP (não senha normal)  
→ Verificar 2FA ativado no Gmail

### 2. "Médica não encontrada"
→ Ajustar seletores CSS  
→ Verificar nome exato da médica  
→ Ver screenshots de debug

### 3. "Workflow não executa"
→ Ativar Actions no repositório  
→ Verificar sintaxe do arquivo .yml  
→ Repositório deve ter pelo menos 1 commit

---

## 📞 Suporte

Para problemas técnicos:
1. Verificar logs no GitHub Actions
2. Baixar screenshots de debug
3. Ajustar seletores conforme estrutura do site

---

## ✅ Tudo Pronto!

Após configuração, você receberá emails automaticamente quando houver horários disponíveis antes da sua consulta atual.

**Boa sorte!** 🍀
