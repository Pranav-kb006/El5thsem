# Cognisync — extra dataset suggestions
Source: `/home/bhandi/Downloads/cognisync_datasets.zip` (49 files, extracted at
`/home/bhandi/cognisync_datasets/cognisync_datasets/`). Manifest: `data/raw/MANIFEST.json`.

## What is already in the zip
| Folder | Contents | Role in project |
|---|---|---|
| `devaraj_simplification_factuality` | Human-factuality annotations on Newsela + WikiLarge (deletion/insertion/substitution) + system outputs from ACCESS/controlTS/Dress/editNTS/t5_vanilla | B2: factuality evaluation in text simplification. Note says "News/Wikipedia domain, not textbooks." |
| `oulad` | Open University Learning Analytics (studentInfo/assessments/studentVle/registration + OULAD.names) | B1 scores-only baselines; B3 calibration. |
| `kaggle_student_lifestyle` | 2,000 rows: study/sleep/social/activity hours, GPA, Stress_Level (24h check advised; synthetic risk) | A2 global prior only. |
| `duolingo_hlr` | settles.acl16.learning_traces.13m.csv.gz — p_recall, delta, user_id, lexeme, history_seen/correct | A2 retention: p_recall after delta seconds (delayed recall). |
| `sciq` | 13.7K crowdsourced science MCQs with support paragraphs (train/val/test) | A4 quiz/RAG testing. |
| `nli_model` | `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` (safetensors only) | B2: NLI factuality model, used as-is. |

The naming pattern (B1/B2/B3, A2/A4, "global prior", "calibration") is the
project's own, so "relevant" here means: datasets that plug into the same
task slots — simplification + factuality, student retention/performance,
science QA/RAG, language-learning traces.

## Suggested additions (pick by gap)
### 1. Simplification training corpora (complement devaraj's news/Wikipedia data)
- **WikiLarge** (Zhang & Lapata, EMNLP 2017) — 296K parallel English↔Simple
  English Wikipedia sentence pairs; the standard training corpus for
  simplification. HF mirrors: `waboucaywaboucay/wikilarge`,
  `an-atlas/wikilarge`. License: none stated on original paper (mirror repos
  vary — prefer the GitHub `zhangHongbo/WikiDocument` release or
  `https://github.com/...` if you want a clean copy).
- **OneStopEnglish** (Vajjala & Lučić, BEA 2018) — 189 Guardian articles
  rewritten at 3 levels (elementary/intermediate/advanced = 567 aligned
  texts). Best fit for the project's A2/B2-level scheme; CC BY-SA 4.0;
  GitHub `nishkalavallabhi/OneStopEnglishCorpus`, Zenodo 1219041.
- **SimpleText / CLEF SimpleText** (Ermakova et al., 2024) — scientific
  abstracts (DBLP+PubMed) simplified by experts; STsent (1.6K) + STpara (271)
  with human simplicity ratings. Fills the "textbooks/scientific text,
  not news" gap the manifest already flags. CLEF track data, CC BY 4.0.
- **Simple English Wikipedia** dump (en.wikipedia.org/wiki/Simple_Wikipedia;
  CC BY-SA 4.0) — raw corpus for mining your own aligned pairs, cheap and big.

### 2. Factuality benchmarking (your DeBERTa-mnli model needs test data)
- **FRANK** (Pagnoni et al., 2021) — 2,250 summaries with human error-category
  judgments (semantic frame, discourse, content verifiability); the standard
  factuality benchmark for summarization/NLI-style models. arXiv:2104.13346.
- **FactCC** (Kryscinski et al., 2020) — synthetic consistency labels for
  sentence pairs; arXiv:1910.12807. Pairs well with your DeBERTa baseline.
- **QAGS** (Wang et al., 2020) — QA-based factual-consistency metric;
  arXiv:1910.05876.

### 3. Student retention / performance (OULAD is the anchor; second public
cohort for generalization)
- **UCI Student Performance** — math + PortugueseCSV grades for 385 students,
  33 attributes; classic benchmark. https://archive.ics.uci.edu/dataset/320/student+performance
  (UCI CC BY 4.0). Add this as a second, small institutional dataset to test
  whether retention models generalize beyond OU (OULAD).

### 4. Science QA / RAG (SciQ slot already filled)
- **AI2 ARC** — 7,787 grade-school science MCQs (Challenge/Easy splits +
  14M sentence support corpus). HF: `allenai/ai2_arc`.
- **OpenBookQA** — 5,957 MCQs + a "open book" fact sheet; multi-step
  reasoning. HF: `allenai/openbookqa`.
- **QASC** — 8,000 train / 9,000 test science MCQs requiring sentence
  composition. HF: `allenai/qasc`.

### 5. Language learning (Duolingo HLR slot)
- **International Corpus of Learner English (ICLEv2)** — 3.7M words, 16 L1
  backgrounds, advanced learner essays (Granger et al.). Restricted access
  (via Learner Corpus Research / authors).
- **Cambridge Learner Corpus** — 15M+ words, coded errors. Restricted
  (Cambridge University Press).

## Pick these first (4)
1. OneStopEnglish — directly matches the A2/B2 labelling scheme, small,
   free, CC BY-SA.
2. WikiLarge — core simplification training data; fills the "no training
   corpus" gap.
3. UCI Student Performance — cheap second institutional dataset for
   retention modelling.
4. AI2 ARC / OpenBookQA — direct SciQ complement for the QA/RAG slot.

## Notes
- Every new addition should be recorded in `data/raw/MANIFEST.json` with
  source URL, licence, SHA-256, and a note (mirror of the Phase-1 data-card
  requirement in `download_datasets.py`).
- "Relevant" here means: usable as (a) training data for simplification,
  (b) benchmark for factuality metrics against the DeBERTa NLI model, (c) a
  second retention cohort, or (d) a science-QA/RAG test set.
