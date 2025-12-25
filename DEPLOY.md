# 🚀 FitBot API - Render Deployment Checklist

## ✅ Pre-Deployment Checklist

- [ ] Code is working locally
- [ ] `.env` file is in `.gitignore` (don't commit secrets!)
- [ ] `GROQ_API_KEY` is ready
- [ ] All dependencies are in `requirements.txt`
- [ ] `render.yaml` is configured
- [ ] README.md is updated

## 📦 GitHub Setup

1. **Initialize Git (if not already done):**
   ```bash
   git init
   ```

2. **Add all files:**
   ```bash
   git add .
   ```

3. **Commit:**
   ```bash
   git commit -m "FitBot API ready for deployment"
   ```

4. **Create GitHub repository:**
   - Go to https://github.com/new
   - Create a new repository (e.g., `fitbot-api`)
   - Don't initialize with README (we already have one)

5. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/fitbot-api.git
   git branch -M main
   git push -u origin main
   ```

## 🌐 Render Deployment

### Option 1: Blueprint (Recommended)

1. Go to https://dashboard.render.com/
2. Click **New +** → **Blueprint**
3. Connect your GitHub repository
4. Render will detect `render.yaml`
5. Add environment variable:
   - Key: `GROQ_API_KEY`
   - Value: `your_actual_groq_api_key`
6. Click **Apply**
7. Wait for deployment (5-10 minutes)

### Option 2: Manual Web Service

1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Connect your repository
4. Configure:
   - **Name:** `fitbot-api`
   - **Environment:** Python 3
   - **Build Command:**
     ```
     apt-get update && apt-get install -y ffmpeg portaudio19-dev && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```
     sh start.sh
     ```
5. Add environment variable: `GROQ_API_KEY`
6. Click **Create Web Service**

## 🧪 Post-Deployment Testing

Once deployed, test these endpoints:

1. **Health Check:**
   ```bash
   curl https://your-app.onrender.com/health
   ```

2. **API Info:**
   ```bash
   curl https://your-app.onrender.com/
   ```

3. **Chat Test:**
   ```bash
   curl -X POST "https://your-app.onrender.com/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hi", "user_id": "test", "chat_history": []}'
   ```

4. **Interactive Docs:**
   - Open: `https://your-app.onrender.com/docs`

## 📝 Your API URL

After deployment, your API will be available at:
```
https://fitbot-api.onrender.com
```

Save this URL - you'll need it for frontend integration!

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify FFmpeg installation command is correct
- Ensure all dependencies are in `requirements.txt`

### App Crashes on Startup
- Check `GROQ_API_KEY` is set correctly
- View logs in Render dashboard
- Verify start command: `sh start.sh`

### 502 Bad Gateway
- Wait a few minutes (app might be starting)
- Check health endpoint: `/health`
- Review application logs

## ✨ Success!

If all tests pass, your FitBot API is live! 🎉

**Next Steps:**
1. Share your API URL
2. Build or deploy a frontend
3. Test with real users
4. Monitor usage in Groq Console

---

**Need help?** Check the logs in Render dashboard or review README.md
