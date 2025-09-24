# Technical Test – Weather + Generative-AI Voice Chatbot

_Last updated: 24 Sep 2025_

---

## 1. Purpose
Demonstrate curiosity and ability to learn cutting-edge technology (e.g.
Generative AI) by building and showcasing a small, working product.

## 2. Assignment Overview
Build a chatbot that:
1. Accepts **Japanese voice input**.
2. Fetches **weather data** from a free public API.
3. Generates proposals/suggestions using a **Generative AI model**.

Theme is open (travel, fashion, sports, agriculture, etc.).

**Deadline:** Fri 26 Sep 2025, 20:00 IST

## 3. Functional Requirements
- **Voice Input (JP):** Transcribe spoken Japanese to text.
- **Weather Retrieval:** Query a public weather API (no cost preferred).
- **AI Suggestions:** Send user query + weather JSON to an LLM and return
  Japanese suggestions.
- **Chat UI:** Show a chat-style conversation in the browser.
- **(Optional) Voice Output:** Read AI reply aloud using Text-to-Speech.

## 4. Non-Functional Requirements
None specified → optimise for speed of delivery and free-tier hosting.

## 5. Deliverables
| # | Item | Notes |
|---|------|-------|
| 1 | **Working demo** | Public URL (Vercel) or short demo video |
| 2 | **Source code**  | GitHub repo link |

## 6. Proposed Tech Stack & Architecture
### 6.1 High-Level Diagram
```
Browser (React + Vite)
│  ├─ Speech-to-Text (Web Speech API, lang=ja-JP)
│  ├─ Chat UI  (Tailwind, shadcn/ui)
│  └─ Text-to-Speech (optional)
│
└── REST/GraphQL API (Express + Node.js)
    ├─ /weather   ──> Open-Meteo REST
    └─ /chat      ──> OpenAI gpt-3.5-turbo
        └─ MongoDB (store chat logs, user prefs)  
```
Separate **client** and **server** folders in the same repo; deploy frontend to Vercel/Netlify and backend to Render/Fly.io (or Heroku) on free tiers.

### 6.2 Key Choices
- **Frontend:** React 18 + Vite + TypeScript
- **Backend:** Node.js 20 + Express 4 + TypeScript (ts-node/dev)
- **Database:** MongoDB Atlas free tier (optional, for chat history)
- **Styling:** Tailwind CSS + shadcn/ui components
- **Speech-to-Text:** Browser `SpeechRecognition` (Chrome/Edge). Fallback: Whisper via backend
- **Weather API:** [Open-Meteo](https://open-meteo.com) (no key) or OpenWeatherMap
- **LLM:** OpenAI `gpt-3.5-turbo` (≈ $0.0005/msg)

## 7. User Flow (MVP)
1. User clicks mic → speaks in Japanese.
2. Browser STT returns text → append to chat.
3. Frontend calls `/api/weather` with coords (geolocation or hard-coded city).
4. Frontend sends JSON weather + user query to `/api/chat`.
5. Server calls OpenAI → returns suggestions.
6. UI displays reply; optional TTS speaks it.

## 8. Folder Structure Sketch
```
ChatAgent/
├─ client/                 # React + Vite
│   ├─ src/
│   │   ├─ App.jsx         # routes & chat UI
│   │   ├─ componenjs/
│   │   │   ├─ Chat.jsx
│   │   │   └─ useSpeech.js
│   │   └─ ...
│   └─ vite.config.js
├─ server/                 # Node + Express
│   ├─ src/
│   │   ├─ routes/
│   │   │   ├─ weather.js  # GET /weather
│   │   │   └─ chat.js     # POST /chat
│   │   ├─ services/
│   │   │   └─ openai.js
│   │   ├─ models/
│   │   │   └─ ChatLog.js  # (optional) Mongoose model
│   │   └─ index.js        # Express app entry
│   └─ jsconfig.json
├─ .env.example            # OPENAI_API_KEY, MONGODB_URI, etc.
└─ README.md / this file
```

## 9. Prompt Design (server-side)
```
system:
あなたは旅行プランナーのAIアシスタントです。以下のJSONの天気情報を
読み取り、ユーザーの要望に応じた提案を日本語で3つ出してください。
必ず箇条書きで。カジュアルな口調。

user:
{
  "weather": { … },
  "query": "週末に家族とピクニック行きたい"
}
```

## 10. Implementation Timeline (~8 hrs)
| Day | Time | Task |
|-----|------|------|
| 1 | 1 h | Scaffold Next.js repo, push to GitHub |
|   | 1 h | Implement `/api/weather` + test |
|   | 2 h | Build chat UI skeleton (Tailwind) |
|   | 1 h | Integrate Web Speech API |
| 2 | 1 h | Implement `/api/chat` with OpenAI SDK |
|   | 1 h | Chain weather → LLM → UI |
|   | 1 h | Polish UI, add (optional) TTS |
|   | 1 h | Record demo video & final deploy |

## 11. Cost Estimate
| Service | Cost |
|---------|------|
| Open-Meteo | Free |
| OpenAI gpt-3.5-turbo | ~ $0.005 per 10 demo chats |
| Vercel hobby | Free |

## 12. Submission Checklist ✓
- [ ] GitHub repo pushed & public
- [ ] `.env.example` committed (no real keys)
- [ ] Vercel URL or demo video link
- [ ] README with setup, run & deploy instructions

---
Feel free to update this file as the project evolves. 