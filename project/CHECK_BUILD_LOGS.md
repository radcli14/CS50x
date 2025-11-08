# How to Check if Dependencies are Being Installed

## The Problem
Your code works locally but fails on Vercel with "Python process exited with exit status: 1". 
Since the local test shows "No module named 'flask'" when dependencies aren't installed,
the issue is likely that Vercel isn't installing your dependencies from `requirements.txt`.

## How to Check Build Logs

1. **Go to Vercel Dashboard**
   - https://vercel.com/dashboard
   - Select your project

2. **Check Latest Deployment**
   - Go to **"Deployments"** tab
   - Click on the **latest deployment** (most recent one)

3. **Look for Build Logs**
   - Look for **"Build Logs"** or **"Build Output"** section
   - This shows what happens during the build phase

4. **What to Look For:**
   - ✅ **Good:** You should see lines like:
     ```
     Installing dependencies from requirements.txt...
     Collecting flask>=2.0.0
     Installing collected packages: flask, werkzeug, flask-session
     ```
   - ❌ **Bad:** If you see:
     ```
     No requirements.txt found
     ```
     OR no mention of installing dependencies at all

## If Dependencies Aren't Being Installed

The `@vercel/python` builder should automatically detect `requirements.txt`, but sometimes it doesn't.

### Solution 1: Ensure requirements.txt is in root
Make sure `requirements.txt` is in the project root (same directory as `vercel.json`).

### Solution 2: Check Python Version
Vercel might be using a different Python version. Check the build logs for:
```
Using Python 3.x.x
```

Your local Python is 3.13.5, but Vercel might default to 3.9 or 3.11.

### Solution 3: Explicitly Specify Python Version
We can add a `runtime.txt` file to specify the Python version, but Vercel's Python builder might not support this.

## Next Steps

1. **Check the build logs** using the steps above
2. **Share what you see** - especially:
   - Does it mention installing dependencies?
   - What Python version is being used?
   - Are there any error messages during the build phase?

This will tell us if the issue is:
- Dependencies not being installed
- Python version mismatch
- Something else

