# spectro-calendar

*[English version](README.md)*

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
powershell -ExecutionPolicy ByPass -c "irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | iex"
```

No macOS e no Linux, abra um terminal e execute:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | sh
```

O instalador executa as seguintes etapas:

1. Instala o [uv](https://docs.astral.sh/uv/) em `~/.local/bin`, caso ainda
   não esteja presente. O uv baixa o próprio Python, de modo que nenhuma
   instalação prévia é necessária, e qualquer instalação de Python existente
   permanece inalterada.
2. Executa `uv tool install --python 3.12 spectro-calendar`, que instala a
   ferramenta em um ambiente isolado e adiciona `spectro-calendar` ao PATH.

O comando fica disponível nos terminais abertos após a instalação. A variável
de ambiente `SPECTRO_CALENDAR_PACKAGE` altera o que o instalador instala (por
exemplo, uma versão específica, como `spectro-calendar==0.1.0`). Para
desinstalar, execute `uv tool uninstall spectro-calendar`.

**Com uv ou pip.** O spectro-calendar é publicado no PyPI e requer Python 3.10
ou posterior:

```bash
uv tool install spectro-calendar   # como ferramenta de linha de comando isolada
pip install spectro-calendar       # ou com pip, no ambiente atual
```

`uv tool upgrade spectro-calendar` atualiza a ferramenta. Ela também pode ser
executada uma única vez, sem instalação permanente, com
`uvx spectro-calendar /caminho/para/gravacoes`.

**Programas de sistema opcionais.** Dois programas externos ampliam a
ferramenta. Nenhum deles é instalado pelos métodos acima:

- O [ffmpeg](https://ffmpeg.org/) habilita o backend de espectrogramas mais
  rápido (`--use-ffmpeg`; veja [Backends](#backends)). Ele está disponível nos
  gerenciadores de pacotes usuais, por exemplo `brew install ffmpeg`,
  `sudo apt install ffmpeg` ou `winget install --id Gyan.FFmpeg`.
- O [sshfs](https://github.com/libfuse/sshfs) permite processar gravações
  armazenadas em uma máquina remota (veja
  [Gravações Remotas via SSH](#gravações-remotas-via-ssh)).

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
`pyproject.toml`. A partir de um checkout do código-fonte, os comandos deste
documento são prefixados com `uv run`, ou executados como
`python -m spectro_calendar` em um ambiente ativado.

## Uso

```bash
spectro-calendar /caminho/para/gravacoes
```

O diretório de gravações deve conter arquivos `.wav` cujos nomes incluam a data
e a hora da gravação. Por padrão, a ferramenta espera a convenção do AudioMoth,
`AAAAMMDD_HHMMSS.WAV` (por exemplo, `20260315_063000.WAV`); outras convenções
são configuradas com `--datetime-format` e `--filename-prefix` (veja
[Formatos de Nome de Arquivo](#formatos-de-nome-de-arquivo)). Somente o nível
superior do diretório é examinado, a menos que `--recursive` seja informado
(veja [Subpastas](#subpastas)).

Uma execução produz os seguintes arquivos, no diretório de gravações por
padrão ou no diretório indicado com `--output-dir`:

- `<nome>-thumbnail-<label>.png`: uma miniatura de espectrograma por gravação.
- `<nome>-fullsize-<label>.png`: o espectrograma em resolução completa,
  gravado somente com `--save-fullsize`.
- `index_<label>.html`: a página do calendário.
- `spectrogram-table.css`: a folha de estilos usada pela página do calendário.

`<label>` é o valor de `--spec-label`, vazio por padrão. O calendário é
visualizado abrindo `index_<label>.html` em um navegador.

Com `--output-dir`, todos os arquivos gerados são gravados em um diretório
separado, e o diretório de gravações é apenas lido, nunca modificado:

```bash
spectro-calendar /dados/sitio-1/gravacoes --output-dir /dados/sitio-1/calendario
```

Os players de áudio (`--include-audio`) referenciam as gravações originais por
um caminho relativo, de modo que continuam funcionando embora as gravações não
sejam copiadas para o diretório de saída. Quando não existe caminho relativo,
como no caso de gravações e saída em unidades diferentes no Windows, um
caminho absoluto é usado.

### Subpastas

Por padrão, somente os arquivos `.wav` localizados diretamente no diretório de
gravações são processados. Com `--recursive`, as subpastas também são
examinadas:

```bash
spectro-calendar /dados/sitio-1/gravacoes --recursive
```

As imagens de cada gravação são então gravadas em um subdiretório do diretório
de saída que reproduz a localização da gravação. Por exemplo, uma gravação em
`gravacoes/moth-a/20260304_100000.WAV` produz suas imagens em
`calendario/moth-a/`. Isso evita que gravações com nomes idênticos em
subpastas diferentes (tipicamente uma pasta por gravador ou campanha)
sobrescrevam os espectrogramas umas das outras. A página do calendário e a
folha de estilos permanecem no nível superior do diretório de saída.

O calendário tem uma única célula para cada combinação de data e horário. Quando
duas gravações têm o mesmo carimbo de data e hora, por exemplo dois gravadores
operando no mesmo agendamento, somente uma delas pode aparecer na tabela. Nesse
caso, a ferramenta exibe um aviso com o nome dos dois arquivos, e os
espectrogramas de todas as gravações são gerados mesmo assim. Para exibir todas
as gravações, a ferramenta pode ser executada uma vez por subpasta, cada vez
com o seu próprio `--output-dir`.

### Arquivo de Configuração

As opções também podem ser definidas em um arquivo YAML passado com `--config`:

```bash
spectro-calendar --config example_config.yaml
```

[`example_config.yaml`](example_config.yaml) contém um exemplo completo. Cada
chave corresponde a uma opção de linha de comando, com hífens substituídos por
sublinhados (por exemplo, `--output-dir` torna-se `output_dir`). O diretório de
gravações também pode ser definido, como `recording_dir`, de modo que uma
execução pode ser descrita inteiramente por um arquivo de configuração.

As opções informadas na linha de comando têm precedência sobre o arquivo de
configuração, que apenas fornece valores padrão:

```bash
# Usa todos os valores de example_config.yaml, exceto max_cores, que passa a
# ser 2 independentemente do valor no arquivo.
spectro-calendar --config example_config.yaml --max-cores 2
```

Uma chave não reconhecida no arquivo de configuração é informada como erro,
com a lista das chaves válidas.

### Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `recording_dir` | nenhum | Diretório que contém as gravações `.wav`. Posicional; obrigatório, a menos que seja definido como `recording_dir` no arquivo de configuração |
| `--config CAMINHO` | nenhum | Arquivo YAML com valores padrão das opções (veja [Arquivo de Configuração](#arquivo-de-configuração)) |
| `--version` | | Exibe a versão instalada e encerra |
| `--use-ffmpeg` | desligado | Usa o backend ffmpeg em vez do scipy. O backend scipy é usado quando o ffmpeg não está instalado |
| `--max-cores N` | `4` | Número de gravações processadas em paralelo (`1` desativa o processamento paralelo) |
| `--gain N` | `1` | Ganho em dB aplicado ao espectrograma (somente backend ffmpeg) |
| `--gain-scale` | `log` | Escala de intensidade do espectrograma do ffmpeg (`log`, `sqrt`, `lin` e outras aceitas pelo ffmpeg) |
| `--highest-freq N` | `20000` | Limite superior do eixo de frequência, em Hz |
| `--lowest-freq N` | `0` | Limite inferior do eixo de frequência, em Hz |
| `--freq-scale` | `lin` | Escala do eixo de frequência, `lin` ou `log` (somente backend ffmpeg) |
| `--color-choice` | `plasma` | Paleta de cores (somente backend ffmpeg; o backend scipy usa sempre `plasma`) |
| `--spec-label` | `""` | Sufixo acrescentado aos nomes dos arquivos de saída, para que várias bandas de frequência (por exemplo `lf` e `hf`) possam ser gravadas no mesmo diretório |
| `--img-size LxA` | `1080x720` | Dimensões do espectrograma em tamanho real, em pixels. A miniatura é reduzida a partir dessa imagem, de modo que esse valor também afeta o detalhe da miniatura |
| `--thumbnail-scale L:A` | `108:72` | Dimensões da miniatura, em pixels; também o tamanho da imagem no calendário |
| `--save-fullsize` | desligado | Grava também o espectrograma em tamanho real ao lado de cada miniatura. Desligado por padrão, pois o calendário usa somente as miniaturas e as imagens em tamanho real ocupam consideravelmente mais espaço em disco |
| `--clear` | desligado | Apaga os arquivos `*<label>.png` existentes no diretório de saída antes de gerar os novos |
| `--include-audio` | desligado | Adiciona um player de áudio sob cada miniatura, vinculado à gravação original. Os players usam `preload="none"`, de modo que uma gravação é carregada somente quando é reproduzida |
| `--speed-control` | desligado | Adiciona um seletor de velocidade de reprodução (de 1× a 1/16) acima do calendário. Reduzir a velocidade também abaixa o tom, o que torna o ultrassom audível (veja [Ouvindo Ultrassom](#ouvindo-ultrassom)). Requer `--include-audio` |
| `--annotate` | desligado | Modo de anotação: adiciona uma caixa de seleção sob cada miniatura e uma barra que exporta as gravações selecionadas como uma lista `.txt` (veja [Modo de Anotação](#modo-de-anotação)) |
| `--dates D1 D2 ...` | todas as datas | Processa somente as datas informadas, no formato `AAAAMMDD`. Cada data deve ter gravações |
| `--start-date AAAAMMDD` | data mais antiga | Primeira data de um intervalo contínuo. Não pode ser combinada com `--dates` |
| `--end-date AAAAMMDD` | data mais recente | Última data do intervalo (inclusive). Não pode ser combinada com `--dates` |
| `--time-step N` | nenhum | Mantém no máximo uma gravação por intervalo de N minutos em cada dia |
| `--start-time HHMMSS` | `000000` | Início da janela diária de horários |
| `--end-time HHMMSS` | `235900` | Fim da janela diária de horários |
| `--recursive` | desligado | Examina também as subpastas do diretório de gravações (veja [Subpastas](#subpastas)) |
| `--output-dir DIR` | diretório de gravações | Diretório para todos os arquivos gerados; criado se não existir. Quando definido, o diretório de gravações é apenas lido |
| `--datetime-format FMT` | `%Y%m%d_%H%M%S` | Formato `strptime` que descreve como a data e a hora aparecem em cada nome de arquivo, após a remoção do prefixo |
| `--filename-prefix PREFIXO` | `""` | Texto fixo que precede a data e a hora em cada nome de arquivo, por exemplo `SM4_` para `SM4_20260304_100000.wav` |

O exemplo a seguir usa o backend ffmpeg com seis processos paralelos, exibe
somente frequências até 2 kHz e mantém uma gravação a cada 30 minutos entre
05:00 e 09:00:

```bash
spectro-calendar /dados/sitio-1 \
  --use-ffmpeg --max-cores 6 \
  --spec-label lf --highest-freq 2000 \
  --time-step 30 --start-time 050000 --end-time 090000
```

### Formatos de Nome de Arquivo

`--datetime-format` aceita qualquer
[formato strptime](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).
`--filename-prefix` é removido do radical do nome do arquivo (o nome sem a
extensão) antes da aplicação do formato.

| Gravador ou convenção | Exemplo de nome de arquivo | Opções |
|---|---|---|
| AudioMoth (padrão) | `20260304_100000.WAV` | nenhuma |
| Wildlife Acoustics SM4 | `SM4_20260304_100000.wav` | `--filename-prefix SM4_` |
| Data primeiro, com hífens | `2026-03-04_10-00-00.wav` | `--datetime-format "%Y-%m-%d_%H-%M-%S"` |
| Identificador de sítio | `SITE1-20260304-100000.wav` | `--filename-prefix SITE1- --datetime-format "%Y%m%d-%H%M%S"` |

Quando um prefixo é definido, os arquivos `.wav` que não começam com ele são
ignorados e a sua quantidade é informada, de modo que gravações de outros
dispositivos podem permanecer no mesmo diretório. Um arquivo que começa com o
prefixo mas não corresponde a `--datetime-format` interrompe a execução com um
erro que identifica o arquivo, em vez de ser ignorado ou interpretado
incorretamente.

### Ouvindo Ultrassom

`--speed-control` adiciona um seletor **Playback speed** acima do calendário,
com os valores 1×, 1/2, 1/4, 1/8, 1/10 e 1/16, que se aplica a todos os
players de áudio:

```bash
spectro-calendar /dados/sitio-1 --include-audio --speed-control
```

A velocidade é alterada da mesma forma que no efeito "Change Speed" do
Audacity, e não como uma mudança de andamento que preserva o tom: o tom é
dividido pelo mesmo fator que a velocidade. Essa técnica, conhecida como
expansão temporal, é a forma usual de ouvir ultrassom. Um chamado de morcego
de 40 kHz reproduzido a 1/10 da velocidade é ouvido a 4 kHz, e uma gravação de
um minuto passa a durar dez minutos. O seletor exibe essa conversão para a
velocidade escolhida.

O seletor apenas define as propriedades `playbackRate` e `preservesPitch` de
cada elemento `<audio>` no navegador. Nenhum áudio é decodificado ou
processado pela página, e os players continuam sem carregar nada até serem
reproduzidos. As gravações devem ter uma taxa de amostragem alta o suficiente
para conter o ultrassom (por exemplo, uma gravação de AudioMoth a 250 ou
384 kHz). 1/16 é a menor velocidade que os navegadores reproduzem de forma
confiável.

### Modo de Anotação

`--annotate` transforma o calendário em uma ferramenta simples de anotação.
Cada célula recebe uma caixa de seleção sob a sua miniatura, e uma barra no
topo da página exporta as gravações selecionadas como um arquivo de texto
simples:

```bash
spectro-calendar /dados/sitio-1 --include-audio --annotate
```

As gravações de interesse são selecionadas durante a revisão do calendário, e o
botão **Export selection (.txt)** baixa a lista. Nenhum rótulo precisa ser
digitado, pois a própria lista exportada serve como anotação. Cada linha
identifica uma gravação selecionada, no formato escolhido no seletor ao lado
do botão:

| Formato | Exemplo de linha |
|---|---|
| `filename` (padrão) | `20260304_100000.WAV` |
| `date & time` | `2026-03-04 10:00:00` |
| `filename + date & time` | `20260304_100000.WAV<TAB>2026-03-04 10:00:00` |

As linhas seguem a ordem cronológica, e o arquivo é nomeado
`annotations_<label>_<AAAAMMDD-HHMMSS>.txt`, em que o carimbo de tempo é o
momento da exportação, de modo que exportações sucessivas não se sobrescrevem.
Com `--recursive`, cada nome de arquivo inclui a subpasta em que foi
encontrado (por exemplo, `moth-a/20260304_100000.WAV`), pois o mesmo nome pode
ocorrer uma vez por gravador. Calendários gerados para bandas de frequência
diferentes (`--spec-label lf`, `hf` e assim por diante) exportam com os seus
próprios nomes.

Para selecionar várias gravações de uma vez, clica-se em uma caixa de seleção
e, em seguida, em outra mantendo **Shift** pressionado. Todas as caixas no
retângulo entre as duas recebem então o mesmo estado: os horários entre as
duas linhas, em cada data entre as duas colunas. Por exemplo, clicar em
01 Mar 05:00 e depois clicar com Shift em 03 Mar 07:00 seleciona das 05:00 às
07:00 nos dias 1, 2 e 3 de março. Todas as caixas assumem o novo estado da
caixa clicada com Shift, de modo que a mesma ação sobre caixas marcadas limpa
o intervalo. Cada clique com Shift também se torna o canto inicial do próximo
intervalo.

As células selecionadas são destacadas, a barra exibe o número de gravações
selecionadas, e **Clear selection** limpa toda a seleção após uma confirmação.
A seleção também é armazenada no armazenamento local do navegador, sob uma
chave derivada da localização da página, de modo que é restaurada quando o
calendário é recarregado ou reaberto posteriormente.

O Chrome não oferece armazenamento local a páginas abertas diretamente do disco
(`file://`). No Chrome, portanto, a seleção é mantida somente enquanto a aba
estiver aberta, e deve ser exportada antes que a aba seja fechada. O Firefox
oferece armazenamento local a essas páginas. Servir o calendário por HTTP
torna a seleção persistente em qualquer navegador; nesse caso, o servidor deve
ser iniciado em um diretório que contenha tanto o diretório de saída quanto as
gravações, para que os players de áudio alcancem as gravações (por exemplo,
`python -m http.server` executado no diretório pai comum aos dois). Todas as
demais funções, incluindo a exportação, funcionam a partir de `file://` nos
dois navegadores.

### Gravações Remotas via SSH

Gravações armazenadas em uma máquina remota podem ser processadas montando o
diretório remoto localmente com o [sshfs](https://github.com/libfuse/sshfs) e
informando o ponto de montagem como diretório de gravações. Como a ferramenta
apenas lê o diretório de gravações, uma montagem somente leitura é suficiente:

```bash
mkdir -p ~/mnt/sitio-1
sshfs usuario@host:/caminho/no/servidor ~/mnt/sitio-1 \
  -o ro,reconnect,cache=yes,kernel_cache \
  -o IdentityFile=$HOME/.ssh/sua_chave,IdentitiesOnly=yes

spectro-calendar ~/mnt/sitio-1 \
  --output-dir ~/calendarios/sitio-1 \
  --use-ffmpeg --include-audio
```

**Determinação do caminho remoto.** O sshfs usa o subsistema SFTP do servidor
SSH, cuja visão do sistema de arquivos frequentemente difere da de um shell de
login. Dispositivos NAS, em particular, costumam apresentar as pastas
compartilhadas na raiz do SFTP. Um caminho que funciona com `scp` pode,
portanto, falhar com o sshfs, especialmente em clientes OpenSSH anteriores à
versão 9.0, nos quais o `scp` usa o shell remoto em vez do SFTP. O caminho
correto pode ser obtido diretamente pelo SFTP:

```bash
sftp usuario@host
sftp> pwd     # o diretório atual, segundo o SFTP
sftp> ls /    # o conteúdo da raiz do SFTP
```

Em um dispositivo Synology, por exemplo, o shell pode informar
`/volume1/homes/usuario`, enquanto o SFTP apresenta a pasta compartilhada como
`/Gravacoes/sitio-1`; o sshfs requer este último. O argumento
`usuario@host:caminho` inteiro deve estar entre aspas quando o caminho remoto
contiver espaços ou caracteres acentuados. A página gerada referencia as
gravações pelo ponto de montagem local, de modo que os nomes remotos não
aparecem nela.

A geração dos espectrogramas transfere cada gravação selecionada pela conexão
uma vez. Essa é a parte mais lenta do processo e não pode ser evitada, pois
cada arquivo precisa ser lido por completo para o cálculo do seu
espectrograma. Os filtros de data e horário (`--dates` ou
`--start-date`/`--end-date`, `--start-time`/`--end-time`, `--time-step`) são
o meio de reduzir a transferência. Todos os arquivos gerados são gravados
localmente, em `--output-dir`.

**A reprodução não exige baixar as gravações.** Com `--include-audio`, cada
player de áudio lê a sua gravação através da montagem, e `preload="none"`
garante que somente as gravações efetivamente reproduzidas sejam transferidas,
e apenas até o ponto em que são ouvidas. Abrir o calendário em si não
transfere nada. Como WAV é um formato sem compressão (um minuto de áudio do
AudioMoth a 48 kHz ocupa aproximadamente 23 MB), a reprodução é confortável em
uma rede local ou VPN, mas pode travar em uma conexão lenta.

Dois pontos adicionais se aplicam:

- O calendário deve ser aberto diretamente do disco (`file://`). O caminho
  relativo do diretório de saída até o ponto de montagem sai do diretório de
  saída (por exemplo, `../../mnt/sitio-1/20260304_100000.WAV`), de modo que um
  servidor web iniciado no diretório de saída, como `python -m http.server`,
  não consegue servir o áudio, embora as miniaturas carreguem normalmente.
- Se a conexão for interrompida, `-o reconnect` restabelece a montagem, mas as
  leituras em andamento falham primeiro. Executar o comando novamente gera os
  espectrogramas que faltaram; com o backend ffmpeg, como no exemplo acima, os
  espectrogramas existentes são mantidos e não são transferidos novamente. A
  montagem é removida com `fusermount -u ~/mnt/sitio-1`.

## Funcionamento

Todo o processamento está implementado em `src/spectro_calendar/cli.py`. Uma
execução consiste nas seguintes etapas:

1. **Leitura dos argumentos.** O `argparse` define as opções listadas acima e
   converte os seus valores para os tipos adequados. Antes da leitura
   principal, uma passagem preliminar extrai `--config`; `load_yaml_config` lê
   esse arquivo, rejeita chaves desconhecidas e instala os seus valores como
   padrões do parser com `parser.set_defaults(**config)`. Como o argparse usa
   um padrão somente para opções ausentes da linha de comando, qualquer opção
   informada na linha de comando tem precedência tanto sobre o arquivo de
   configuração quanto sobre o padrão embutido.

2. **Limpeza opcional.** Com `--clear`, os arquivos `*<label>.png` existentes
   no diretório de saída são apagados, para que espectrogramas de uma execução
   anterior com parâmetros diferentes não permaneçam.

3. **Descoberta dos arquivos.** Todos os arquivos `.wav` (sem distinção entre
   maiúsculas e minúsculas) do diretório de gravações são listados, incluindo
   as subpastas com `--recursive`. Quando `--filename-prefix` é definido, os
   arquivos sem esse prefixo são excluídos. `parse_recording_datetime` remove
   o prefixo do radical de cada nome de arquivo e interpreta o restante com
   `datetime.strptime` e `--datetime-format`; um nome de arquivo que não
   corresponde interrompe a execução com um erro que identifica o arquivo. Os
   arquivos são então ordenados pela data e hora interpretadas, e não pelo
   nome, e todas as etapas seguintes dependem somente desses valores, e não da
   convenção de nomes.

4. **Filtragem por data.** As datas informadas com `--dates` são comparadas com
   as datas presentes (`validate_dates` informa qualquer data sem gravações).
   Com `--start-date`/`--end-date`, `filter_dates_by_range` mantém as datas
   dentro do intervalo inclusivo; os limites não precisam ter gravações,
   qualquer um deles pode ser omitido, e a execução é interrompida se o
   intervalo não contiver gravações. As duas formas são mutuamente exclusivas;
   sem nenhuma delas, todas as datas são usadas.

5. **Filtragem por horário.** `filter_wav_files_by_time_window` mantém os
   arquivos cujo horário está entre `--start-time` e `--end-time` em cada data
   selecionada. Essa janela é sempre aplicada, com padrões que incluem o dia
   inteiro.

6. **Redução por intervalo de tempo.** Com `--time-step`,
   `filter_wav_files_by_time_step` percorre os arquivos de cada dia em ordem
   cronológica e mantém o primeiro arquivo no horário mantido anteriormente
   mais N minutos, ou depois dele. Isso reduz, por exemplo, uma gravação por
   minuto a uma a cada 30 minutos, sem exigir que as gravações comecem em
   horários exatos.

7. **Geração dos espectrogramas.** Cada arquivo restante é processado por um
   de dois backends intercambiáveis. `--use-ffmpeg` seleciona o backend ffmpeg
   quando o programa `ffmpeg` é encontrado (`shutil.which`); caso contrário, o
   backend scipy é usado. Ambos gravam as suas imagens no diretório de saída:
   - **`spectrogram_ffmpeg`** executa o filtro `showspectrumpic` do ffmpeg,
     encadeado com um filtro `scale`, de modo que a miniatura é produzida a
     partir da gravação em uma única chamada. Com `--save-fullsize`, o ffmpeg
     é executado duas vezes: uma para produzir a imagem em tamanho real e
     outra para reduzi-la à miniatura. Gravações cujas imagens solicitadas já
     existem são ignoradas.
   - **`spectrogram_scipy`** lê a gravação com `scipy.io.wavfile`, converte
     gravações estéreo em mono, calcula uma transformada de Fourier de tempo
     curto (`scipy.signal.stft`, `nperseg=2048`), restringe-a ao intervalo
     entre `--lowest-freq` e `--highest-freq` e plota a magnitude em decibéis
     com o matplotlib (mapa de cores `plasma`, sem eixos). A imagem em tamanho
     real, mantida em memória a menos que `--save-fullsize` seja informado, é
     então reduzida à miniatura com o Pillow. Imagens existentes são geradas
     novamente.

   Uma gravação que não pode ser lida, como um arquivo truncado quando o cartão
   de memória de um gravador encheu, é informada no fim da execução e recebe
   uma célula vazia, sem interromper a execução. Quando `--max-cores` é maior
   que 1, as gravações são distribuídas em um
   `concurrent.futures.ProcessPoolExecutor` desse tamanho. O backend ffmpeg se
   beneficia porque cada processo passa a maior parte do tempo aguardando o
   seu ffmpeg, e o backend scipy porque o cálculo é executado em vários
   processos ao mesmo tempo. A docstring do módulo `cli.py` contém tempos de
   processamento medidos para os dois backends com 1, 2, 4 e 6 processos.

8. **Geração do calendário.** `generate_html` constrói uma correspondência
   entre a data e a hora de cada gravação processada e o seu arquivo, e grava
   `index_<label>.html` em UTF-8. A página é composta por um cabeçalho fixo
   (`spectro-calendar`), as barras de ferramentas opcionais, uma tabela com
   uma coluna por data e uma linha por horário do dia, cuja linha de cabeçalho
   e primeira coluna permanecem visíveis durante a rolagem, e um rodapé com um
   link para [biodiversica.xyz](https://biodiversica.xyz/). Cada célula exibe
   a miniatura correspondente, acompanhada de um player de áudio quando
   `--include-audio` é informado, ou fica vazia quando não existe gravação
   para aquela data e horário.

   Os players usam `preload="none"`. Sem isso, o navegador lê o cabeçalho de
   todas as gravações ao abrir a página, apenas para exibir a sua duração; em
   um calendário grande (um mês com intervalos de 15 minutos tem cerca de 3000
   células), isso atrasa consideravelmente a página, sobretudo quando as
   gravações estão em uma montagem de rede. Os endereços das imagens e dos
   áudios são calculados por `html_link` em relação ao diretório de saída, de
   modo que o diretório de saída e o diretório de gravações não precisam estar
   aninhados. Cada segmento do caminho é codificado, de modo que nomes com
   espaços, acentos ou símbolos como `#` funcionam corretamente; quando não
   existe caminho relativo (unidades diferentes no Windows), um endereço
   absoluto `file://` é usado.

   Com `--speed-control`, a página inclui o seletor de velocidade e o script
   `SPEED_SCRIPT`. Com `--annotate`, cada célula inclui também uma caixa de
   seleção que carrega o caminho da gravação relativo ao diretório de
   gravações e o seu carimbo de data e hora, e a página inclui a barra de
   ferramentas e o script `ANNOTATION_SCRIPT`. Os dois scripts são embutidos na
   página, em vez de gravados como arquivos `.js` separados, para que o
   calendário continue sendo uma única página que pode ser movida ou
   compartilhada. Eles usam JavaScript simples, sem bibliotecas. O script de
   anotação monta o texto exportado a partir dos atributos das caixas de
   seleção e o oferece como download, aplica os intervalos de Shift+clique
   usando a linha e a coluna de cada caixa e armazena a seleção no
   `localStorage`. Todo acesso ao armazenamento é protegido, pois o Chrome
   nega armazenamento a páginas `file://` e a página deve continuar
   funcionando nesse caso.

9. **Folha de estilos.** O CSS de `SPECTROGRAM_TABLE_CSS` é gravado como
   `spectrogram-table.css` ao lado da página do calendário, para que a página
   seja exibida corretamente quando aberta diretamente do disco.

10. **Tempo de execução.** O tempo total de processamento é medido e exibido no
    fim da execução, pelo mesmo método usado na comparação de backends da
    docstring do módulo.

## Backends

| | ffmpeg | scipy |
|---|---|---|
| Velocidade | Mais rápido (veja as medições em `cli.py`) | Mais lento |
| Requisitos | O programa `ffmpeg` no PATH | Somente pacotes Python (`scipy`, `matplotlib`, `pillow`) |
| Paleta de cores | Configurável com `--color-choice` | Sempre `plasma` |
| Escala de frequência | Configurável com `--freq-scale` (`lin` ou `log`) | Somente linear |

Se `--use-ffmpeg` for informado mas o ffmpeg não for encontrado, o backend
scipy é usado automaticamente.

## Desenvolvimento

```bash
uv sync               # instala o projeto e as ferramentas de desenvolvimento
uv run ruff check .   # verificação de estilo
uv run pytest         # testes
```

Os testes geram gravações sintéticas curtas, executam a ferramenta completa
sobre elas e inspecionam os arquivos gerados. O teste do backend ffmpeg é
ignorado quando o ffmpeg não está instalado. A integração contínua executa a
verificação de estilo e os testes no Linux, no macOS e no Windows, e executa
também os instaladores nos três sistemas com o pacote gerado.

Estrutura do projeto:

```
src/spectro_calendar/
├── __init__.py   # versão do pacote
├── __main__.py   # permite `python -m spectro_calendar`
├── cli.py        # leitura dos argumentos e todo o processamento
└── richhelp.py   # saída formatada de --help
tests/            # testes de ponta a ponta
scripts/          # instaladores anexados a cada versão
```

### Publicação de uma Versão

Defina a nova versão tanto em `pyproject.toml` quanto em
`src/spectro_calendar/__init__.py`, execute `uv lock`, faça o commit da
alteração e, em seguida, crie e envie uma tag:

```bash
git tag v0.2.0 && git push origin v0.2.0
```

A tag dispara `.github/workflows/release.yml`. Os testes são executados nos
três sistemas, o pacote é enviado ao PyPI e uma versão **em rascunho** é
criada no GitHub, com os instaladores anexados e as notas de
`.github/release-notes.md`. Depois que os destaques forem escritos, a versão
deve ser publicada, pois os comandos de instalação baixam da versão
*publicada* mais recente. A compilação falha se a tag não corresponder à
versão em `pyproject.toml`, ou se essa versão for diferente da versão em
`src/spectro_calendar/__init__.py`.

## Licença

MIT; veja [LICENSE](LICENSE).
