# Configuration File

*English · [Português (Brasil)](../pt-BR/configuration.md)*

Options can also be set in a YAML file passed with `--config`:

```bash
spectro-calendar --config example_config.yaml
```

[`example_config.yaml`](../../example_config.yaml) contains a complete example.
Each key corresponds to a [command-line option](cli.md), with hyphens replaced
by underscores (for example, `--output-dir` becomes `output_dir`). The
recording directory can also be set, as `recording_dir`, so that a run can be
described entirely by a configuration file.

Options given on the command line take precedence over the configuration
file, which only supplies default values:

```bash
# Uses every value from example_config.yaml, except max_cores, which is set
# to 2 regardless of the value in the file.
spectro-calendar --config example_config.yaml --max-cores 2
```

An unrecognised key in the configuration file is reported as an error, with
the list of valid keys.

The calendar page lists the settings it was made with, and where each came
from, under the **?** in its header (see
[The Settings of a Calendar](usage.md#the-settings-of-a-calendar)).
