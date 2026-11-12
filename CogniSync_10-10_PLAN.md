# CogniSync — 10/10 Project Makeover Plan

**Status:** Critique → Rework spec (lean MVP first)
**Source:** `Downloads/CogniSync_PRD_v1.0.md` + extracted dataset zip
**Verdict on v1.0:** Solid spec, 6.5/10. Over-scoped, data gap unaddressed, core signal chain unproven.

---

## 1. The one-line fix
**Do not build what's in v1.0 as written.** Narrow to the core loop (predict → recommend → confirm), prove the recommendation works with real student data, then add the integrations (wearables, commute, summarization) in later phases.

---

## 2. What to cut from MVP (Phase 1)
| Cut | Reason |
|---|---|
| Google Health / wearable integration | Highest-risk integration; least impact on core promise; data unavailable anyway |
| Android commute companion + Maps API | Risky (battery, permissions, billing), peripheral to "predict when to study" |
| PDF OCR / scanned PDF fallback | Shadows the core loop; add when docs become the primary input |
| LLM summarization | Adds LLM cost + hallucination risk; not needed for the core promise |
| What-if simulator | Nice-to-have, not a launch driver |
| Mood/stress fields | Already excluded — keep excluded |
| Trends dashboard (FR-DASH-08) | Post-MVP |

---

## 3. MVP scope (weeks 1–2): the core loop
### 3.1 Must-have features
- **Auth & isolation** — register/login; every student-owned record carries ownership; no cross-student data access.
- **Dashboard** — current study-effectiveness estimate with uncertainty/data-coverage indicator; best upcoming study windows; upcoming classes/exams/deadlines from a simple timetable.
- **Study session capture** — in-app event recording (PDF open, summary, quiz start/finish); group into candidate sessions with inactivity rule; small confirm prompt (subject, duration, focus/difficulty optional).
- **Quiz generation** — from a selected topic/PDF; record attempts, scores, and link to the correct session.
- **Prediction & recommendation** — Model B output (effectiveness proxy + uncertainty); ranked feasible windows; fallback to simple baseline when data sparse.

### 3.2 Non-negotiable acceptance criteria
- Student can predict their current effectiveness with an explicit `insufficient-data` state.
- Recommendation engine never schedules over a confirmed class/exam/deadline.
- Quiz scores attach to the correct session/subject/material — never to "latest session".
- Mood/stress absent from UI, DB schema, and model features.
- Basic time-of-day baseline works even with zero personal data.
- Self-hostable on a single machine; all external API calls have timeouts + rate limits + retry.

---

## 4. Data strategy — what actually builds the moat
| Need | Source | Status |
|---|---|---|
| Initial research | Zip datasets (OULAD, Duolingo, Kaggle lifestyle, SciQ) | ✅ Use for feature exploration only, not for the predictor |
| Student study-performance labels | **Consented pilot cohort** | 🔴 Must collect first |
| Health signals (optional) | Student's own wearables | 🔴 Opt-in, later phase |
| Academic schedule | PDF upload + student review | 🔴 Later phase |

**Rule:** no personal model calibration until ≥N observations (define N, e.g. 10 sessions) per student.

---

## 5. What to keep as Phase 2 (after pilot validation)
- Google Health OAuth (server-side, minimal scopes, 7-day testing-limit documented)
- Android commute companion (geofences + Maps routes API, caching + quota alerts)
- AI summarization (grounded in uploaded content, source/page references)
- Trends dashboard, what-if simulator, model explainability panels

---

## 6. Validation protocol (required before shipping)
1. **Baseline comparison** — always beat: (a) time-of-day heuristic, (b) soonest-free-slot heuristic.
2. **Time-aware splits** — by user, by time period; no random row leakage.
3. **Calibration & uncertainty** — report when data is sparse; don't overstate.
4. **Pilot study** — 20–30 students, ≥2 weeks, measure: prediction error, recommendation act-on rate, session confirmation rate, drop-off points.
5. **Decision gate** — if the model can't beat the simple baseline in the pilot, ship the baseline. Period.

---

## 7. Success metrics (measure, don't claim)
| Area | Metric |
|---|---|
| Adoption | % completing onboarding; % using the app ≥3 days |
| Prediction | MAE/RMSE vs. quiz-score proxy; calibration error |
| Recommendations | % of students who start studying within 24h of a recommendation |
| Data quality | sync rate; extraction correction rate; session-confirmation rate |
| Retention | weekly active users; % returning after first recommendation |

**Rule:** measure what students *do*, not what the model says.

---

## 8. Phased delivery
| Phase | Scope | Exit condition |
|---|---|---|
| **0 (pre-build)** | Configure Google Cloud + Maps + Android SDK (read-only audit of limits/caps); design consent flow; recruit pilot cohort | Docs + pilot roster |
| **1 (MVP)** | Dashboard, auth, session confirm, quiz, prediction + recommendations, baseline model | Manual demo with 1 student working end-to-end |
| **2 (pilot)** | Onboard 20–30 students; collect consented data; iterate model | Model beats simple baseline; students act on recommendations |
| **3 (integrations)** | Wearables, commute, OCR, summarization | Each integration isolated behind its own service; graceful fallback to no-wearable/no-commute |
| **4 (hardening)** | Scale, audit, retention, metrics, team enablement | Acceptance criteria in PRD v1.0 SS.6 met; pilot measured |

---

## 9. One-sentence promise (rewritten for v1.1)
“CogniSync recommends when you should study next and how effective it will likely be, using your schedule, learning history and — if you choose — your recovery signals.”

**Excluded from all versions:** mood, stress, medical claims, guaranteed grades, iOS, chatbot, mandatory wearables, mandatory commute tracking, raw GPS logs.
