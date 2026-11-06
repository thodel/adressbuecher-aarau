# ATR batch — aarau-antiqua-qwen3vl30b-v1

- pages: **395**
- started: 2026-11-06T13:53:47+00:00
- wall time: 50.3 min

| model | read | skipped | failed | empty | looped | arguing | cut off | chars/page | s/page | wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `qwen3-vl-30b-a3b-instruct` | 395 | 0 | 0 | 0 | 2 | 0 | 11 | 2544 | 7.6 | 50.3 min |

**These columns are not quality.** There is no ground truth in this run, and characters per page measures how much a model wrote, not how much of it is right — a model that hallucinates fluently leads this table. Comparing the readings is the point; the numbers only say what each run cost and whether it completed. Measuring accuracy needs transcribed lines and `eval/linebench.py`.

## Readings that were cut off

- `qwen3-vl-30b-a3b-instruct`: 11 of 395 page(s)
  - 1896_p008
  - 1896_p014
  - 1896_p016
  - 1896_p017
  - 1896_p018
  - 1896_p019
  - 1896_p021
  - 1896_p206
  - 1899_p007
  - 1899_p170
  - 1899_p188

These pages hit the model's token ceiling and stop mid-text. The request succeeded and the text is real — there is just less of it than the page has, and it reads like a model that gave up rather than one that was interrupted. Raise the ceiling — `ATR_VLLM_MAX_NEW_TOKENS` on the gateway, `GEMINI_MAX_TOKENS` for an external reader — delete the affected results and re-run: the batch re-reads only what is missing. A reasoning model spends the same ceiling on thinking before it writes a character, so lowering the thinking level buys page as surely as raising the ceiling does (#611) — check the thinking level before buying tokens.

## Pages the model padded

- `qwen3-vl-30b-a3b-instruct`: 2 of 395 page(s) (1%)
  - 1899_p170
  - 1899_p188

A run of one character twenty long or half the lines repeating is not a reading of a page. **These carry text, so every average over them is wrong** — characters per page most of all. They are described, not removed: whether the page itself is a table, a ruled form or a scan the model could not hold on to is settled by looking at it.

## Readings

395 page(s) per model — too many to put in one file. The transcriptions are in `/home/dh/agentic_historian/agentic_historian/data/vlm_test/aarau-antiqua-qwen3vl30b-v1`, one `.txt` per page per model.
