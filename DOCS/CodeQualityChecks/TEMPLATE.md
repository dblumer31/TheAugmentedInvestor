# Code Quality Assessment

**Story / Scope:** [e.g., US-XXX or module name]  
**Date:** [YYYY-MM-DD]  
**Assessor:** [name or "AI"]

---

## 1. Complexity Analysis Summary

Brief overview of tools used and overall result (e.g., Radon for Python, ESLint for JS).

- **Tool(s):** 
- **Scope:** [files or modules assessed]
- **Overall finding:** [Pass / Review needed / Fail]

---

## 2. Function-by-Function Assessment

| Location (file:function) | Complexity (grade/score) | Maintainability (grade/score) | Notes |
|--------------------------|--------------------------|-------------------------------|-------|
| example.py:parse_file    | B (5)                    | A (85)                        | OK    |
| example.py:validate_row  | C (12)                   | B (65)                        | Flag if >10 |
| ...                      | ...                      | ...                           | ...   |

- **Complexity grading (typical):** A (1–5), B (6–10), C (11–20), D (21–30), E (31–40), F (41+).  
- **Maintainability (e.g. Radon):** A (20–100), B (10–19), C (0–9).  
- **Policy:** No Grade C+ complexity (C, D, E, F) introduced without justification. Flag any function with complexity > 10.

---

## 3. Grading Scale Reference

- **Cyclomatic complexity (e.g. Radon):** A = 1–5, B = 6–10, C = 11–20, D = 21–30, E = 31–40, F = 41+.  
- **Maintainability index:** A = 20–100, B = 10–19, C = 0–9 (lower is worse).  
- **Action threshold:** Complexity > 10 or grade C+ → document justification or refactor.

---

## 4. Action Items

| Item | Priority | Owner | Status |
|------|----------|--------|--------|
| [e.g., Refactor `validate_row` to reduce complexity] | High / Medium / Low | [TBD] | Open / Done |
| ... | ... | ... | ... |

---

## 5. Notes

Any justification for C+ complexity, one-off exceptions, or follow-up checks.
