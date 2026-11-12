# CogniSync — ML workstream

OULAD offline benchmark (PRD v1.2 models M1–M5) and plans for the CogniSync models (M6–M16). Fatigue (M17–M18) lives in a separate workstream.

## Layout

| Path | What |
|---|---|
| `src/ml/pipeline.py` | Point-in-time feature generation and the leakage test suite |
| `src/ml/oulad_benchmark.py` | Trains and evaluates M1–M5, writes the JSON results and the Markdown report |
| `docs/benchmarks/` | Evaluation protocol and benchmark reports |
| `docs/plans/` | Plans for next-quiz / delayed-retention models, personalisation and the recommender |
| `cognisync_datasets/download_datasets.py` | Downloads the raw datasets (not committed; see `.gitignore`) |

## Data

Put OULAD at `cognisync_datasets/data/raw/oulad/` (the layout of the team's dataset zip), or pass `--data-dir`. `studentVle.csv` is only needed for `--with-vle`.

## Run

```bash
pip install -r requirements.txt

# score history + metadata
python src/ml/oulad_benchmark.py --out-json docs/benchmarks/oulad_results.json --report docs/benchmarks/M5_OULAD_report.md

# same + VLE engagement features (the score-only vs. context-aware comparison)
python src/ml/oulad_benchmark.py --with-vle --out-json docs/benchmarks/oulad_results_vle.json --report docs/benchmarks/M5_OULAD_report_vle.md
```

Each run takes several minutes, mostly the leakage suite and the tree models. `--skip-leakage` makes a quick run; `--horizon-days N` changes how far before each deadline the prediction is made (default 7).

## Protocol in one paragraph

Each OULAD assessment attempt is predicted at a fixed point before its deadline, from that student's earlier submissions of *other* assessments only. The split is chronological by presentation (train 2013B+2013J, validate 2014B, test 2014J) with no student in more than one split. Every model is compared with historical-mean and last-score baselines. OULAD is a benchmark only: it says nothing directly about CogniSync quiz scores.
