# Instalação

*[English](../en/installation.md) · Português (Brasil)*

**Sem Python.** O instalador configura tudo o que é necessário e adiciona o
comando `spectro-calendar`. Executá-lo novamente atualiza a instalação.

No Windows, abra o PowerShell e execute:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | Out-String | iex"
```

No macOS e no Linux, abra um terminal e execute:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | sh
```

O instalador primeiro lista o que vai fazer e pede confirmação antes de
alterar qualquer coisa. Em seguida, executa as seguintes etapas:

1. Instala o [uv](https://docs.astral.sh/uv/) em `~/.local/bin`, caso ainda
   não esteja presente. O uv baixa o próprio Python, de modo que nenhuma
   instalação prévia é necessária, e qualquer instalação de Python existente
   permanece inalterada.
2. Executa `uv tool install --python 3.12 spectro-calendar`, que instala a
   ferramenta em um ambiente isolado e adiciona `spectro-calendar` ao PATH.

O comando fica disponível nos terminais abertos após a instalação. A variável
de ambiente `SPECTRO_CALENDAR_PACKAGE` altera o que o instalador instala (por
exemplo, uma versão específica, como `spectro-calendar==0.1.0`), e
`SPECTRO_CALENDAR_YES=1` dispensa a confirmação, para instalar ou desinstalar
a partir de um script.

**Desinstalação.** Execute o instalador novamente com
`SPECTRO_CALENDAR_UNINSTALL=1`. Ele lista o que vai remover e pede confirmação
antes. No Windows, execute no PowerShell:

```powershell
$env:SPECTRO_CALENDAR_UNINSTALL=1; irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | Out-String | iex
```

No macOS e no Linux:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | SPECTRO_CALENDAR_UNINSTALL=1 sh
```

Isso remove o spectro-calendar. Os calendários e espectrogramas que ele gerou
nunca são removidos, nem o uv, que outros programas podem usar. Executar
`uv tool uninstall spectro-calendar` diretamente tem o mesmo efeito.

**Com uv ou pip.** O spectro-calendar é publicado no PyPI e requer Python 3.10
ou posterior:

```bash
uv tool install spectro-calendar   # como ferramenta de linha de comando isolada
pip install spectro-calendar       # ou com pip, no ambiente atual
```

`uv tool upgrade spectro-calendar` atualiza a ferramenta. Ela também pode ser
executada uma única vez, sem instalação permanente, com
`uvx spectro-calendar /caminho/para/gravacoes`.

**Programa de sistema opcional.** O [ffmpeg](https://ffmpeg.org/), que não é
instalado pelos métodos acima, habilita o backend de espectrogramas mais
rápido (`--use-ffmpeg`; veja [Backends](backends.md)). Ele está disponível nos
gerenciadores de pacotes usuais, por exemplo `brew install ffmpeg`,
`sudo apt install ffmpeg` ou `winget install --id Gyan.FFmpeg`.

**A partir do código-fonte.** Para modificar o código, clone o repositório e
instale-o com o uv, que cria `.venv` a partir de `pyproject.toml` e `uv.lock`:

```bash
git clone https://github.com/biodiversica/spectro-calendar.git
cd spectro-calendar
uv sync
uv run spectro-calendar /caminho/para/gravacoes
```

Alternativamente, com pip em um ambiente virtual (uma instalação editável
requer `pip>=21.3`):

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

`requirements.txt` lista as mesmas dependências de execução que
`pyproject.toml`. A partir de um checkout do código-fonte, os comandos desta
documentação são prefixados com `uv run`, ou executados como
`python -m spectro_calendar` em um ambiente ativado. Veja
[Desenvolvimento](development.md) para os testes e a estrutura do projeto.
