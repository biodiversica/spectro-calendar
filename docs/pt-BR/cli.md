# Opções da Linha de Comando

*[English](../en/cli.md) · Português (Brasil)*

`spectro-calendar --help` lista as mesmas opções. Todas as opções também podem
ser definidas em um [arquivo de configuração](configuration.md).

## Exemplo

O exemplo a seguir usa o backend ffmpeg com seis processos paralelos, exibe
somente frequências até 2 kHz e mantém uma gravação a cada 30 minutos entre
05:00 e 09:00:

```bash
spectro-calendar /dados/sitio-1 \
  --use-ffmpeg --max-cores 6 \
  --spec-label lf --highest-freq 2000 \
  --time-step 30 --start-time 050000 --end-time 090000
```

## Opções

| Opção | Padrão | Descrição |
|---|---|---|
| `recording_dir` | nenhum | Diretório que contém as gravações `.wav`. Posicional; obrigatório, a menos que seja definido como `recording_dir` no arquivo de configuração |
| `--config CAMINHO` | nenhum | Arquivo YAML com valores padrão das opções (veja [Arquivo de Configuração](configuration.md)) |
| `--version` | | Exibe a versão instalada e encerra |
| `--use-ffmpeg` | desligado | Usa o backend ffmpeg em vez do scipy. O backend scipy é usado quando o ffmpeg não está instalado (veja [Backends](backends.md)) |
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
| `--speed-control` | desligado | Adiciona um seletor de velocidade de reprodução (de 1× a 1/16) acima do calendário. Reduzir a velocidade também abaixa o tom, o que torna o ultrassom audível (veja [Ouvindo Ultrassom](ultrasound.md)). Requer `--include-audio` |
| `--annotate` | desligado | Modo de anotação: adiciona uma caixa de seleção sob cada miniatura e uma barra que exporta as gravações selecionadas como uma lista `.txt` (veja [Modo de Anotação](annotation.md)) |
| `--dates D1 D2 ...` | todas as datas | Processa somente as datas informadas, no formato `AAAAMMDD`. Cada data deve ter gravações |
| `--start-date AAAAMMDD` | data mais antiga | Primeira data de um intervalo contínuo. Não pode ser combinada com `--dates` |
| `--end-date AAAAMMDD` | data mais recente | Última data do intervalo (inclusive). Não pode ser combinada com `--dates` |
| `--time-step N` | nenhum | Mantém no máximo uma gravação por intervalo de N minutos em cada dia |
| `--start-time HHMMSS` | `000000` | Início da janela diária de horários |
| `--end-time HHMMSS` | `235900` | Fim da janela diária de horários |
| `--recursive` | desligado | Examina também as subpastas do diretório de gravações (veja [Subpastas](usage.md#subpastas)) |
| `--output-dir DIR` | diretório de gravações | Diretório para todos os arquivos gerados; criado se não existir. Quando definido, o diretório de gravações é apenas lido |
| `--datetime-format FMT` | `%Y%m%d_%H%M%S` | Formato `strptime` que descreve como a data e a hora aparecem em cada nome de arquivo, após a remoção do prefixo (veja [Formatos de Nome de Arquivo](filename-formats.md)) |
| `--filename-prefix PREFIXO` | `""` | Texto fixo que precede a data e a hora em cada nome de arquivo, por exemplo `SM4_` para `SM4_20260304_100000.wav` |
