# Contributing to Monitor Consulta Rede D'Or

Obrigado por considerar contribuir para este projeto! 🎉

## 🚀 Como Contribuir

### Reportar Bugs

Se você encontrou um bug, por favor abra uma issue com:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots (se aplicável)
- Logs relevantes do GitHub Actions

### Sugerir Melhorias

Sugestões são bem-vindas! Abra uma issue com:
- Descrição da melhoria
- Justificativa (por que é útil)
- Exemplos de uso (se aplicável)

### Pull Requests

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 🛠️ Configuração do Ambiente de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/monitor-consulta-rededor.git
cd monitor-consulta-rededor

# Instale dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Instale Playwright browsers
playwright install chromium

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais
```

## 🧪 Executar Testes

```bash
# Executar testes
pytest

# Com coverage
pytest --cov=. --cov-report=html

# Ver relatório de coverage
open htmlcov/index.html
```

## 🎨 Code Style

Este projeto usa:

- **black** para formatação de código
- **ruff** para linting
- **mypy** para type checking

```bash
# Formatar código
black check_availability.py

# Lint
ruff check check_availability.py

# Type check
mypy check_availability.py
```

### Pre-commit Hooks (Recomendado)

```bash
# Instalar pre-commit hooks
pre-commit install

# Rodar manualmente
pre-commit run --all-files
```

## 📝 Padrões de Código

- Use type hints sempre que possível
- Docstrings em formato Google Style para funções/classes
- Nomes de variáveis em português (já que o projeto é em PT-BR)
- Nomes de funções/classes em PascalCase ou snake_case conforme PEP 8
- Máximo de 100 caracteres por linha

### Exemplo de Docstring

```python
def minha_funcao(param1: str, param2: int) -> bool:
    """
    Breve descrição da função.

    Args:
        param1: Descrição do parâmetro 1
        param2: Descrição do parâmetro 2

    Returns:
        Descrição do retorno

    Raises:
        ValueError: Quando param2 é negativo
    """
    pass
```

## 🔍 Áreas que Precisam de Contribuição

- [ ] Testes unitários adicionais
- [ ] Suporte para outros sites de agendamento médico
- [ ] Melhorias nos seletores CSS (mais robustos)
- [ ] Suporte para múltiplos médicos/especialidades
- [ ] Dashboard web para visualizar histórico
- [ ] Notificações via Telegram/WhatsApp

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença MIT do projeto.

## ❓ Dúvidas?

Se tiver dúvidas, abra uma issue ou entre em contato!

---

**Obrigado pela sua contribuição!** 🙏
