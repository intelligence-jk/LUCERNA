# LUCERNA: Latin for a lamp: numbers kept lit and readable

Formerly `maths-video-contrast`.

Colour contrast checker for maths videos.

## What it does
Light grey working on a white slide looks fine on your screen and disappears on a phone in sunlight. This tool computes the WCAG 2.x contrast ratio between a text colour and a background colour, tells you whether it passes AA and AAA (for normal and large text), checks a whole palette file at once, and suggests the nearest passing colour with the same hue.

## Example
```bash
python -m maths_video_contrast check "#777777" "#ffffff"
python -m maths_video_contrast suggest "#777777" "#ffffff"
python -m maths_video_contrast palette palette.example.json
```
Real output:
```
#777777 on #ffffff: 4.48:1  AA FAIL  AAA FAIL
#767676
title: #ffffff on #0b2a6f 13.33:1 AA pass
caption: #777777 on #ffffff 4.48:1 AA FAIL  try #767676
big number: #777777 on #ffffff 4.48:1 AA pass
```
The exit code is 0 when everything passes, 1 when something fails, 2 for bad input. The palette file is JSON: `{"pairs": [{"name": "...", "text": "#rrggbb", "background": "#rrggbb", "large": false}]}`. Add `--level AAA` to `suggest` or `palette`, and `--large` to `check` or `suggest`.

## The maths behind it
Each 8-bit channel is scaled to c = value / 255, then linearised (undoing the screen's gamma curve):

- if c <= 0.03928: c_lin = c / 12.92
- otherwise: c_lin = ((c + 0.055) / 1.055) ^ 2.4

The relative luminance is a weighted sum, because the eye is most sensitive to green and least to blue:

L = 0.2126 R_lin + 0.7152 G_lin + 0.0722 B_lin

L runs from 0 (black) to 1 (white). With L1 the lighter and L2 the darker colour, the contrast ratio is

ratio = (L1 + 0.05) / (L2 + 0.05)

The 0.05 stands for ambient light on the screen. It gives 1:1 for equal colours and 21:1 for black on white (1.05 / 0.05). WCAG asks for at least 4.5:1 (AA) or 7:1 (AAA) for normal text, and 3:1 (AA) or 4.5:1 (AAA) for large text (18 pt, or 14 pt bold, and up).

To suggest a fix, the colour is converted to HSL, the hue and saturation are held fixed, and the lightness is moved in steps of 0.001 in both directions, smallest move first, until the ratio passes. That gives the closest passing colour in lightness, with the same hue.

## Install and run
```bash
python -m pip install -e .
python -m pytest
python -m maths_video_contrast check "#000" "#fff"
```
Python 3.10 or newer, standard library only.

## Licence
MIT. Made by Math & Myth (mathandmyth.ae): one to one maths mentoring, online, across the UAE.
