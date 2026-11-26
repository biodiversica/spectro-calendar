# Backends

*[English](../en/backends.md) · Português (Brasil)*

Os espectrogramas são desenhados por um de dois backends intercambiáveis. O
scipy é o padrão; `--use-ffmpeg` seleciona o ffmpeg.

| | ffmpeg | scipy |
|---|---|---|
| Velocidade | Mais rápido (veja as medições em `cli.py`) | Mais lento |
| Requisitos | O programa `ffmpeg` no PATH | Somente pacotes Python (`scipy`, `matplotlib`, `pillow`) |
| Paleta de cores | Configurável com `--color-choice` | Sempre `plasma` |
| Escala de frequência | Configurável com `--freq-scale` (`lin` ou `log`) | Somente linear |

Se `--use-ffmpeg` for informado mas o ffmpeg não for encontrado, o backend
scipy é usado automaticamente. [Instalação](installation.md) indica como
instalar o ffmpeg, e [Funcionamento](how-it-works.md) descreve o que cada
backend faz.
