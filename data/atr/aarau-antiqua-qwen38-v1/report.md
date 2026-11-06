# ATR batch — aarau-antiqua-qwen38-v1

- pages: **395**
- started: 2026-11-06T13:09:08+00:00
- wall time: 452.6 min

| model | read | skipped | failed | empty | looped | arguing | cut off | chars/page | s/page | wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `qwen3.8-27b` | 395 | 0 | 0 | 9 | 0 | 0 | 12 | 2178 | 68.7 | 452.6 min |

**These columns are not quality.** There is no ground truth in this run, and characters per page measures how much a model wrote, not how much of it is right — a model that hallucinates fluently leads this table. Comparing the readings is the point; the numbers only say what each run cost and whether it completed. Measuring accuracy needs transcribed lines and `eval/linebench.py`.

## Readings that were cut off

- `qwen3.8-27b`: 12 of 395 page(s)
  - 1896_p037
  - 1896_p084
  - 1896_p196
  - 1899_p049
  - 1899_p050
  - 1899_p051
  - 1899_p064
  - 1899_p077
  - 1899_p087
  - 1899_p111
  - 1899_p119
  - 1899_p196

These pages hit the model's token ceiling and stop mid-text. The request succeeded and the text is real — there is just less of it than the page has, and it reads like a model that gave up rather than one that was interrupted. Raise the ceiling — `ATR_VLLM_MAX_NEW_TOKENS` on the gateway, `GEMINI_MAX_TOKENS` for an external reader — delete the affected results and re-run: the batch re-reads only what is missing. A reasoning model spends the same ceiling on thinking before it writes a character, so lowering the thinking level buys page as surely as raising the ceiling does (#611) — check the thinking level before buying tokens.

## Pages that came back empty

- `qwen3.8-27b`: 9 of 395 page(s) (2%)
  - 1896_p037
  - 1899_p049
  - 1899_p050
  - 1899_p051
  - 1899_p077
  - 1899_p087
  - 1899_p111
  - 1899_p119
  - 1899_p196

These are successes by every signal this runner has: a 200, no error, both files on disk, and `is_complete` will skip them on every later run. **Look at the images before reading anything into the number.** A blank verso or an envelope flap is genuinely empty, and knowing how many the corpus holds is worth having before extrapolating a cost per page. A *written* page that comes back empty is a defect no other column here would ever show — the segmenter found no lines on it (gateway), or the model answered the page with nothing at all (external reader). The second is a reading the prompt refused, not a page the model could not fetch: compare the same pages under another prompt before concluding anything about the corpus.

## Readings

395 page(s) per model — too many to put in one file. The transcriptions are in `/home/dh/agentic_historian/agentic_historian/data/vlm_test/aarau-antiqua-qwen38-v1`, one `.txt` per page per model.
