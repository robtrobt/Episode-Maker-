# EPISODEline

Multi-agent animation pipeline: idea → script → storyboard → characters ‖ world →
key frames → consistency (fail loop) → animation → audio → edit.

Runs end to end on free services and local tools — no API keys, no paid tiers,
and `--offline` needs no network at all.

## Run it

```bash
python main.py                                  # free models + local frames
python main.py "Pip finds a lost puppy in the band room"   # any idea
python main.py --images pollinations            # try free AI frames (slow tier)
python main.py --offline                        # no network at all
python main.py --characters-dir casts/iggies --out runs
```

Requires Python 3.10+ and (for video) ffmpeg on PATH. Nothing to `pip install`:
the only dependencies are the standard library and the `ffmpeg` binary.

Every run writes to `output/<timestamp>-<slug>/`:

```
episode.mp4        final cut (a camera move on each frame + mixed audio)
thumbnail.png      first key frame
frames/            key frames
audio/             music bed, spoken lines, mixed track
clips/             per-shot video clips
*.json             every stage's output (script, storyboard, visuals, …)
```

## Where the free generation comes from

| Stage | Default | Cost | Notes |
|-------|---------|------|-------|
| Script | Pollinations `openai-fast` | free, no key | 1 reply / 45s per IP |
| Key frames | local procedural art | free, instant | drawn in Python from the character palette |
| Voice | Google Translate TTS | free, no key | one voice per language, pitch-shifted per character |
| Music | procedural WAV | free, local | generated with the standard library |
| Video | ffmpeg | free, local | zoompan + concat + mux |

`--images pollinations` swaps the local frames for free AI frames. That tier is
limited to **one image per 45 seconds per IP** and the classic endpoint is often
busy, so a six-frame episode can take several minutes and some frames may still
fall back to local art. Everything degrades instead of failing:

- text → the built-in script
- image → local procedural frame (character palette, flat shapes)
- voice → that line is silent, music continues
- video → skipped if ffmpeg is missing

Higher limits, still free: set `POLLINATIONS_TOKEN` to a free pollen key, or point
text at a local [Ollama](https://ollama.com) daemon
(`TEXT_PROVIDER = "ollama"` in `episodeline/config.py`, then `ollama pull llama3.2`).

## Characters

The current cast is the Iggies: Milo, Pip, Romster, Yoshi, Susie and Sasha.
Each has a folder built from their turnaround sheet (palette, wardrobe,
personality, voice note) plus the sheet itself in `references/`.

Character design lives in `characters/<slug>/character.json`, one folder per
character, with optional reference art in `references/`.

- Edit a folder → every shot prompt for that character changes on the next run.
- The script agent is given the cast list, so new episodes are written for
  Milo, Pip, Romster, Yoshi, Susie and Sasha instead of inventing speakers.
- A speaker with no folder gets one scaffolded automatically (with a warning);
  edit it, re-run, and the design is locked in.
- `characters/_template/` is the copy-me example; see `characters/README.md` for
  every field.

The Visual agent builds frame prompts from the folder's canonical anchor
(description + wardrobe + palette), and the Consistency agent fails the loop when
a frame drifts from that anchor, drops a character from the shot, or writes a
missing/truncated image.

Each folder also carries a `features` list — `glasses`, `backpack`, `toolkit`,
`drum-harness`, `drumsticks`, `microphone`, `bass`, `guitar`, `skateboard`,
`tail`, `fringe`, `mane`, `ponytail`, `long-hair`. The local renderer draws
them from the character's own palette (so Milo's glasses and Romster's drum
kit appear even at zero cost), and the list is repeated in the AI prompt.
Unknown names are ignored; add new ones in `episodeline/providers.py`
(`FEATURE_ALIASES`).

## Known limits

- "Animation" is a camera move over each key frame, not generated motion.
- SFX are listed in the audio plan but not synthesised.
- Free TTS has a single voice per language; character `voice` notes nudge pitch.
- Local procedural frames are flat stand-ins: palette, silhouette and
  `features` props, not illustrations — use `--images pollinations` (or wire
  your own `image_gen`) for real art.
- The consistency check is prompt- and asset-level; a vision model diffing
  rendered frames against `references/` is the plug-in point for the rest.
