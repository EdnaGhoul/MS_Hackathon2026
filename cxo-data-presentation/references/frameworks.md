# Framework layering

Load when the user asks "why", "which framework", contests a check, or wants the
structure justified. No single framework covers all four layers — layer by purpose.

## The four layers
| Layer | Framework | What it supplies | Limitation the skill compensates for |
|---|---|---|---|
| Argument structure | Minto Pyramid Principle | One governing thought, grouped supporting arguments; think bottom-up, communicate top-down. De facto standard in major consulting firms for memos, reports and decks. | Can make a contested recommendation look settled → UNC-01/02, OPT-01 force uncertainty and alternatives into view |
| Metric architecture | Balanced Scorecard (Kaplan & Norton, 1992; yearlong study with 12 companies) | Financial, customer, internal-process, learning-and-growth perspectives; leading drivers alongside lagging financials | Degenerates into four disconnected buckets without a strategy map / causal logic → KPI-01 requires each metric to name its decision |
| Visual encoding and notation | Cleveland–McGill (JASA 1984) + Heer & Bostock (CHI 2010) for perception; IBCS 2.0 and ISO 24896:2026 for notation consistency | Perceptual accuracy ordering; consistent notation across recurring reports | Notation standards do not say which decisions matter → DEC-01, KPI-01 |
| Alternatives, risk, uncertainty | Decision Quality (six links in a chain) and HM Treasury Green Book / Five Case Model | Framing, alternatives incl. BAU, information quality, values/trade-offs, reasoning, commitment; ranges, sensitivities, switching values, optimism bias | More rigour than routine communication needs → gated to S3 (OPT-02, decision-quality chain) |

## Supporting disciplines
| Discipline | Contribution | Where encoded |
|---|---|---|
| SEC Plain English Handbook (1998) | Audience-led organisation, big picture before detail, descriptive headings, active voice, concrete language; graphics drawn to scale, no distorting baselines, time left→right, no 3D, prune chartjunk | TTL-01, VIS-02, VIS-05, VIS-06, plain-language rules in the decision-paper playbook |
| UK Civil Service submission structure | Issue → recommendation → timing → background → argument; important decisions need a written submission, not a deck or email | Answer-first order; Route D for S3 |
| WCAG 2.2 SC 1.4.1 (Level A) | Colour never the sole means of conveying information; ≥3:1 contrast where lightness is the additional cue | VIS-04, `scripts/contrast_check.py` |
| NIST CSF 2.0 | High-level outcomes for prioritising and communicating security effort at executive level without prescribing controls | CIO/CTO/CDO lens framing |
| Porter & Nohria CEO time study | 27 CEOs tracked hourly for 13 weeks over 12 years; CEOs manage contradictory dualities under acute time scarcity | Governing rule: organise around the decision, allow depth on request |

## Why "design around the decision" is the spine
The Porter–Nohria evidence establishes the time constraint; Minto supplies the traversal;
Cleveland–McGill supplies the perceptual ordering; Decision Quality and the Green Book
supply the discipline for options, risk and commitment. A report that leaves any of
these to chance forfeits the specific advantage each documents.

## What is evidence and what is heuristic
| Claim | Standing |
|---|---|
| Position > length > angle for accuracy | Peer-reviewed experiment (definitive) |
| Colour not the sole cue; 3:1 contrast | Formal W3C standard (definitive) |
| ISO 24896:2026 notation | International standard (definitive) |
| Draw to scale; no 3D; chartjunk | Regulator handbook (definitive for its domain) |
| Balanced Scorecard, Minto | Strong foundational evidence / practitioner standard |
| QBR eight blocks, pre-wiring, all-green warning | Practitioner consensus |
| "Five slides", "seven KPIs", specific thresholds | Heuristics — never presented as findings |

The skill never reports a heuristic as a finding. Slide counts and KPI counts are not
checks.
