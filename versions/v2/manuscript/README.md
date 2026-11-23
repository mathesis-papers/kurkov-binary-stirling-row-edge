# Kurkov's binary Stirling row edge

Haobo Ma (ChronoAI Pte Ltd, Singapore) and Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore). CC BY 4.0.

## Contents

- `note.tex`: complete proofs, source locators, coverage table and references.
- `verify.py`: exact rational and integer checks using Python 3's standard library.
- `verification.json`: the finite ranges and results.
- `metadata.json`: bibliographic information and statement coverage.

The note proves the full binary Stirling row edge and a rising-factorial identity connecting A358612 to A373183. Consequences include the signed factorial transform, the falling-factorial identity in MathOverflow 483753, lower-bit recurrences, a sharp excedance bound, and two corrected suffix identities. The ordinary suffix identity has range `0 <= q < 2^m`; the generalized initial-factorial identity in the note also requires `n > 0`. Counterexamples to the printed unrestricted assertions are included.

## Build

Use Tectonic 0.17.0:

```sh
tectonic --untrusted note.tex
python3 verify.py --output verification.json
```

Alternatively run `pdflatex note.tex` twice with the standard AMS, Latin Modern, geometry, booktabs, array, longtable and hyperref packages. The bibliography is included in the TeX source; no BibTeX database is required.

## Statement coverage

Every all-index conclusion has a written proof. The PDF links four Lean files pinned at commit `47f05ad67b37a0f7cbc4673c33bb17fb7c1e78fb` and identifies the exact declarations for the rational block, vanishing strictly above the edge, rational edge quotient, numerator binomial identity and three-term polynomial recurrence. Positivity below the edge, integrality, the complete rising-factorial connection, lower-bit formulas, corrected suffix ranges and sharp inequality are supplied by written proofs.

The checker compares the literal rational array and independent polynomial/excedance recurrences, including rows 0–4095. Its finite checks supplement, rather than replace, the all-index proofs. `verification.json` gives every additional parameter range and the two explicit counterexamples.

## Attribution

The title and abstract credit Ehrenborg–Steingrímsson (2000) for the excedance-product and inclusion–exclusion results, and Erlbacher (July 2026) for the binary prefix-product derivation. The normalized gap product and Boolean transform are presented as consequences of prior work. The precise primary-source conjectures and their proven, corrected or uncovered scope are tabulated in the note. No priority claim is made.

The source files are licensed CC BY 4.0. The cited third-party sources retain their own terms.
