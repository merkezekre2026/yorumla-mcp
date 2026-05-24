# Yorumla MCP

Turkish AI shopping decision engine for Hepsiburada review analysis. The primary interface is a Render-deployable Streamable HTTP MCP server for Claude.

The server does not call OpenAI, Anthropic, Ollama, or another model API. Claude uses the MCP tools and reasons over structured outputs produced by deterministic Turkish review analysis.

## Features

- Hepsiburada product URL validation
- Playwright review scraping
- Turkish complaint and praise clustering
- Fake review scoring from heuristic signals
- Seller, shipping, packaging, return/refund risk analysis
- Purchase recommendation: `ALINIR`, `DİKKATLİ AL`, `UZAK DUR`
- Streamable HTTP MCP endpoint at `/mcp`
- Optional FastAPI REST endpoints and Next.js frontend
- Docker and Render-ready deployment

## Structure

```text
backend/     FastAPI, MCP endpoint, scraper, analysis, SQLite
frontend/    Optional Next.js 15 dashboard
render.yaml  Render web service blueprint
```

## Local Backend Setup

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
playwright install --with-deps chromium
PORT=8000 MCP_AUTH_TOKEN=change-me uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## MCP Usage

Endpoint:

```text
POST /mcp
```

Claude Code remote MCP config:

```bash
claude mcp add --transport http yorumla https://YOUR-SERVICE.onrender.com/mcp \
  --header "Authorization: Bearer YOUR_MCP_AUTH_TOKEN"
```

Anthropic Messages API MCP connector:

```json
{
  "type": "url",
  "url": "https://YOUR-SERVICE.onrender.com/mcp",
  "name": "yorumla",
  "authorization_token": "YOUR_MCP_AUTH_TOKEN"
}
```

Exposed tools:

- `analyze_product_reviews(url)`
- `get_fake_review_score(url)`
- `summarize_reviews(url)`
- `seller_risk_analysis(url)`

## REST API

Use `Authorization: Bearer <MCP_AUTH_TOKEN>` when `MCP_AUTH_TOKEN` is set to a value other than `change-me`.

```bash
curl -X POST http://localhost:8000/api/products/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer change-me" \
  -d '{"url":"https://www.hepsiburada.com/ornek-urun-pm-123"}'
```

Other endpoints:

- `GET /api/products/fake-score?url=...`
- `GET /api/products/summary?url=...`
- `GET /api/products/seller-risk?url=...`

## Local Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Open `http://localhost:3000`.

## Docker

```bash
docker compose up --build
```

Backend: `http://localhost:8000`
Frontend: `http://localhost:3000`

## Render Deployment

1. Push the repo to GitHub.
2. Create a Render Blueprint from `render.yaml`.
3. Set `MCP_AUTH_TOKEN` as a secret.
4. Add a persistent disk mounted at `/data` if SQLite cache should survive deploys.
5. Deploy.
6. Confirm `https://YOUR-SERVICE.onrender.com/health` returns `{"status":"ok"}`.
7. Add the MCP server to Claude using the remote HTTP command above.

Render requires web services to bind to `0.0.0.0:${PORT}`. The backend Docker entrypoint already does this and defaults to port `10000`.

## Example MCP Tool Result

```json
{
  "purchase_recommendation": "DİKKATLİ AL",
  "fake_review": {
    "fake_review_score": 42,
    "risk_level": "MEDIUM"
  },
  "seller_risk": {
    "risk_score": 35,
    "risk_level": "LOW"
  },
  "summary": "Genel yorum profili mixed. Öne çıkan olumlu başlıklar: Kalite, Hızlı teslimat. Öne çıkan risk/şikayet başlıkları: Kargo ve teslimat. Sahte yorum risk skoru 42/100. Sonuç: DİKKATLİ AL."
}
```

## Production Notes

- Scraping is best-effort. The service does not bypass CAPTCHA, login walls, or anti-bot protections.
- SQLite is acceptable for MVP cache/storage. Use a Render persistent disk for durability.
- Move to Postgres when multiple instances or stronger durability are needed.
- Keep `MCP_AUTH_TOKEN` private.
- Monitor scraper errors because Hepsiburada DOM changes can break selectors.
