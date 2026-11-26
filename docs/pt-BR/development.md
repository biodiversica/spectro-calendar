# Desenvolvimento

*[English](../en/development.md) · Português (Brasil)*

```bash
git clone https://github.com/biodiversica/spectro-calendar.git
cd spectro-calendar
uv sync               # instala o projeto e as ferramentas de desenvolvimento
uv run ruff check .   # verificação de estilo
uv run pytest         # testes
uv run spectro-calendar /caminho/para/gravacoes
```

## Testes e Integração Contínua

Os testes geram gravações sintéticas curtas, executam a ferramenta completa
sobre elas e inspecionam os arquivos gerados. O teste do backend ffmpeg é
ignorado quando o ffmpeg não está instalado. A integração contínua executa a
verificação de estilo e os testes no Linux, no macOS e no Windows, e executa
também os instaladores nos três sistemas com o pacote gerado.

## Estrutura do Projeto

```
src/spectro_calendar/
├── __init__.py   # versão do pacote
├── __main__.py   # permite `python -m spectro_calendar`
├── cli.py        # leitura dos argumentos e todo o processamento
└── richhelp.py   # saída formatada de --help
tests/            # testes de ponta a ponta
scripts/          # instaladores anexados a cada versão
docs/             # esta documentação, em inglês e em português
```

[Funcionamento](how-it-works.md) percorre o `cli.py` etapa por etapa.

## Documentação

A documentação fica em [`docs/`](../README.md), uma página por tópico em inglês
e em português, com o mesmo nome de arquivo. Uma alteração em um idioma deve
ser feita também no outro, no mesmo commit.
