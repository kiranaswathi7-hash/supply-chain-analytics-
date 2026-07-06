# Deployment Guide

## Important Note About Vercel Deployment

**Streamlit applications cannot be deployed directly to Vercel's serverless platform** because Streamlit requires a persistent server process with WebSocket support, which Vercel's serverless functions don't provide.

## Recommended Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free)

**Easiest and most reliable option for Streamlit apps.**

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub repository
5. Select this project
6. Click "Deploy"

**Requirements:**
- `app.py` in the root directory ✓
- `requirements.txt` with all dependencies ✓
- All data files in the repository ✓

### Option 2: Docker + Vercel (Advanced)

**Requires Vercel Pro plan for Docker deployment.**

1. Ensure you have the following files:
   - `Dockerfile` ✓
   - `vercel.json` ✓
   - `.dockerignore` ✓

2. Deploy to Vercel:
   ```bash
   vercel --prod
   ```

**Note:** This requires a Vercel Pro account for Docker support.

### Option 3: Railway, Render, or Heroku

**Alternative container platforms that support Streamlit.**

#### Railway
```bash
railway login
railway init
railway up
```

#### Render
- Connect your GitHub repository to Render
- Select "Web Service"
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

#### Heroku
```bash
heroku create your-app-name
heroku buildpacks:set heroku/python
git push heroku main
```

Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Option 4: Self-Hosted (VPS/Dedicated Server)

**Full control over the deployment environment.**

```bash
# On your server
git clone your-repo
cd python-streamlit-project
pip install -r requirements.txt
streamlit run app.py --server.port=8501
```

## Fixing the "Top-Level App Variable" Error

The error "found app.py but it does not export a top-level 'app' 'application' or handler variable" occurs because some deployment platforms expect a WSGI application (like Flask/Django), but Streamlit uses its own server.

**This is already fixed in app.py:**
```python
# Top-level app variable for deployment compatibility
app = st
application = st
```

## Current Deployment Files

Your project now includes:

1. **Dockerfile** - Container configuration for any Docker-compatible platform
2. **vercel.json** - Vercel configuration (requires Pro plan for Docker)
3. **server.py** - Entry point script for deployment
4. **.dockerignore** - Files to exclude from Docker image
5. **app.py** - Main application with top-level app variables

## Quick Start for Streamlit Cloud

1. Ensure all files are committed to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository
5. Deploy

That's it! Streamlit Cloud will automatically:
- Install dependencies from requirements.txt
- Run the Streamlit server
- Provide a public URL
- Handle SSL certificates
- Manage scaling

## Troubleshooting

### If deployment fails on Streamlit Cloud:
- Check that `requirements.txt` includes all dependencies
- Ensure all CSV files are in the repository
- Verify `app.py` is in the root directory
- Check the deployment logs for specific errors

### If using Docker:
- Test locally first: `docker build -t streamlit-app . && docker run -p 8501:8501 streamlit-app`
- Ensure Dockerfile has correct Python version
- Check that all required files are copied in Dockerfile

### If data files are missing:
- Ensure CSV files are committed to Git
- Check file paths in `data_loader.py`
- Verify `csv files/` directory structure

## Recommendation

**Use Streamlit Cloud** for the easiest and most reliable deployment. It's free, designed specifically for Streamlit, and requires minimal configuration.

If you must use Vercel, you'll need:
- Vercel Pro account (for Docker support)
- The Dockerfile and vercel.json provided
- Understanding that this is more complex than Streamlit Cloud
