# 🔧 Guia de Ajuste de Seletores

O script está configurado para a **Dra. Isadora Leda Braga** (ID: `725717342`) no Hospital Villa Lobos.

> [!WARNING]
> Sites de agendamento mudam frequentemente sua estrutura HTML.  
> Se o script não encontrar horários na primeira execução, siga este guia.

---

## 📋 Passo 1: Executar e Verificar Logs

1. Execute o workflow manualmente no GitHub Actions
2. Verifique os logs da execução
3. Procure por mensagens como:
   - `"✓ Encontrados X elementos com: div[class*='horario']"`
   - `"⚠️ Não foi possível encontrar horários automaticamente"`

---

## 📸 Passo 2: Baixar Screenshots de Debug

Se o script não encontrar horários:

1. Vá em GitHub `Actions` → Execução mais recente
2. Role até o final e procure "Artifacts"
3. Baixe "debug-screenshots"
4. Você receberá:
   - `debug_screenshot.png` (tela principal)
   - `page_ html.html` (código fonte da página)

---

## 🔍 Passo 3: Inspecionar a Página

### Opção A - Manualmente (mais fácil)

1. Abra https://www.rededorsaoluiz.com.br/paciente/marcar-consulta/?medicom=725717342
2. Pressione `F12` para abrir DevTools
3. Clique na setinha (Inspector) no canto superior esquerdo
4. Clique em um horário disponível na página
5. O DevTools mostrará o HTML daquele elemento

### Opção B - Usando HTML salvo

1. Abra o arquivo `page_html.html` baixado dos Artifacts
2. Procure por textos como horários (14:30, 15:00, etc)
3. Veja a estrutura ao redor desses textos

---

## ✏️ Passo 4: Ajustar Seletores no Código

Edite o arquivo `check_availability.py`, localize a seção:

```python
selectors_horarios = [
    'div[class*="horario"]',
    'button[class*="schedule"]',
    # ... outros seletores
]
```

**ADICIONE** os seletores corretos que você identificou.

### Exemplos

**Exemplo 1** - Se os horários estão em `<div class="slot-item">`:
```python
selectors_horarios = [
    'div.slot-item',        # ← ADICIONE ESTE
    'div[class*="horario"]',
    # ... resto dos seletores
]
```

**Exemplo 2** - Se os horários estão em `<button data-time="14:30">`:
```python
selectors_horarios = [
    'button[data-time]',    # ← ADICIONE ESTE
    'div[class*="horario"]',
    # ... resto dos seletores
]
```

**Exemplo 3** - Se há um iframe com sistema externo:
```python
# Já está configurado para detectar iframes automaticamente
# Mas você pode adicionar palavras-chave específicas:
if any(keyword in frame_url for keyword in ['agenda', 'schedule', 'nome-do-sistema']):
#                                                                 ^^^^^^^^^^^^^^^^
#                                                                 ADICIONE AQUI
```

---

## 🎯 Passo 5: Ajustar Extração de Data/Hora

Se o script encontra elementos mas não extrai data/hora corretamente:

Localize esta seção no código:

```python
data_elem = elem.query_selector('[class*="data"], [class*="date"]')
hora_elem = elem.query_selector('[class*="hora"], [class*="time"]')
```

**AJUSTE** conforme a estrutura real.

### Exemplos

**Exemplo 1** - Data em `<span class="day">` e hora em `<span class="hour">`:
```python
data_elem = elem.query_selector('span.day')     # ← AJUSTE AQUI
hora_elem = elem.query_selector('span.hour')    # ← AJUSTE AQUI
```

**Exemplo 2** - Tudo em um único elemento:
Mantenha o código de regex que já extrai automaticamente:
```python
import re
date_match = re.search(r'(\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?)', texto)
time_match = re.search(r'(\d{1,2}:\d{2})', texto)
```

---

## 📊 Passo 6: Testar Localmente (Opcional)

Para testar mais rápido antes de fazer commit:

```bash
# 1. Clone o repositório para sua máquina
# 2. Instale as dependências
pip install -r requirements.txt
playwright install chromium

# 3. Configure variáveis de ambiente
export EMAIL_SENDER="seu-email@gmail.com"
export EMAIL_PASSWORD="sua-senha-de-app"

# 4. Execute
python check_availability.py

# 5. Verifique os arquivos gerados
# - debug_screenshot.png
# - page_html.html
# - error_screenshot.png (se houver erro)
```

---

## 🔄 Passo 7: Commit e Teste

```bash
# 1. Salve suas alterações no código
# 2. Faça commit e push
git add check_availability.py
git commit -m "Ajuste de seletores para agendamento"
git push

# 3. Execute manualmente no GitHub Actions
# 4. Verifique os logs novamente
```

---

## 💡 Dicas e Truques

### 1. Ordem importa
Os seletores são testados na ordem. Coloque os mais específicos primeiro.

### 2. Use console.log no navegador
Abra a página no navegador, pressione `F12` → `Console`, e digite:
```javascript
document.querySelectorAll('seu-seletor-aqui')
```
Veja quantos elementos retornam.

### 3. Seletores CSS úteis

| Seletor | Descrição |
|---------|-----------|
| `div.classe` | div com classe exata |
| `div[class*="parte"]` | div com classe contendo "parte" |
| `div[data-id="123"]` | div com atributo específico |
| `div > span` | span filho direto de div |
| `div span` | span descendente de div |

### 4. Regex patterns úteis

| Pattern | Exemplo |
|---------|---------|
| `r'\d{1,2}/\d{1,2}/\d{4}'` | 15/02/2026 |
| `r'\d{1,2}:\d{2}'` | 14:30 |
| `r'\d{1,2}/\d{1,2}'` | 15/02 |

---

## ⚠️ Problemas Comuns

| Problema | Solução |
|----------|---------|
| "Timeout esperando elemento" | Aumente o tempo de espera ou verifique se o seletor está correto |
| "Elementos encontrados mas sem data/hora" | Ajuste os seletores de extração de data/hora |
| "Site carrega mas não mostra horários" | Pode ser necessário interação (clicar, rolar) |
| "Muitos horários duplicados" | Adicione lógica de deduplicação no código |

### Exemplo: Adicionar interação

```python
page.click('button.ver-horarios')  # Clicar em botão
page.wait_for_timeout(2000)        # Aguardar carregamento
```

---

## 📞 Estrutura Típica de Sites de Agendamento

A maioria dos sites de agendamento médico usa uma destas estruturas:

### Tipo 1 - Calendário com botões
```html
<div class="calendar">
  <button class="day-slot" data-date="15/02" data-time="14:30">
    14:30
  </button>
</div>
```

### Tipo 2 - Lista de horários
```html
<ul class="time-slots">
  <li class="slot">
    <span class="date">15/02</span>
    <span class="time">14:30</span>
  </li>
</ul>
```

### Tipo 3 - Cards de agendamento
```html
<div class="appointment-card">
  <div class="date">15 de Fevereiro</div>
  <div class="time">14:30</div>
  <button>Agendar</button>
</div>
```

### Tipo 4 - Iframe de sistema externo
```html
<iframe src="https://sistema-externo.com/agenda?medico=123">
  <!-- Conteúdo dentro do iframe -->
</iframe>
```

---

## 🎓 Recursos Adicionais

- [CSS Selectors Reference](https://www.w3schools.com/cssref/css_selectors.php)
- [Playwright Documentation](https://playwright.dev/python/docs/selectors)
- [Regex Tester](https://regex101.com/)

---

**Boa sorte!** Com paciência e estas instruções, você conseguirá ajustar o script. 🍀
