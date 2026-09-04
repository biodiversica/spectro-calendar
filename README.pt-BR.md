# spectro-calendar

*[English version](README.md)*

Gera um "calendário" HTML navegável de espectrogramas a partir de uma pasta de
gravações `.wav`, por exemplo de um [AudioMoth](https://www.openacousticdevices.info/audiomoth)
ou de qualquer outro gravador acústico passivo que inclua uma marcação de
data/hora no nome de cada arquivo.

Cada gravação vira uma miniatura de espectrograma posicionada em uma tabela,
com datas nas colunas e horários do dia nas linhas, de modo que é possível
percorrer semanas de dados de monitoramento bioacústico rapidamente (e,
opcionalmente, reproduzir o áudio de qualquer célula). Uma versão em resolução
completa de cada espectrograma é gravada ao lado da sua miniatura, para ser
aberta diretamente do diretório de saída quando alguma célula precisar de um
olhar mais atento.

Isto pode ser considerado uma adaptação estendida dos [scripts criados por Nathan Wolek](https://github.com/nwolek/audiomoth-scripts).

## Requisitos

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) (recomendado) ou `pip` puro, para gerenciar dependências
- Opcionalmente, [`ffmpeg`](https://ffmpeg.org/) no seu `PATH` para o backend
  rápido de espectrogramas (veja [Backends](#backends) abaixo)
- Opcionalmente, [`sshfs`](https://github.com/libfuse/sshfs), caso as gravações
  estejam em uma máquina remota (veja [Gravações remotas via SSH](#gravações-remotas-via-ssh) abaixo)

## Instalação

### Como ferramenta autônoma

Se você quer apenas *executar* o spectro-calendar, o `uv` pode instalá-lo
diretamente do GitHub como uma ferramenta autônoma — com seu próprio ambiente
virtual isolado, o comando `spectro-calendar` no seu `PATH` e nenhum clone
para manter:

```bash
uv tool install git+https://github.com/biodiversica/spectro-calendar.git
```

O comando passa a funcionar a partir de qualquer diretório, sem o prefixo
`uv run` e sem nada para ativar:

```bash
spectro-calendar /caminho/para/gravacoes --use-ffmpeg --include-audio
```

Se o seu shell não encontrá-lo depois disso, rode `uv tool update-shell` uma
vez para adicionar o diretório de ferramentas do uv ao seu `PATH` e abra um
novo shell. Para atualizar para o commit mais recente, ou para remover:

```bash
uv tool upgrade spectro-calendar
uv tool uninstall spectro-calendar
```

Para experimentar sem instalar nada permanentemente, o `uvx` executa a
ferramenta em um ambiente temporário, descartado em seguida:

```bash
uvx --from git+https://github.com/biodiversica/spectro-calendar.git \
  spectro-calendar /caminho/para/gravacoes
```

O `--from` é necessário porque o projeto não está publicado no PyPI, então é
preciso dizer ao uv de onde buscá-lo. Se você já clonou o repositório, `uv
tool install .` de dentro dele instala essa cópia de trabalho da mesma forma
(acrescente `-e` para mantê-la editável).

Nos dois casos isso instala apenas as dependências Python. O backend opcional
[`ffmpeg`](https://ffmpeg.org/) é um binário de sistema — instale-o pelo
gerenciador de pacotes da sua distribuição se quiser usar `--use-ffmpeg`.

### A partir de um clone

Para modificar o código, ou para trabalhar a partir de um checkout, primeiro
clone o repositório:

```bash
git clone https://github.com/biodiversica/spectro-calendar.git
cd spectro-calendar
```

Depois escolha um dos métodos de instalação — ambos instalam as mesmas dependências de
execução (`numpy`, `scipy`, `matplotlib`, `pillow`, `pyyaml`):

**Com `uv`** (cria o `.venv` e instala a partir de `pyproject.toml` /
`uv.lock`):

```bash
uv sync
```

**Com `pip`** (em um ambiente virtual de sua preferência):

```bash
python -m venv .venv
source .venv/bin/activate  # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

O `requirements.txt` é mantido em sincronia com as dependências declaradas no
`pyproject.toml`, para quem preferir não instalar o `uv`. A instalação editável
(`pip install -e .`) exige `pip>=21.3`; se ela reclamar de `setup.py`, rode
`pip install --upgrade pip` antes.

## Uso

Rode como CLI através do `uv run`, como script de console instalado ou como
módulo Python — todos são pontos de entrada equivalentes para o mesmo código,
independentemente de como você instalou:

```bash
# se instalado com `uv tool install` (veja acima) -- sem prefixo algum
spectro-calendar /caminho/para/gravacoes

# via uv, de dentro de um clone (sem um passo separado de "activate")
uv run spectro-calendar /caminho/para/gravacoes

# como módulo python (funciona tanto com uv quanto com um venv instalado via pip)
uv run python -m spectro_calendar /caminho/para/gravacoes
python -m spectro_calendar /caminho/para/gravacoes  # com o venv do pip ativado

# o script de console também está no PATH do venv nos dois casos
.venv/bin/spectro-calendar /caminho/para/gravacoes
```

`recording_dir` precisa conter arquivos `.wav` com data/hora embutidas no nome
do arquivo. Por padrão apenas o primeiro nível de `recording_dir` é varrido;
use `--recursive` se as gravações estiverem em subpastas (veja
[Subpastas](#subpastas) abaixo). Por padrão a ferramenta espera a convenção do AudioMoth,
`AAAAMMDD_HHMMSS.WAV` (ex.: `20260315_063000.WAV`), mas isso é totalmente
configurável via `--datetime-format` e `--filename-prefix` — veja
[Formatos de nome de arquivo](#formatos-de-nome-de-arquivo) abaixo para
gravadores que usam outra convenção (ex.: `SM4_AAAAMMDD_HHMMSS.wav` do
Wildlife Acoustics SM4).

Executar o comando produz o seguinte, dentro de `recording_dir` por padrão, ou
inteiramente dentro de `--output-dir` se informado (caso em que `recording_dir`
é apenas lido, nunca escrito):

- `<nome-original>-fullsize-<label>.png` — um espectrograma em resolução completa por arquivo WAV
- `<nome-original>-thumbnail-<label>.png` — a miniatura correspondente, reduzida
- `index_<label>.html` — a tabela do calendário que dispõe todas as miniaturas
- `spectrogram-table.css` — a folha de estilo usada pela tabela HTML

Abra `index_<label>.html` em um navegador para ver o calendário. Use
`--output-dir` para manter todos os arquivos gerados (imagens, HTML, CSS)
separados das gravações originais, por exemplo para publicar apenas essa pasta:

```bash
uv run spectro-calendar /dados/sitio-1/gravacoes --output-dir /dados/sitio-1/calendario
```

O HTML continua ligando o player `<audio>` opcional de cada miniatura ao WAV
original em `recording_dir` por um caminho relativo, então `--include-audio`
continua funcionando mesmo que as gravações em si não sejam copiadas para
`--output-dir`.

### Subpastas

Por padrão só são considerados os arquivos `.wav` que estão diretamente em
`recording_dir` — qualquer coisa dentro de uma subpasta é ignorada. Use
`--recursive` para descer também pelas subpastas:

```bash
uv run spectro-calendar /dados/sitio-1/gravacoes --recursive
```

Os PNGs de cada gravação são então escritos em um subdiretório do diretório de
saída que espelha a localização do WAV, ex.: uma gravação em
`gravacoes/moth-a/20260304_100000.WAV` gera suas imagens em
`calendario/moth-a/`. Isso evita que arquivos de mesmo nome em subpastas
diferentes (uma pasta por gravador ou por instalação, por exemplo)
sobrescrevam os espectrogramas uns dos outros. O calendário HTML e o CSS
continuam na raiz do diretório de saída e referenciam as imagens por caminho
relativo.

Uma ressalva: o calendário tem uma única célula por data e horário do dia,
então se duas gravações compartilham o mesmo horário — dois gravadores com a
mesma programação, em duas subpastas — apenas uma delas pode aparecer na
tabela. A execução imprime um aviso nomeando os dois arquivos sempre que isso
acontece, e ainda gera os espectrogramas de todos eles, então nada se perde em
disco. Para ver todas as gravações, rode a ferramenta uma vez por subpasta,
cada uma com seu próprio `--output-dir`.

### Arquivo de configuração

Em vez de usar flags de linha de comando, as opções podem ser
definidas em um arquivo YAML e passadas com `--config`:

```bash
uv run spectro-calendar --config example_config.yaml
```

Veja [`example_config.yaml`](example_config.yaml) para um exemplo completo.
Cada chave YAML corresponde a uma flag da CLI com os hífens trocados por
sublinhados (ex.: `--output-dir` → `output_dir`), incluindo o próprio
`recording_dir`, de modo que uma execução pode ser totalmente descrita por um
arquivo de configuração, sem nenhum argumento posicional.

**Qualquer flag passada explicitamente na linha de comando tem precedência
sobre o arquivo de configuração** — a configuração apenas fornece valores
padrão para as opções que você não especificar na linha de comando:

```bash
# usa todos os valores de example_config.yaml, exceto max_cores, que é
# sobrescrito para 2 independentemente do que o arquivo diga
uv run spectro-calendar --config example_config.yaml --max-cores 2
```

Uma chave desconhecida no arquivo de configuração é tratada como erro (com a
lista de chaves válidas), em vez de ser silenciosamente ignorada.

### Opções

| Flag | Padrão | Descrição |
|---|---|---|
| `recording_dir` | — | Diretório com as gravações `.wav` (posicional; obrigatório, a menos que definido via `recording_dir` no `--config`) |
| `--config CAMINHO` | nenhum | Arquivo YAML com valores padrão das opções (veja [Arquivo de configuração](#arquivo-de-configuração)); flags explícitas da CLI sempre têm precedência |
| `--use-ffmpeg` | desligado | Usa o backend ffmpeg em vez do scipy (volta ao scipy se o ffmpeg não estiver instalado) |
| `--max-cores N` | `4` | Número de arquivos processados em paralelo (`1` desativa o paralelismo) |
| `--gain N` | `1` | Ganho em dB aplicado ao espectrograma (apenas backend ffmpeg) |
| `--gain-scale` | `log` | Escala do ganho no ffmpeg (`log`, `sqrt`, `lin`, ...) |
| `--highest-freq N` | `20000` | Limite superior do eixo de frequência, em Hz |
| `--lowest-freq N` | `0` | Limite inferior do eixo de frequência, em Hz |
| `--freq-scale` | `lin` | Escala do eixo de frequência, `lin` ou `log` (apenas backend ffmpeg) |
| `--color-choice` | `plasma` | Paleta de cores (backend ffmpeg; o backend scipy é fixo em `plasma`) |
| `--spec-label` | `""` | Sufixo usado para distinguir os nomes dos arquivos de saída, ex.: gerar as bandas `lf`/`hf` no mesmo diretório sem colisões |
| `--img-size LxA` | `1080x720` | Dimensões do espectrograma em tamanho real, em pixels |
| `--thumbnail-scale L:A` | `108:72` | Dimensões da miniatura, em pixels; define também o tamanho da célula `<img>` no HTML |
| `--clear` | desligado | Apaga os arquivos `*<label>.png` existentes no diretório de saída antes de gerar os novos |
| `--include-audio` | desligado | Insere um player `<audio>` sob cada miniatura, apontando para o WAV correspondente em `recording_dir`. Os players usam `preload="none"`, então uma gravação só é buscada quando você aperta play nela |
| `--dates D1 D2 ...` | todas as datas | Restringe o processamento a datas `AAAAMMDD` específicas (validadas contra as datas realmente presentes, usando a data lida da gravação, qualquer que seja o formato do nome do arquivo) |
| `--start-date AAAAMMDD` | data mais antiga disponível | Primeira data a incluir; seleciona um intervalo contíguo em vez de uma lista explícita. Não pode ser combinada com `--dates` |
| `--end-date AAAAMMDD` | data mais recente disponível | Última data a incluir (inclusive). Não pode ser combinada com `--dates` |
| `--time-step N` | nenhum | Mantém apenas uma gravação por intervalo de N minutos em cada dia, em vez de todas as gravações |
| `--start-time HHMMSS` | `000000` | Início da janela diária de horários a incluir |
| `--end-time HHMMSS` | `235900` | Fim da janela diária de horários a incluir |
| `--recursive` | desligado | Também varre as subpastas de `recording_dir` em busca de arquivos `.wav`. Os espectrogramas de cada arquivo são escritos em uma subpasta correspondente dentro do diretório de saída (veja [Subpastas](#subpastas)) |
| `--output-dir DIR` | `recording_dir` | Diretório para toda a saída gerada (PNGs dos espectrogramas, `index_<label>.html`, `spectrogram-table.css`); criado se não existir. Quando definido, `recording_dir` é apenas lido — nada é escrito lá. O player `<audio>` do HTML (`--include-audio`) continua apontando para o WAV original por um caminho relativo |
| `--datetime-format FMT` | `%Y%m%d_%H%M%S` | Formato compatível com strptime descrevendo como data/hora estão embutidas em cada nome de arquivo, após remover `--filename-prefix` |
| `--filename-prefix PREFIXO` | `""` | Prefixo literal a ser removido do nome do arquivo antes de aplicar `--datetime-format`, ex.: `SM4_` para `SM4_20260304_100000.wav` |

Exemplo — backend rápido do ffmpeg, apenas a banda de baixas frequências, uma
amostra a cada 30 minutos entre 5h e 9h, 6 processos em paralelo:

```bash
uv run spectro-calendar /dados/sitio-1 \
  --use-ffmpeg --max-cores 6 \
  --spec-label lf --highest-freq 2000 \
  --time-step 30 --start-time 050000 --end-time 090000
```

### Formatos de nome de arquivo

`--datetime-format` aceita qualquer string de formato do [strptime](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes);
`--filename-prefix` é removido do radical do nome do arquivo (a parte antes da
extensão) antes que esse formato seja aplicado.

| Gravador / convenção | Exemplo de nome | Flags |
|---|---|---|
| AudioMoth (padrão) | `20260304_100000.WAV` | nenhuma necessária |
| Wildlife Acoustics SM4 | `SM4_20260304_100000.wav` | `--filename-prefix SM4_` |
| Data primeiro, com hífens | `2026-03-04_10-00-00.wav` | `--datetime-format "%Y-%m-%d_%H-%M-%S"` |
| Gravador com etiqueta de sítio | `SITE1-20260304-100000.wav` | `--filename-prefix SITE1- --datetime-format "%Y%m%d-%H%M%S"` |

Se um nome de arquivo não começar com `--filename-prefix`, ou se o restante não
corresponder a `--datetime-format`, a ferramenta encerra com um erro nomeando o
arquivo problemático, em vez de ignorá-lo ou interpretá-lo incorretamente em
silêncio.

### Gravações remotas via SSH

Se as gravações estiverem em uma máquina remota, monte esse diretório
localmente com o [`sshfs`](https://github.com/libfuse/sshfs) e aponte
`recording_dir` para o ponto de montagem. Nada mais muda — a ferramenta apenas
lê de `recording_dir`, então uma montagem somente leitura é suficiente:

```bash
mkdir -p ~/mnt/sitio-1
sshfs usuario@host:/caminho/no/servidor ~/mnt/sitio-1 \
  -o ro,reconnect,cache=yes,kernel_cache \
  -o IdentityFile=$HOME/.ssh/sua_chave,IdentitiesOnly=yes

uv run spectro-calendar ~/mnt/sitio-1 \
  --output-dir ~/calendarios/sitio-1 \
  --use-ffmpeg --include-audio
```

**Acertando o caminho remoto.** O `sshfs` conversa com o *subsistema SFTP* do
servidor SSH, cuja visão do sistema de arquivos frequentemente não é a mesma de
um shell de login — NAS em particular costumam expor as pastas compartilhadas
na raiz do SFTP. Um caminho que funciona com `scp` pode, portanto, falhar com
`sshfs`, especialmente em clientes OpenSSH anteriores à versão 9.0, em que o
`scp` roda sobre o shell remoto em vez de SFTP. Pergunte direto ao SFTP em vez
de adivinhar:

```bash
sftp usuario@host
sftp> pwd     # onde o SFTP acha que você está
sftp> ls /    # o que realmente existe na raiz do SFTP
```

Em um Synology, por exemplo, o shell pode reportar `/volume1/homes/voce`
enquanto o SFTP coloca a pasta compartilhada em `/Recordings/sitio-1` — e é
este último que o `sshfs` precisa. Coloque todo o argumento `usuario@host:caminho`
entre aspas se o caminho remoto contiver espaços ou caracteres acentuados; a
montagem os esconde do HTML gerado, então o que aparece nos links de áudio são
os nomes locais do ponto de montagem.

Gerar os espectrogramas puxa cada WAV selecionado pela rede uma vez — essa é a
parte lenta, e não há como evitá-la, já que cada arquivo precisa ser lido por
inteiro para calcular seu espectrograma. Os filtros de data/hora (`--dates` ou
`--start-date`/`--end-date`, `--start-time`/`--end-time`, `--time-step`) são a
alavanca para reduzir essa transferência. Tudo que é escrito — PNGs, HTML, CSS
— fica localmente em `--output-dir`.

**Reproduzir o áudio não exige baixá-lo.** Com `--include-audio`, o elemento
`<audio>` de cada célula transmite direto através da montagem e usa
`preload="none"`, de modo que o navegador busca apenas a gravação em que você
efetivamente apertar play, e apenas até onde você ouvir — abrir o calendário em
si não custa transferência nenhuma. Nada é copiado para o disco local além do
cache de páginas do sistema operacional. Note que WAV não é comprimido (um
minuto de AudioMoth a 48 kHz tem cerca de 23 MB), então a reprodução é
confortável em LAN ou VPN e pode travar em uma conexão lenta.

Dois pontos de atenção:

- Abra o `index_<label>.html` direto do disco (`file://`). O caminho relativo
  de `--output-dir` de volta para a montagem aponta para fora do diretório de
  saída (ex.: `../../mnt/sitio-1/20260304_100000.WAV`), então servir o
  `--output-dir` com algo como `python -m http.server` não vai conseguir
  resolver o áudio, mesmo que as miniaturas continuem carregando — esse
  servidor se recusa a servir caminhos acima da sua raiz.
- Se a conexão cair, `-o reconnect` restaura a montagem, mas qualquer leitura
  em andamento falha antes; rode o comando novamente para preencher os
  espectrogramas que faltaram. Desmonte com `fusermount -u ~/mnt/sitio-1`.

## Como funciona

Toda a pipeline está em `src/spectro_calendar/cli.py`. Executar o comando roda
estas etapas, nesta ordem:

1. **Interpretação dos argumentos** — o `argparse` monta a interface de CLI
   documentada na tabela acima e valida/normaliza os tipos informados pelo
   usuário (ex.: `Path` para o diretório de gravações, `int` para as
   frequências). Antes da interpretação real, uma primeira passagem rápida
   extrai o `--config` (se informado), e `load_yaml_config` lê esse arquivo
   YAML (rejeitando chaves desconhecidas) e instala seus valores como os novos
   padrões do parser, via `parser.set_defaults(**config)`. Como o argparse só
   recorre a um padrão quando a flag não está presente na linha de comando,
   qualquer flag que o usuário *de fato* passe em argv vence tanto o arquivo de
   configuração quanto o padrão embutido. `recording_dir` é obrigatório neste
   ponto (seja como argumento posicional, seja pela chave `recording_dir` da
   configuração).

2. **Limpeza opcional** — se `--clear` for passado, os arquivos
   `*<spec-label>.png` existentes no diretório de saída (`--output-dir`, se
   informado, senão `recording_dir`) são apagados antes, para que
   espectrogramas antigos de uma execução com outros parâmetros não fiquem
   pendurados.

3. **Descoberta dos arquivos** — todo arquivo `.wav` (sem distinção de
   maiúsculas/minúsculas) diretamente dentro de `recording_dir` é listado; com
   `--recursive`, as subpastas também são percorridas.
   `parse_recording_datetime` remove `--filename-prefix` do radical de cada
   nome e interpreta o restante com `datetime.strptime(stem, --datetime-format)`,
   construindo um mapeamento `{caminho_wav: datetime}`; qualquer nome que não
   corresponda encerra o programa com um erro identificando-o. Os arquivos são
   então ordenados cronologicamente por essa data/hora interpretada (não pelo
   nome), e `get_available_dates` / `get_available_times` derivam dali os
   valores distintos de `AAAAMMDD`/`HHMMSS` para uso nas etapas seguintes —
   desacoplando toda a lógica posterior de data/hora da convenção original de
   nomes.

4. **Filtragem por data** — se `--dates` foi informado, esses valores são
   conferidos contra as datas realmente presentes (`validate_dates` levanta
   erro se alguma data pedida não tiver gravações). Se em vez disso foram
   informados `--start-date`/`--end-date`, `filter_dates_by_range` mantém as
   datas descobertas dentro desse intervalo inclusivo — os próprios limites não
   precisam ter gravações, e qualquer um deles pode ser omitido para deixar
   aquela ponta aberta, mas a execução é abortada se o intervalo não selecionar
   nada. As duas formas são mutuamente exclusivas; sem nenhuma delas, todas as
   datas descobertas são usadas.

5. **Filtragem por horário do dia** — `filter_wav_files_by_time_window` mantém
   apenas os arquivos cujo horário cai dentro de `[--start-time, --end-time]`
   em cada data selecionada (essa janela é sempre aplicada, usando os padrões
   permissivos de 00:00:00–23:59:00 quando não personalizada).

6. **Subamostragem temporal** — se `--time-step` estiver definido,
   `filter_wav_files_by_time_step` percorre os arquivos restantes de cada dia em
   ordem cronológica e mantém apenas o primeiro arquivo em/depois do horário do
   último arquivo mantido mais `N` minutos — transformando, por exemplo, uma
   gravação por minuto em uma a cada 30 minutos, sem exigir que as gravações
   caiam em marcos exatos do relógio.

7. **Geração dos espectrogramas** — cada arquivo restante é entregue a um de
   dois backends intercambiáveis (`--use-ffmpeg` seleciona o do ffmpeg, desde
   que o binário `ffmpeg` seja encontrado via `shutil.which`; caso contrário o
   scipy é usado, independentemente da flag). Ambos os backends escrevem seus
   PNGs no diretório de saída (`--output-dir`, se informado, senão
   `recording_dir`) — o diretório de origem dos WAVs nunca é escrito quando
   `--output-dir` está definido:
   - **`spectrogram_ffmpeg`** chama `subprocess.run` duas vezes: uma para o
     filtro `showspectrumpic` do ffmpeg, que renderiza o PNG em tamanho real
     diretamente do WAV, e outra para reduzir esse PNG à miniatura. Ele pula
     arquivos cujas imagens em tamanho real e miniatura já existam.
   - **`spectrogram_scipy`** lê o WAV com `scipy.io.wavfile`, converte estéreo
     em mono, calcula uma transformada de Fourier de tempo curto
     (`scipy.signal.stft`, `nperseg=2048`), aplica uma máscara para
     `[--lowest-freq, --highest-freq]` e renderiza o espectrograma de magnitude
     logarítmica com `matplotlib` (colormap `plasma`, eixos ocultos). O PNG
     salvo é então reaberto e redimensionado com o `Pillow` para produzir a
     miniatura.

   Quando `--max-cores` é maior que 1, os arquivos são distribuídos em um pool
   `concurrent.futures.ProcessPoolExecutor` desse tamanho, em vez de serem
   processados um a um; o backend ffmpeg paraleliza bem porque cada worker fica
   limitado por E/S, esperando um subprocesso, enquanto o backend scipy se
   beneficia de paralelismo real de CPU entre processos. Veja a tabela de
   benchmark no docstring do módulo `cli.py` para a vazão medida dos dois
   backends com 1/2/4/6 núcleos.

8. **Geração do calendário HTML** — `generate_html` monta uma busca
   `{(data, hora): caminho_wav}` a partir do mapeamento `file_dates` dos
   arquivos *processados* e então escreve `index_<spec-label>.html`: uma tabela
   HTML com cabeçalho e primeira coluna fixos, uma coluna por data e uma linha
   por horário do dia. Cada célula ou mostra a miniatura correspondente (nomeada
   segundo o radical real daquele arquivo, qualquer que seja sua convenção de
   nome), com um player `<audio>` adicionado quando `--include-audio` está
   ativo, ou fica em branco se não houver gravação para aquela combinação de
   data/hora. Esses players são emitidos com `preload="none"`: sem isso, o
   navegador lê o cabeçalho de cada WAV ao carregar a página só para exibir a
   duração, o que em um calendário grande (um mês com espaçamento de 15 minutos
   dá cerca de 3000 células) trava a página muito antes de você clicar em
   qualquer coisa — de forma severa quando as gravações estão em uma montagem de
   rede. O `src` da miniatura é um nome de arquivo relativo simples dentro do
   diretório de saída; o `src` do `<audio>` é calculado com `os.path.relpath`
   do diretório de saída de volta para `recording_dir`, de modo que os dois
   diretórios não precisam estar aninhados um no outro.

9. **Style sheet** — o CSS embutido em `SPECTROGRAM_TABLE_CSS` é escrito
   como `spectrogram-table.css` ao lado do arquivo HTML, no mesmo destino
   `--output-dir`/`recording_dir` (cabeçalhos fixos, contêiner de rolagem,
   destaque alternado de semanas/horas), para que o `index_<label>.html` gerado
   renderize corretamente quando aberto diretamente do disco.

10. **Cronometragem** — o tempo total de execução é medido com `time.time()` e
    exibido ao final, seguindo a mesma metodologia usada para produzir a tabela
    de benchmark ffmpeg-vs-scipy no docstring do módulo.

## Backends

| | ffmpeg | scipy |
|---|---|---|
| Velocidade | Mais rápido (veja o benchmark em `cli.py`) | Mais lento, Python puro |
| Dependência | Exige o binário `ffmpeg` no `PATH` | Apenas pacotes Python (`scipy`, `matplotlib`, `pillow`) |
| Paleta de cores | Configurável via `--color-choice` | Fixa em `plasma` |
| Escala de frequência | Configurável via `--freq-scale` (`lin`/`log`) | Apenas linear |

Se `--use-ffmpeg` for passado mas o ffmpeg não for encontrado, a ferramenta
volta automaticamente ao backend scipy.

## Desenvolvimento

```bash
uv sync --group dev
uv run ruff check .
```

Estrutura do projeto:

```
src/spectro_calendar/
├── __init__.py   # versão do pacote
├── __main__.py   # habilita `python -m spectro_calendar`
└── cli.py        # interpretação dos argumentos + pipeline completo de processamento
```

## Licença

MIT — veja [LICENSE](LICENSE).
