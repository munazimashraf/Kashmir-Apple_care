# Deployment Guide: Vercel & Cloud Backend

This guide outlines how to deploy **AppleCare Kashmir** to [Vercel](https://vercel.com) (Frontend) and [Render](https://render.com) / [Railway](https://railway.app) (FastAPI Backend).

---

## 1. Quick Deploy to Vercel (Frontend SPA)

Since AppleCare Kashmir is built with **Vite**, it deploys to Vercel with zero configuration.

### Steps:
1. Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
2. Click **"Add New..."** → **"Project"**.
3. Import your GitHub repository: `munazimashraf/Kashmir-Apple_care`.
4. Vercel automatically detects the configuration from `vercel.json`:
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
5. Click **"Deploy"**.
6. Within 30 seconds, your site will be live at:
   `https://kashmir-apple-care.vercel.app`

> **Note**: The frontend is fully functional on Vercel even without an external backend because it includes built-in client-side fallbacks:
> - 7-Day Spray Window Forecast (connects directly to Open-Meteo live API)
> - SKUAST-K Kashmir 8-Stage Spray Calendar & Compatibility Matrix
> - Interactive Orchard Tank Mixture Calculator
> - 19 Licensed Kashmir Pesticide Dealers with GPS proximity navigation
> - SKUAST-K Expert Helplines & 24/7 AI Agronomist consultation
> - Direct "Buy Online" links to BigHaat, IFFCO, AgroStar, and IndiaMart

---

## 2. Deploy the FastAPI AI Backend (Free on Render)

To enable server-side deep learning inference (PyTorch / ONNX model predictions):

### Steps on Render:
1. Go to [render.com](https://render.com) and sign up/log in with GitHub.
2. Click **"New +"** → **"Web Service"**.
3. Connect your repository: `munazimashraf/Kashmir-Apple_care`.
4. Configure the service:
   - **Name**: `applecare-backend`
   - **Region**: Singapore or Frankfurt (lowest latency to India/Kashmir)
   - **Runtime**: `Python` (or `Docker`)
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt
     ```
   - **Start Command**:
     ```bash
     PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
5. Click **"Create Web Service"**.
6. Render will provide a free URL, for example:
   `https://applecare-backend.onrender.com`

---

## 3. Connect Vercel Frontend to Render Backend (Zero CORS)

To let your Vercel frontend seamlessly call your Render backend without CORS issues, add a rewrite rule in `vercel.json`:

```json
{
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://applecare-backend.onrender.com/api/:path*"
    }
  ]
}
```

Whenever you push to GitHub:
```bash
git add vercel.json
git commit -m "chore: configure Vercel API proxy to Render backend"
git push origin main
```
Vercel will automatically re-deploy and forward all `/api/v1/...` requests to your live backend!

---

## 4. Alternative: Deploy Backend via Docker (Railway / Fly.io / DigitalOcean)

The repository includes a production-ready `backend/Dockerfile`:

```bash
# Build locally or on any cloud container service
docker build -f backend/Dockerfile -t applecare-backend .
docker run -p 8000:8000 applecare-backend
```
