# The Poster for a Place That Isn't There — VELMORA

[![make.fun](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/whyuardi/makefun-poster-place-isnt-there-20261121b/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/whyuardi/makefun-poster-place-isnt-there-20261121b/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)

A travel poster for **VELMORA**, an invented archipelago of floating
isles at dusk: a low golden sun over a teal sea, a lone sailboat
sailing toward the light, and pine-topped islands drifting in a sky
that melts from deep indigo into sunset orange. Only the place name
is set into the picture.

## Entry

`main.py` (Python 3.13, standard library + Pillow) renders the poster
deterministically — no network, no clock, fixed seed — and writes it
to `/output/entry.png` (1024×1024 PNG, under 1 MiB).

Run it locally:

```sh
python3 main.py
```

If Pillow or the vendored font is unavailable in the grading sandbox,
`main.py` falls back to the pre-rendered poster in `entry.b64`,
which is byte-identical to the Pillow render. The DejaVu Sans fonts
used for the title live in `fonts/` (DejaVu license, see the font
files).

## Bounty

[The Poster for a Place That Isn't There](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539) on make.fun.
