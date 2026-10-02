# Testing

## Automated
```bash
cd backend && pytest          # 21 tests, no API key or network needed
cd frontend && npm test       # 5 tests
```
| Area | Covered |
|---|---|
| Backend: valid request | all 4 endpoints return `success: true`; input appears in the prompt |
| Backend: empty / invalid | empty, whitespace, >8000 chars, missing field, bad options → 422, LLM never called |
| Backend: API failure | 429/503/504/502 return friendly JSON; unexpected exception hides details |
| Backend: malformed AI response | missing candidates, empty text, non-object, safety block; HTTP status mapping |
| Frontend: empty input | message shown, API not called |
| Frontend: valid input | API called with correct endpoint/body, result rendered as headings |
| Frontend: loading | message shown, button disabled until response |
| Frontend: API error | friendly message shown, user's text kept |

Backend tests replace the LLM with a fake client via a FastAPI dependency override (tests only).

## Manual checklist (needs a real GEMINI_API_KEY)
- [ ] Summarize: ~200 words → 4 sections, no invented facts.
- [ ] Quiz: 3 questions, hard, topic set → 3 MCQs with A-D, answer, explanation.
- [ ] Explain: "What is recursion?" at beginner and advanced → different depth, both with an example.
- [ ] Improve: weak answer → meaning kept, "What Was Improved" list present.
- [ ] Empty text → "Please enter some study material first."
- [ ] 9000 characters → too-long message.
- [ ] Wrong key in `.env` → "not configured correctly" (key never shown).
- [ ] Stop the backend → "Cannot reach the server…".
- [ ] 360px wide browser → layout stays usable.
