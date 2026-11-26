# Formatos de Nome de Arquivo

*[English](../en/filename-formats.md) · Português (Brasil)*

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
