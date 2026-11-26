# Funcionamento

*[English](../en/how-it-works.md) · Português (Brasil)*

Todo o processamento está implementado em `src/spectro_calendar/cli.py`. Uma
execução consiste nas seguintes etapas:

1. **Leitura dos argumentos.** O `argparse` define as [opções](cli.md) e
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
   de dois [backends](backends.md) intercambiáveis. `--use-ffmpeg` seleciona o
   backend ffmpeg quando o programa `ffmpeg` é encontrado (`shutil.which`);
   caso contrário, o backend scipy é usado. Ambos gravam as suas imagens no
   diretório de saída:
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
   uma coluna por data (rotulada `DD-MM-AAAA`) e uma linha por horário do dia,
   cuja linha de cabeçalho e primeira coluna permanecem visíveis durante a
   rolagem, e um rodapé com um link para
   [biodiversica.xyz](https://biodiversica.xyz/). Cada célula exibe a
   miniatura correspondente, acompanhada de um player de áudio quando
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

   As configurações da execução, listadas por `settings_summary`, são
   colocadas em uma tabela, em um painel ligado ao **?** do cabeçalho da
   página. Ele é exibido ao passar o mouse ou ao receber o foco, apenas com
   CSS, sem script.

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
