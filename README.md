# HOMERun Camp

A HOMER promotional 3D endless runner in the style of Subway Surfers. Run through the campsite, into the house, out to the backyard and back to camp. Dodge camping gear in three lanes, collect leaf coins, keep away from the bear, and make the Top 10.

**Play:** https://shintar0u923143-dot.github.io/HOMERun-Camp/

## Controls

| Action | Phone | Keyboard |
|---|---|---|
| Change lane | Swipe left / right | ← → or A D |
| Jump (BBQ grill, hammock, chair, cat) | Swipe up | ↑, W or Space |
| Roll (tent, table, hammock) | Swipe down | ↓ or S |
| Pause | Tap the ❚❚ button | P or Esc |

Run up the ladder onto the camper van, or onto a kitchen counter, and across the top. Grab the HOMER wagon for a speed boost. One life: three close calls and the bear catches you.

## How it's built

- `index.html` is the game: fully 3D with [three.js](https://threejs.org) (loaded from the jsDelivr CDN). The camper is a code-built rigged character with physics-driven run, jump and roll animation; trees, props and scenery are 3D models. Source: `src/game-full3d.html`. This is the file GitHub Pages serves (`full3d.html` is the same build).
- `cards.html` / `src/game3d.html` is the previous version that uses the Gemini pictures as cards in the 3D world.
- `src/game3d.html` is the 3D source. Obstacles, the van, the house front and back doors, the hallway and fences are 3D models built in code. The Gemini art is used for the ground tiles (the 3D floor), the trees beside the path, the horizon and the runner poses.
- `classic.html` / `src/game.html` is the earlier 2D version, kept for comparison.
- `assets/` holds the cut-out game art (WebP):
  - `tile-<stage>-0N`: top-down ground tiles that loop and scroll in perspective
  - `wall-<stage>-<side>-0N`: side-view wall and fence tiles
  - `horizon-<stage>`: the far sky (the only layer that stays still)
  - `prop-<side>-<name>`: trees and other props beside the path
  - `obs-mid-lane-<name>`: each obstacle seen straight from behind. It's used in all three lanes, because side lanes are only about 5° off-centre with this camera. Turn on `USE_LANE_VIEWS` in `src/game.html` to use separate left/right art.
  - `runner-<lane>-lane-<pose>`: runner poses
  - Anything missing falls back to the older art, so new images can be added a few at a time.
- `art-sheets/` holds the original Gemini sheets. `art-prompts.html` has the prompts used to make them.
- `tools/` contains the build scripts.

## Adding new art

```bash
python3 tools/cut.py art-sheets/sheet-obs-van.jpg sheet-obs-van   # cut a sheet into assets/
python3 tools/seam.py tile-camp                                   # match ground tile edges after cutting tiles
python3 tools/build.py                                            # rebuild index.html (full 3D)
python3 tools/build.py cards.html                                 # rebuild the Gemini-picture version
python3 tools/build.py classic.html                               # rebuild the 2D classic version
python3 tools/cut.py --list                                       # every sheet name and what it produces
```

Needs Python 3 with Pillow, NumPy and SciPy.

## Scores

The Top 10 scoreboard is currently saved on each device (browser storage).

## Online Top 10 and HOMER promo sign-up

Works the same way as the ARGOPOWER game: a Google Sheet with a small Apps Script web app.

1. Go to sheets.new and name the sheet "HOMERun Camp Scores" (ideally from a CBK company Google account).
2. Extensions > Apps Script. Paste all of `apps-script/Code.gs`, then Save.
3. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone. Deploy and authorize.
4. Copy the web app link (ends in `/exec`) and paste it into `config.js` between the quotes. Commit.

Scores go to the `scores` tab; promo sign-ups (name, email, mobile, consent) go to the private `contacts` tab and are never shown in the game.

The sign-up form is hidden from the public until the DPO / Legal review is done. To preview it, open the game link with `?promo=1` at the end.
To go live, fill in the `[bracketed]` items in `PRIV` in `src/game-full3d.html`, set `PROMO_ON = true`, and rebuild with `python3 tools/build.py`.
