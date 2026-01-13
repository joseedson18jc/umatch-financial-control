# Complete Deployment Guide - UMatch Financial Control

## ✅ Prerequisites Complete
- [x] Code cleaned and verified
- [x] Git repository initialized
- [x] Code committed locally
- [x] Application tested locally
- [x] Deployment configuration ready

## 🚀 Step-by-Step Deployment

### Step 1: GitHub Setup (In Progress)

#### 1.1 Create Repository
1. Go to https://github.com and log in
2. Click "+" → "New repository"
3. Repository details:
   - Name: `umatch-financial-control`
   - Description: `UMatch Financial Control System`
   - Visibility: Private or Public
   - ⚠️ DO NOT check "Initialize with README"
4. Click "Create repository"

#### 1.2 Push Code to GitHub
Once you provide the repository URL, run:
```bash
cd "/Users/joseedsondacosta/Downloads/final prok"
git remote add origin YOUR_GITHUB_REPO_URL
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend to Render.com

#### 2.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub account (recommended)
3. Authorize Render to access your repositories

#### 2.2 Deploy Backend Service
1. On Render Dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository: `umatch-financial-control`
3. Configure the service:
   ```
   Name: umatch-backend
   Region: Oregon (or closest to you)
   Branch: main
   Root Directory: backend
   Runtime: Docker

   Docker Build Context Directory: backend
   Dockerfile Path: ./Dockerfile

   Instance Type: Free
   ```

4. Add Environment Variables:
   - Click "Advanced" → "Add Environment Variable"
   - Variables to add:
     ```
     PORT = 8000
     PYTHON_VERSION = 3.9
     SECRET_KEY = [generate a secure random string]
     ```

5. Click "Create Web Service"
6. Wait 5-10 minutes for deployment
7. **Copy the backend URL** (looks like: `https://umatch-backend.onrender.com`)

#### 2.3 Add Persistent Storage (Optional)
1. In your backend service, go to "Disks"
2. Add disk:
   ```
   Name: data-storage
   Mount Path: /app/data
   Size: 1 GB
   ```

### Step 3: Deploy Frontend to Render.com

#### 3.1 Create Static Site
1. On Render Dashboard, click "New +" → "Static Site"
2. Connect the same repository: `umatch-financial-control`
3. Configure:
   ```
   Name: umatch-frontend
   Branch: main
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: dist
   ```

4. Add Environment Variable:
   ```
   Key: VITE_API_URL
   Value: [Your backend URL from Step 2.2]
   ```

5. Click "Create Static Site"
6. Wait 3-5 minutes for deployment
7. **Copy the frontend URL** (looks like: `https://umatch-frontend.onrender.com`)

### Step 4: Configure CORS

#### 4.1 Update Backend Environment
1. Go to your backend service on Render
2. Click "Environment" tab
3. Add new variable:
   ```
   Key: FRONTEND_URL
   Value: [Your frontend URL from Step 3.1]
   ```
4. Click "Save Changes"
5. Backend will automatically redeploy (2-3 minutes)

### Step 5: Test Your Live Application

1. **Open your frontend URL**: `https://umatch-frontend.onrender.com`
2. **Test login** with default credentials:
   - Username: `admin`
   - Password: `admin123`
3. **Test file upload**: Upload a CSV file
4. **Check API**: Visit `https://umatch-backend.onrender.com/docs`

## 🔍 Verification Checklist

After deployment, verify:
- [ ] Frontend loads without errors
- [ ] Backend API docs accessible at `/docs`
- [ ] Login works with default credentials
- [ ] CSV upload functionality works
- [ ] Dashboard displays data correctly
- [ ] No CORS errors in browser console

## ⚠️ Important Notes

### Free Tier Limitations
- Services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- 750 hours/month free (enough for development)

### Security Reminders
- ⚠️ Change default admin password immediately
- ⚠️ Update SECRET_KEY environment variable
- ⚠️ Add OPENAI_API_KEY if using AI features

### Custom Domain (Optional)
To use a custom domain:
1. Go to service settings
2. Click "Custom Domain"
3. Follow instructions to add DNS records

## 🐛 Troubleshooting

### Frontend shows "Network Error"
- Check VITE_API_URL environment variable
- Verify backend is running
- Check browser console for CORS errors

### Backend fails to deploy
- Check build logs in Render dashboard
- Verify Dockerfile syntax
- Ensure requirements.txt has all dependencies

### CORS Errors
- Verify FRONTEND_URL is set correctly in backend
- Check that URLs match exactly (https, no trailing slash)

## 📊 Monitoring

### Check Logs
- Backend logs: Render Dashboard → Service → Logs
- Frontend logs: Browser Developer Tools → Console

### Check Status
- Backend health: `https://your-backend.onrender.com/api/health`
- Frontend: Access the main URL

## 🔄 Updates

To deploy updates:
```bash
git add .
git commit -m "Your update message"
git push origin main
```

Both services will auto-deploy on push (if enabled).

## 📞 Support

If you encounter issues:
1. Check Render service logs
2. Review environment variables
3. Verify build commands
4. Check the project documentation

---

**Current Status:** ⏳ Waiting for GitHub repository URL

**Next Step:** Push code to GitHub, then proceed with Render deployment
