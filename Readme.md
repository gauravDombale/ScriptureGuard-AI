# ScriptureGuard AI

Christianity-focused AI assistant with grounded KJV scripture citations, denomination-aware chat, guarded image generation, session memory, and a safety-first backend pipeline.

## Current Stack

- Backend: FastAPI, Python 3.11, OpenAI, Pinecone, Redis, PostgreSQL
- Frontend: Next.js 15, TypeScript, Tailwind CSS v4
- Runtime: Docker Compose with Redis and PostgreSQL

## Local Development

```bash
cp .env.example .env
docker compose up --build
```

Frontend: `http://localhost:3000`

Backend: `http://localhost:8000`

Health check:

```bash
curl http://localhost:8000/health
```

## Notes

- Keep `.env` local only.
- Use `POST /chat/stream` for streaming chat responses.
- Use `POST /image/generate` for guarded Christian image generation.
