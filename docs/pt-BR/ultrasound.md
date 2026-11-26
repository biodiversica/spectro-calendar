# Ouvindo Ultrassom

*[English](../en/ultrasound.md) · Português (Brasil)*

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
