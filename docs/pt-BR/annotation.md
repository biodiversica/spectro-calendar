# Modo de Anotação

*[English](../en/annotation.md) · Português (Brasil)*

`--annotate` transforma o calendário em uma ferramenta simples de anotação.
Cada célula recebe uma caixa de seleção sob a sua miniatura, e uma barra no
topo da página exporta as gravações selecionadas como um arquivo de texto
simples:

```bash
spectro-calendar /dados/sitio-1 --include-audio --annotate
```

## Exportação da Seleção

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

## Seleção de um Intervalo

Para selecionar várias gravações de uma vez, clica-se em uma caixa de seleção
e, em seguida, em outra mantendo **Shift** pressionado. Todas as caixas no
retângulo entre as duas recebem então o mesmo estado: os horários entre as
duas linhas, em cada data entre as duas colunas. Por exemplo, clicar em
01 Mar 05:00 e depois clicar com Shift em 03 Mar 07:00 seleciona das 05:00 às
07:00 nos dias 1, 2 e 3 de março. Todas as caixas assumem o novo estado da
caixa clicada com Shift, de modo que a mesma ação sobre caixas marcadas limpa
o intervalo. Cada clique com Shift também se torna o canto inicial do próximo
intervalo. Um lembrete disso aparece ao passar o mouse sobre **Annotation**, à
esquerda da barra.

## Conservação da Seleção

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
