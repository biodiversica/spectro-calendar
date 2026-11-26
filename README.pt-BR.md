# |=|=| spectro-calendar

*[English](README.md) · Português (Brasil)*

O spectro-calendar gera um calendário HTML navegável de espectrogramas a partir
de uma pasta de gravações `.wav` feitas por um
[AudioMoth](https://www.openacousticdevices.info/audiomoth) ou por qualquer
outro gravador acústico passivo que registre a data e a hora no nome de cada
arquivo.

Cada gravação é representada por uma miniatura de espectrograma posicionada em
uma tabela, com as datas nas colunas e os horários do dia nas linhas, de modo
que semanas de dados de monitoramento acústico podem ser examinadas de uma só
vez. Opcionalmente, cada célula inclui um player de áudio da gravação, um
controle de velocidade de reprodução para ouvir ultrassom e uma caixa de
seleção para marcar gravações e exportar a seleção como uma lista. Com
`--save-fullsize`, um espectrograma em resolução completa também é gravado ao
lado de cada miniatura, para uma inspeção mais detalhada.

A ferramenta é uma adaptação estendida dos
[scripts criados por Nathan Wolek](https://github.com/nwolek/audiomoth-scripts).

## Instalação

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

O instalador lista o que vai fazer e pede confirmação antes de alterar
qualquer coisa.

**Desinstalação.** Execute o instalador novamente com
`SPECTRO_CALENDAR_UNINSTALL=1`. No Windows, execute no PowerShell:

```powershell
$env:SPECTRO_CALENDAR_UNINSTALL=1; irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | Out-String | iex
```

No macOS e no Linux:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | SPECTRO_CALENDAR_UNINSTALL=1 sh
```

Calendários e espectrogramas nunca são removidos.

**Com uv ou pip.** O spectro-calendar é publicado no PyPI e requer Python 3.10
ou posterior:

```bash
uv tool install spectro-calendar   # como ferramenta de linha de comando isolada
pip install spectro-calendar       # ou com pip, no ambiente atual
```

[Instalação](docs/pt-BR/installation.md) descreve o que o instalador faz, as
suas variáveis de ambiente, o backend opcional ffmpeg e a instalação a partir
do código-fonte.

## Primeiros Passos

```bash
spectro-calendar /dados/sitio-1                          # calendário gravado ao lado das gravações
spectro-calendar /dados/sitio-1 --output-dir calendario  # ou numa pasta própria
spectro-calendar /dados/sitio-1 --include-audio --speed-control --annotate
spectro-calendar --config example_config.yaml            # todas as opções a partir de um arquivo YAML
```

Abra no navegador o `index_.html` gravado pela execução. Os nomes de arquivo
são lidos como `AAAAMMDD_HHMMSS.WAV`, a convenção do AudioMoth, a menos que
`--datetime-format` e `--filename-prefix` indiquem outra.
`spectro-calendar --help` lista todas as opções.

## Documentação

| Página | Conteúdo |
|---|---|
| [Instalação](docs/pt-BR/installation.md) | O instalador, a desinstalação, uv e pip, ffmpeg, a partir do código-fonte |
| [Geração de um Calendário](docs/pt-BR/usage.md) | Os arquivos gravados por uma execução, um diretório de saída separado, subpastas, o painel de configurações |
| [Arquivo de Configuração](docs/pt-BR/configuration.md) | Definição das opções em YAML, precedência da linha de comando |
| [Opções da Linha de Comando](docs/pt-BR/cli.md) | Um exemplo e todas as opções |
| [Formatos de Nome de Arquivo](docs/pt-BR/filename-formats.md) | `--datetime-format` e `--filename-prefix` para outros gravadores |
| [Ouvindo Ultrassom](docs/pt-BR/ultrasound.md) | O seletor de velocidade de reprodução e a expansão temporal |
| [Modo de Anotação](docs/pt-BR/annotation.md) | Seleção de gravações, intervalos com Shift+clique, exportação da lista |
| [Backends](docs/pt-BR/backends.md) | Comparação entre ffmpeg e scipy |
| [Funcionamento](docs/pt-BR/how-it-works.md) | O processamento, etapa por etapa |
| [Desenvolvimento](docs/pt-BR/development.md) | Trabalho no próprio spectro-calendar, testes e integração contínua, estrutura do projeto |

## Licença

MIT; veja [LICENSE](LICENSE).
