# Frontend

React, TypeScript, and Vite dashboard for the PM Internship Scheme Smart Allocation Engine.

## Run locally

Start the FastAPI backend first from `../backend` using the commands in the repository root README. Then run:

```powershell
npm ci
npm run dev
```

The Vite server prints the local dashboard URL, usually `http://localhost:5173`.

## API configuration

The API client defaults to `http://127.0.0.1:8000`, where the FastAPI backend listens by default. To use another URL, copy `.env.example` to `.env.local` and set `VITE_API_URL`.

The frontend API types and requests are in `src/lib/api.ts`; the Vite development proxy is configured in `vite.config.ts`.
