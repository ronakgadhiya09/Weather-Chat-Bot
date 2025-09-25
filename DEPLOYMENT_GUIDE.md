# WeatherBot Deployment Guide 🚀

This guide provides multiple deployment options for your WeatherBot application with automated GitHub workflows.

## 📋 Prerequisites

- GitHub account
- Git repository with your WeatherBot code
- API keys for OpenAI, OpenWeather, and Groq
- Node.js 18+ and Python 3.11+ (for local development)

## 🎯 **Recommended Deployment Stack**

### Frontend: Vercel (Recommended)
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Perfect for React applications

### Backend: Railway (Recommended)
- ✅ Free tier available
- ✅ Automatic deployments
- ✅ Built-in monitoring
- ✅ Easy environment variable management

## 🚀 **Quick Deployment (Recommended)**

### Step 1: Setup GitHub Repository

1. **Push your code to GitHub**:
```bash
git add .
git commit -m "feat: add deployment configurations"
git push origin main
```

2. **Enable GitHub Actions** in your repository settings

### Step 2: Deploy Backend to Railway

1. **Sign up at [Railway.app](https://railway.app)**
2. **Connect your GitHub repository**
3. **Create a new project** and select your repository
4. **Add environment variables**:
   ```
   OPENAI_API_KEY=your_openai_key
   OPENWEATHER_API_KEY=your_openweather_key
   GROQ_API_KEY=your_groq_key
   ```
5. **Deploy** - Railway will automatically detect the Python backend

6. **Get your Railway URL** (e.g., `https://weatherbot-backend-production.up.railway.app`)

### Step 3: Deploy Frontend to Vercel

1. **Sign up at [Vercel.com](https://vercel.com)**
2. **Import your GitHub repository**
3. **Configure build settings**:
   - Framework Preset: `Create React App`
   - Build Command: `cd frontend && npm run build`
   - Output Directory: `frontend/build`
4. **Add environment variables**:
   ```
   REACT_APP_API_URL=https://your-railway-backend-url.up.railway.app
   ```
5. **Deploy** - Vercel will build and deploy automatically

### Step 4: Setup GitHub Secrets

Add these secrets to your GitHub repository (Settings > Secrets and Variables > Actions):

```
VERCEL_TOKEN=your_vercel_token
RAILWAY_TOKEN=your_railway_token
```

**Get Vercel Token**:
1. Go to [Vercel Account Settings](https://vercel.com/account/tokens)
2. Create new token
3. Copy and add to GitHub secrets

**Get Railway Token**:
1. Go to Railway Dashboard > Account Settings > Tokens
2. Create new token
3. Copy and add to GitHub secrets

## 🔄 **Automated Deployment Workflow**

The GitHub Action will automatically:

1. **Test** both frontend and backend
2. **Build** the applications
3. **Deploy** to Vercel and Railway
4. **Run Lighthouse** performance tests
5. **Notify** deployment status

**Trigger**: Every push to `main` branch

## 🛠 **Alternative Deployment Options**

### Option A: Netlify + Render

#### Deploy to Netlify (Frontend)
1. **Sign up at [Netlify.com](https://netlify.com)**
2. **Connect GitHub repository**
3. **Build settings**:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/build`
4. **Environment variables**:
   ```
   REACT_APP_API_URL=https://your-render-backend.onrender.com
   ```

#### Deploy to Render (Backend)
1. **Sign up at [Render.com](https://render.com)**
2. **Create new Web Service**
3. **Connect repository**
4. **Settings**:
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment variables**: Add your API keys

### Option B: Docker + Any Cloud Provider

#### Build and Run with Docker

```bash
# Build and run locally
docker-compose up --build

# Build for production
docker-compose --profile production up --build
```

#### Deploy to Cloud Providers

**DigitalOcean App Platform**:
1. Connect GitHub repository
2. Use the provided `docker-compose.yml`
3. Configure environment variables

**AWS ECS/Fargate**:
1. Push images to ECR
2. Create ECS service
3. Configure load balancer

**Google Cloud Run**:
1. Build images with Cloud Build
2. Deploy to Cloud Run
3. Configure domain and SSL

## 🔒 **Environment Variables Setup**

### Backend Environment Variables
```bash
OPENAI_API_KEY=sk-your-openai-key
OPENWEATHER_API_KEY=your-openweather-key
GROQ_API_KEY=gsk_your-groq-key
```

### Frontend Environment Variables
```bash
REACT_APP_API_URL=https://your-backend-url.com
```

## 🧪 **Testing Deployment**

### Local Testing
```bash
# Test frontend
cd frontend
npm test

# Test backend
cd backend
python -m pytest

# Test with Docker
docker-compose up
```

### Production Testing
1. **Frontend**: Visit your Vercel/Netlify URL
2. **Backend**: Check `/health` endpoint
3. **Integration**: Test chat functionality
4. **Voice Features**: Test microphone permissions
5. **Language Switching**: Test EN/JA toggle

## 📊 **Monitoring & Analytics**

### Built-in Monitoring
- **Vercel Analytics**: Automatic performance tracking
- **Railway Metrics**: Resource usage and uptime
- **GitHub Actions**: Deployment status and logs

### Lighthouse Performance
- **Automated testing** on every deployment
- **Performance budgets** enforced
- **Accessibility compliance** checked

## 🔧 **Troubleshooting**

### Common Issues

**Frontend Build Fails**:
```bash
# Fix dependencies
cd frontend
npm install
npm audit fix
```

**Backend Deployment Fails**:
```bash
# Check requirements
cd backend
pip install -r requirements.txt
python app/main.py
```

**CORS Issues**:
- Update CORS origins in `backend/app/main.py`
- Add your frontend domain to allowed origins

**Environment Variables Not Loading**:
- Check variable names (case-sensitive)
- Restart deployment after adding variables
- Verify secrets are properly set

### Debug Commands

```bash
# Check GitHub Actions logs
gh run list
gh run view [run-id]

# Check deployment status
vercel logs
railway logs

# Local debugging
docker-compose logs backend
docker-compose logs frontend
```

## 🚦 **Deployment Checklist**

### Pre-deployment
- [ ] API keys configured
- [ ] Environment variables set
- [ ] GitHub secrets added
- [ ] CORS origins updated
- [ ] Domain names configured

### Post-deployment
- [ ] Frontend loads correctly
- [ ] Backend health check passes
- [ ] API calls work
- [ ] Voice features enabled
- [ ] Language switching works
- [ ] Mobile responsiveness verified
- [ ] Performance metrics acceptable

## 🔮 **Advanced Features**

### Custom Domain Setup

**Vercel**:
1. Add domain in Vercel dashboard
2. Configure DNS records
3. SSL automatically provisioned

**Railway**:
1. Add custom domain in settings
2. Configure CNAME record
3. SSL certificate auto-generated

### CI/CD Enhancements

**Branch Previews**:
- Automatic preview deployments for PRs
- Separate staging environment
- A/B testing capabilities

**Advanced Monitoring**:
- Error tracking with Sentry
- Performance monitoring with New Relic
- Uptime monitoring with UptimeRobot

## 📚 **Additional Resources**

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com)

## 🆘 **Support**

If you encounter issues:
1. Check the troubleshooting section
2. Review deployment logs
3. Verify environment variables
4. Test locally with Docker
5. Check API key validity

Your WeatherBot is now ready for production with automated deployments! 🎉 