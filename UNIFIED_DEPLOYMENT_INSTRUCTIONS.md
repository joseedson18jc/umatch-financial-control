# ✨ Unified Deployment - Frontend + Backend Together

## ✅ What Changed

The application is now **unified** - frontend and backend are deployed as a **single service**!

### Benefits:
- ✅ One URL for everything
- ✅ No CORS issues
- ✅ Simpler deployment
- ✅ Faster cold starts
- ✅ Lower costs (one service instead of two)

## 🚀 Deploy to Render.com - SIMPLE STEPS

### Option 1: Blueprint (Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com/

2. **Click "New +" → "Blueprint"**

3. **Connect Repository**: `joseedson18jc/umatch-financial-control`

4. **Click "Apply"** - That's it!

5. **Wait 8-10 minutes** for build and deployment

6. **Get your URL**: Will be shown when complete (e.g., `https://umatch-financial-control.onrender.com`)

### Option 2: Manual Web Service

1. **Go to Render Dashboard**: https://dashboard.render.com/

2. **Click "New +" → "Web Service"**

3. **Connect Repository**: `joseedson18jc/umatch-financial-control`

4. **Configure**:
   ```
   Name: umatch-financial-control
   Region: Oregon (US West) or closest
   Branch: main
   Root Directory: (leave empty)
   Runtime: Docker
   Dockerfile Path: ./Dockerfile
   Instance Type: Free
   ```

5. **Environment Variables** (Click "Advanced"):
   ```
   PORT = 8000
   SECRET_KEY = umatch-production-secret-key-change-this-12345
   PYTHON_VERSION = 3.9
   ```

6. **Add Disk** (Optional but recommended):
   ```
   Name: data-storage
   Mount Path: /app/data
   Size: 1 GB
   ```

7. **Click "Create Web Service"**

8. **Wait 8-10 minutes** for deployment

## 🎉 After Deployment

Once deployed, you'll have:
- **One URL** for everything: `https://umatch-financial-control.onrender.com`
- **API docs** at: `https://umatch-financial-control.onrender.com/docs`
- **Health check**: `https://umatch-financial-control.onrender.com/api/health`

### Test Your Deployment

1. **Open the URL** in your browser
2. **Login** with:
   - Username: `admin`
   - Password: `admin123`
3. **Upload a CSV** file to test functionality
4. **Check API docs** at `/docs`

## 🔧 Update Existing Deployment

If you already deployed separate frontend/backend:

1. **Delete the old services**:
   - Go to each service → Settings → Delete Service

2. **Deploy the new unified service** using steps above

## ⚠️ Important Notes

### First Visit
- Free tier services sleep after 15 minutes
- First request takes 30-60 seconds to wake up
- Subsequent requests are instant

### Security
⚠️ **Change these immediately after deployment:**
- Admin password (in the app)
- SECRET_KEY environment variable
- Add OPENAI_API_KEY if using AI features

### Monitoring
- Check logs: Dashboard → Your Service → Logs
- Check health: Visit `/api/health`
- View API: Visit `/docs`

## 📊 What's Included

The unified deployment includes:
- ✅ FastAPI backend
- ✅ React frontend (pre-built)
- ✅ Static file serving
- ✅ API endpoints
- ✅ Authentication
- ✅ File upload
- ✅ Data persistence (with disk)

## 🐛 Troubleshooting

### Build fails
- Check build logs in Render dashboard
- Verify GitHub repository is accessible
- Ensure Dockerfile is in root directory

### App loads but shows blank page
- Check browser console for errors
- Verify build logs show "Frontend build: ✓"
- Check `/api/health` endpoint returns `"frontend_exists": true`

### Can't login
- Check browser console for API errors
- Verify PORT environment variable is set to 8000
- Check service logs for errors

## 💡 Tips

### Custom Domain
Add your own domain in:
Service Settings → Custom Domain

### Environment Variables
Update in:
Service → Environment → Add/Edit

### View Logs
Real-time logs in:
Dashboard → Service → Logs

### Rebuild
Trigger manual rebuild:
Service → Manual Deploy → Deploy Latest Commit

---

## 🎯 Quick Reference

**Repository**: https://github.com/joseedson18jc/umatch-financial-control

**Render Dashboard**: https://dashboard.render.com/

**Documentation**: See `README.md` in repository

**Support**: Check service logs and `/api/health` endpoint

---

**Status**: ✅ Ready to deploy!

**Next Step**: Go to Render.com and click "New +" → "Blueprint" or "Web Service"
