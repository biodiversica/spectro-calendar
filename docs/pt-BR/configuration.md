# Arquivo de Configuração

*[English](../en/configuration.md) · Português (Brasil)*

As opções também podem ser definidas em um arquivo YAML passado com `--config`:

```bash
spectro-calendar --config example_config.yaml
```

[`example_config.yaml`](../../example_config.yaml) contém um exemplo completo.
Cada chave corresponde a uma [opção de linha de comando](cli.md), com hífens
substituídos por sublinhados (por exemplo, `--output-dir` torna-se
`output_dir`). O diretório de gravações também pode ser definido, como
`recording_dir`, de modo que uma execução pode ser descrita inteiramente por um
arquivo de configuração.

As opções informadas na linha de comando têm precedência sobre o arquivo de
configuração, que apenas fornece valores padrão:

```bash
# Usa todos os valores de example_config.yaml, exceto max_cores, que passa a
# ser 2 independentemente do valor no arquivo.
spectro-calendar --config example_config.yaml --max-cores 2
```

Uma chave não reconhecida no arquivo de configuração é informada como erro,
com a lista das chaves válidas.

A página do calendário lista as configurações com que foi gerada, e a origem de
cada uma, sob o **?** do seu cabeçalho (veja
[As Configurações de um Calendário](usage.md#as-configurações-de-um-calendário)).
