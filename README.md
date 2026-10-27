# HOMERun Camp

A HOMER promotional endless runner in the style of Subway Surfers. Run through the campsite, into the house, out to the backyard and back to camp. Dodge camping gear in three lanes, collect leaf coins, keep away from the bear, and make the Top 10.

**Play:** https://shintar0u923143-dot.github.io/HOMERun-Camp/

## Controls

| Action | Phone | Keyboard |
|---|---|---|
| Change lane | Swipe left / right | ← → or A D |
| Jump (BBQ grill, hammock, chair, cat) | Swipe up | ↑, W or Space |
| Roll (tent, table, hammock) | Swipe down | ↓ or S |

Run up the ladder onto the camper van, or onto a kitchen counter, and across the top. Grab the HOMER wagon for a speed boost. One life: three close calls and the bear catches you.

## How it's built

- `index.html` is the whole game in one file, with every image built in. This is the file GitHub Pages serves.
- `src/game.html` is the game source. Images are loaded from `assets/` by file name.
- `assets/` holds the cut-out game art (WebP):
  - `tile-<stage>-0N`: top-down ground tiles that loop and scroll in perspective
  - `wall-<stage>-<side>-0N`: side-view wall and fence tiles
  - `horizon-<stage>`: the far sky (the only layer that stays still)
  - `prop-<side>-<name>`: trees and other props beside the path
  - `obs-<left|mid|right>-lane-<name>`: each obstacle as seen in each lane
  - `runner-<lane>-lane-<pose>`: runner poses
  - Anything missing falls back to the older art, so new images can be added a few at a time.
- `art-sheets/` holds the original Gemini sheets. `art-prompts.html` has the prompts used to make them.
- `tools/` contains the build scripts.

## Adding new art

```bash
python3 tools/cut.py art-sheets/sheet-obs-van.jpg sheet-obs-van   # cut a sheet into assets/
python3 tools/seam.py tile-camp                                   # match ground tile edges after cutting tiles
python3 tools/build.py                                            # rebuild index.html
python3 tools/cut.py --list                                       # every sheet name and what it produces
```

Needs Python 3 with Pillow, NumPy and SciPy.

## Scores

The Top 10 scoreboard is currently saved on each device (browser storage).
