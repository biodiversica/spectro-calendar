# Listening to Ultrasound

*English · [Português (Brasil)](../pt-BR/ultrasound.md)*

`--speed-control` adds a **Playback speed** selector above the calendar,
with the values 1×, 1/2, 1/4, 1/8, 1/10 and 1/16, which applies to every audio
player:

```bash
spectro-calendar /data/site-1 --include-audio --speed-control
```

The speed is changed in the same way as Audacity's "Change Speed" effect,
not as a tempo change that preserves pitch: the pitch is divided by the same
factor as the speed. This technique, known as time expansion, is the usual
way of listening to ultrasound. A 40 kHz bat call played at 1/10 speed is
heard at 4 kHz, and a one-minute recording lasts ten minutes. The selector
displays this conversion for the chosen speed.

The selector only sets the `playbackRate` and `preservesPitch` properties of
each `<audio>` element in the browser. No audio is decoded or processed by the
page, and the players still load nothing until they are played. The
recordings must have a sample rate high enough to contain the ultrasound (for
example, an AudioMoth recording at 250 or 384 kHz). 1/16 is the lowest speed
that browsers play reliably.
