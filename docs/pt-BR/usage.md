# Geração de um Calendário

*[English](../en/usage.md) · Português (Brasil)*

```bash
spectro-calendar /caminho/para/gravacoes
```

O diretório de gravações deve conter arquivos `.wav` cujos nomes incluam a data
e a hora da gravação. Por padrão, a ferramenta espera a convenção do AudioMoth,
`AAAAMMDD_HHMMSS.WAV` (por exemplo, `20260315_063000.WAV`); outras convenções
são configuradas com `--datetime-format` e `--filename-prefix` (veja
[Formatos de Nome de Arquivo](filename-formats.md)). Somente o nível superior
do diretório é examinado, a menos que `--recursive` seja informado (veja
[Subpastas](#subpastas)).

## Arquivos Gerados

Uma execução produz os seguintes arquivos, no diretório de gravações por
padrão ou no diretório indicado com `--output-dir`:

- `<nome>-thumbnail-<label>.png`: uma miniatura de espectrograma por gravação.
- `<nome>-fullsize-<label>.png`: o espectrograma em resolução completa,
  gravado somente com `--save-fullsize`.
- `index_<label>.html`: a página do calendário.
- `spectrogram-table.css`: a folha de estilos usada pela página do calendário.

`<label>` é o valor de `--spec-label`, vazio por padrão. O calendário é
visualizado abrindo `index_<label>.html` em um navegador. As suas colunas são
rotuladas com datas no formato `DD-MM-AAAA`, enquanto as opções de data
(`--dates`, `--start-date`, `--end-date`) recebem datas como `AAAAMMDD`.

## Um Diretório de Saída Separado

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

## Subpastas

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

## As Configurações de um Calendário

Cada calendário registra as configurações com que foi gerado. Passe o mouse
sobre o **?** à direita do cabeçalho da página (ou chegue a ele com Tab, ou
toque nele em uma tela sensível ao toque) para vê-las: uma tabela com um
parâmetro por linha, nomeado como no
[arquivo de configuração](configuration.md), com o valor usado, tenha ele vindo
da linha de comando, do arquivo de configuração ou do padrão. Acima da tabela
aparecem a versão do spectro-calendar, o horário da execução e o arquivo de
configuração usado, se houver.
