# ATR batch — aarau-fraktur-gemini-v1

- pages: **427**
- started: 2026-11-06T13:09:22+00:00
- wall time: 59.8 min

| model | read | skipped | failed | empty | looped | arguing | cut off | chars/page | s/page | wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemini-3.8-flash` | 427 | 0 | 0 | 3 | 0 | 0 | 0 | 2384 | 8.4 | 59.8 min |

**These columns are not quality.** There is no ground truth in this run, and characters per page measures how much a model wrote, not how much of it is right — a model that hallucinates fluently leads this table. Comparing the readings is the point; the numbers only say what each run cost and whether it completed. Measuring accuracy needs transcribed lines and `eval/linebench.py`.

## Pages that came back empty

- `gemini-3.8-flash`: 3 of 427 page(s) (1%)
  - 1884_p001
  - 1888_p001
  - 1892_p001

These are successes by every signal this runner has: a 200, no error, both files on disk, and `is_complete` will skip them on every later run. **Look at the images before reading anything into the number.** A blank verso or an envelope flap is genuinely empty, and knowing how many the corpus holds is worth having before extrapolating a cost per page. A *written* page that comes back empty is a defect no other column here would ever show — the segmenter found no lines on it (gateway), or the model answered the page with nothing at all (external reader). The second is a reading the prompt refused, not a page the model could not fetch: compare the same pages under another prompt before concluding anything about the corpus.

## Readings

427 page(s) per model — too many to put in one file. The transcriptions are in `/home/dh/agentic_historian/agentic_historian/data/vlm_test/aarau-fraktur-gemini-v1`, one `.txt` per page per model.
