# Alternative: Manual Render Deployment

If Blueprint deployment fails, use this manual approach:

## Step-by-Step Manual Deployment

1. **Go to Render Dashboard**: https://dashboard.render.com/

2. **Click "New +" → "Web Service"**

3. **Connect GitHub Repository**:
   - Select: `joseedson18jc/umatch-financial-control`
   - Click "Connect"

4. **Configure Service**:
   ```
   Name: umatch-financial-control
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave blank)
   Runtime: Docker
   Dockerfile Path: ./Dockerfile
   Docker Build Context Directory: (leave blank)
   ```

5. **Select Instance Type**:
   - Choose: **Free**

6. **Environment Variables** (Click "Advanced"):
   Add these one by one:
   ```
   PORT = 8000
   SECRET_KEY = umatch-production-secret-change-this-now
   PYTHON_VERSION = 3.9
   ```

7. **Auto-Deploy**:
   - Enable "Auto-Deploy" (Yes)

8. **Click "Create Web Service"**

9. **Wait for Build**:
   - Takes 8-12 minutes
   - Watch the logs for progress

## What to Watch in Logs

Look for these stages:
```
✓ Stage 1: Building frontend...
✓ npm install
✓ npm run build
✓ Stage 2: Backend setup...
✓ pip install requirements
✓ Copying frontend build
✓ Server starting...
```

## Troubleshooting

### Build Timeout
If build times out:
- Render free tier has limited build time
- Try again - sometimes it's just network issues

### Memory Issues
If you see "out of memory":
- This is a free tier limitation
- Try deploying during off-peak hours

### Build Fails
Check logs for specific errors:
- npm errors → frontend build issue
- pip errors → backend dependency issue
- uvicorn errors → server startup issue

## After Successful Deployment

Your app will be at:
```
https://umatch-financial-control-XXXX.onrender.com
```

Test it:
1. Open the URL
2. Login with admin/admin123
3. Check /docs endpoint
4. Check /api/health endpoint

---

**Need help?** Share the error logs and I'll help debug!
