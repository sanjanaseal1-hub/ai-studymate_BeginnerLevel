# AI StudyMate

An AI-powered study utility that turns study material into summaries, quizzes, explanations and better-written answers.

## 1. Project overview
AI StudyMate is a React + FastAPI web app. The student picks one of four task-specific tools, enters text, and the backend sends it to Google Gemini using a **structured prompt** designed for that task. The result is shown as formatted headings, lists and bold text. It is a **task-based study utility, not a chatbot**: there is no free-form conversation, only defined workflows.

## 2. Problem statement
Students spend time re-reading long notes, writing practice questions, and struggling with unclear concepts or rough answers. General chatbots need good prompting skills to give consistent results.

## 3. Objective
Provide a simple, reliable tool where prompt design is built in, so the student only supplies content and gets consistent, study-ready output.

## 4. Features
| Tool | Input | Output |
|---|---|---|
| Summarize Notes | Lecture notes | Topic, Key Concepts, Important Points, Quick Revision |
| Generate Quiz | Notes + optional count (1-10), difficulty, topic | MCQs with 4 options, correct answer, explanation |
| Explain Concept | Concept/question + level | Definition, step-by-step, example, key points, revision |
| Improve Answer | Student's answer + optional subject | Improved answer + list of what changed |

Also: input validation (frontend and backend), loading state, friendly errors, copy-to-clipboard, responsive layout.

## 5. Technology stack
- **Frontend:** React 18, Vite, react-markdown, plain CSS (responsive)
- **Backend:** Python, FastAPI, Pydantic, httpx
- **AI:** Google Gemini API (REST), behind a replaceable `LLMClient` interface
- **Tests:** pytest (backend), Vitest + Testing Library (frontend)

## 6. System architecture
```
User
 ↓
React Frontend  (validation, loading state, formatted output)
 ↓  POST /api/<utility>  {content, options}
FastAPI Backend (Pydantic validation, error handlers)
 ↓
Structured Prompt  (prompts/templates.py)
 ↓
LLMClient → Gemini API   (API key read from .env, server side only)
 ↓
AI Response → checked (empty? malformed? blocked?)
 ↓
FastAPI → {"success": true, "result": "..."}
 ↓
React UI → Formatted Result
```
The frontend never sees the API key; routes only orchestrate; prompts are separate from API code; `llm_client.py` is the only file that knows Gemini exists.

## 7. Application workflow
1. Choose a tool → 2. Enter content → 3. Set options → 4. Click Generate → 5. Loading message shown, button disabled → 6. Read formatted result → 7. "Start another task".

## 8. Prompt engineering approach
A bare prompt like *"Summarize this."* gives output that varies in length and format, may add facts, and ignores what the student needs. Every StudyMate prompt instead has:

```
Role            (system instruction: educational assistant for college students)
+ Task          (exactly one job)
+ Input         (student text wrapped in <student_input> tags)
+ Constraints   (use only the material, no invented facts, simple language)
+ Output format (fixed Markdown sections)
```
This gives:
- **Relevant** output: task and constraints keep the model on the student's material.
- **Consistent** output: a fixed format means the UI renders it the same way every time.
- **Understandable** output: language level and structure are specified.
- **Task-specific** output: each utility has its own template (`SUMMARIZE_`, `QUIZ_`, `EXPLAIN_`, `IMPROVE_TEMPLATE`).

Extra choices: low temperature (0.4) for consistency; the input is delimited and the role says to treat it as data, a basic defence against prompt injection hidden in pasted text.

## 9. API integration
`backend/services/llm_client.py` defines an abstract `LLMClient.generate(system_instruction, prompt)`. `GeminiClient` implements it with `httpx` against Gemini's `generateContent` endpoint (role as `system_instruction`, task prompt as the user message; key in the `x-goog-api-key` header). To change provider, add another subclass and edit `get_llm_client()`. The app always calls the real API; fake clients exist only inside the test suite.

Endpoints: `POST /api/summarize`, `/api/quiz`, `/api/explain`, `/api/improve-answer`, `GET /api/health`.
Request: `{"content": "...", "options": {...}}` · Success: `{"success": true, "result": "..."}` · Error: `{"success": false, "error": "..."}`

## 10. Input validation
| Check | Frontend | Backend |
|---|---|---|
| Empty / whitespace only | ✔ | ✔ (422) |
| Longer than 8000 chars | ✔ | ✔ (422) |
| Quiz count not 1-10 | ✔ | ✔ (422) |
| Invalid difficulty / level | ✔ (select) | ✔ (Literal types) |
| Missing `content` | n/a | ✔ (422) |

The backend validates because anyone can call the API without the UI. Pydantic errors are converted into one friendly message.

## 11. Error handling
| Situation | HTTP | User sees |
|---|---|---|
| Invalid/missing API key | 500 | "The AI service is not configured correctly…" |
| Rate limit | 429 | "Too many requests right now…" |
| API down (5xx) | 503 | "The AI service is temporarily unavailable…" |
| Timeout (45 s) | 504 | "The AI took too long to respond…" |
| Network error | 502 | "Could not reach the AI service…" |
| Malformed / empty AI response | 502 | "Unable to generate the response right now…" |
| Safety-blocked content | 422 | "The AI could not process this content…" |
| Any other bug | 500 | "Something went wrong on our side…" |

Every AI failure becomes an `LLMError` with a safe `user_message` and a private `log_detail`. Only the first is returned; the second goes to the server log. Stack traces and keys never reach the client.

## 12. Security considerations
- API key only in `.env` (git-ignored); `.env.example` holds a placeholder.
- Key sent in a header, never in a URL; httpx request logging is turned down so it cannot leak.
- CORS limited to configured origins.
- All input validated on the backend; unexpected exceptions return a generic message.
- react-markdown does not render raw HTML from the AI response.

## 13. Installation and environment setup
Requirements: Python 3.10+, Node 18+, a Gemini API key (https://aistudio.google.com/apikey).
```bash
cp .env.example .env        # then edit .env and paste your key
```
## 14. Running the backend
```bash
cd backend
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
## 15. Running the frontend (second terminal)
```bash
cd frontend
npm install
npm run dev          # open http://localhost:5173
```
For deployment set `VITE_API_URL` to the backend URL at build time and add the site URL to `ALLOWED_ORIGINS`.

## 16. Example usage
- *Summarize:* paste a photosynthesis paragraph → Topic / Key Concepts / Important Points / Quick Revision.
- *Quiz:* same notes, 3 questions, hard → three MCQs with options A-D, correct answer, explanation.
- *Explain:* "What is a binary search tree?" (beginner) → definition, numbered steps, example, key points.
- *Improve:* "photosynthesis is when plant eat sun and make food" → clear grammatical answer plus notes on changes.

## 17. Project structure
```
ai-studymate/
├── backend/
│   ├── main.py                  app, CORS, error handlers
│   ├── routes/study.py          4 endpoints
│   ├── services/llm_client.py   LLMClient, GeminiClient, error mapping
│   ├── prompts/templates.py     4 structured prompts
│   ├── models/schemas.py        Pydantic validation
│   ├── utils/                   config.py, errors.py
│   └── tests/test_api.py
├── frontend/src/
│   ├── App.jsx                  state and flow
│   ├── utilities.js             config for the 4 tools
│   ├── components/              UtilityCards, StudyForm, ResultView
│   ├── services/api.js          backend calls
│   ├── utils/validation.js
│   └── App.test.jsx
└── .env.example  .gitignore  README.md  TESTING.md  INTERVIEW_GUIDE.md
```

## 18. Testing
See [TESTING.md](TESTING.md): `cd backend && pytest` and `cd frontend && npm test`.

## 19. Future improvements
PDF/image upload, scored interactive quizzes, history of results, user accounts, streaming responses, per-user rate limiting, flashcard export.
