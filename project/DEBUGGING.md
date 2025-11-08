# Debugging Vercel FUNCTION_INVOCATION_FAILED Errors

## How to Access Error Logs

### Method 1: Vercel Dashboard - Logs Tab (Recommended)

**To see detailed error messages:**

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Click on the **"Logs"** tab (in the top navigation)
4. **Click on a specific log entry** (the row showing "Python process exited...")
   - This will expand the entry and show detailed error messages
   - Look for the diagnostic messages we added (lines starting with `STARTING`, `ERROR`, etc.)
5. **Alternative: Check Function Logs**
   - Go to **"Deployments"** tab
   - Click on the latest deployment
   - Look for **"Functions"** section or tab
   - Click on your function (`api/index.py`)
   - This shows the function's runtime logs with all `print()` output

**What you'll see:**
- The main log view shows a summary: "Python process exited with exit status: 1"
- **Clicking on the log entry** should expand it, but sometimes Vercel doesn't show detailed logs in the expanded view

**If expanded view doesn't show details, try these alternatives:**

1. **Check Build Logs:**
   - Go to **Deployments** tab
   - Click on the latest deployment
   - Look for **"Build Logs"** or **"Build Output"**
   - This shows output during the build/import phase

2. **Use Vercel CLI:**
   ```bash
   vercel logs [your-deployment-url] --follow
   ```
   This often shows more detail than the web interface

3. **Check Function Runtime Logs:**
   - Go to **Deployments** → Latest deployment
   - Look for **"Functions"** section
   - Click on `api/index.py`
   - This shows runtime logs with all print statements

4. **Try the Debug Endpoint (if app partially loads):**
   - Visit: `https://your-site.vercel.app/debug/logs`
   - This shows debug logs written to `/tmp/vercel_debug.log`
   - Only works if the app loads enough to serve requests

**Tip:** Look for log entries with red highlighting - these are the errors. If clicking doesn't show details, use the CLI method above.

### Method 2: Vercel CLI
```bash
# Install Vercel CLI if you haven't
npm i -g vercel

# Login
vercel login

# View logs
vercel logs [your-deployment-url]
```

### Method 3: Browser Network Tab (Limited)
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Make a request to your site
4. Click on the failed request
5. Check the **Response** tab - you might see error details
6. Check the **Headers** tab for status codes

**Note:** Browser console won't show server-side errors, but Network tab might show error responses.

## What to Look For

### Step-by-Step Import Logging

The enhanced error logging will show **exactly where** the import fails:

1. **Look for these markers in the logs:**
   ```
   ================================================================================
   STARTING API/INDEX.PY IMPORT
   ================================================================================
   ```
   - If you see this, the import process started
   - The last message before the error tells you where it failed

2. **Import steps (in order):**
   - `STARTING API/INDEX.PY IMPORT` - Handler file loading
   - `Adding to path: [path]` - Path setup
   - `Attempting to import app...` - Starting app import
   - `STARTING APP.PY IMPORT` - App file loading
   - `Importing Flask...` - Flask library
   - `Importing flask_session...` - Session library
   - `Importing werkzeug...` - Security library
   - `Importing helpers...` - Your helpers module
   - `Importing database...` - Your database module
   - `Creating Flask app...` - App creation
   - `Configuring for Vercel...` - Session setup
   - `Initializing database...` - Database setup
   - `SUCCESS: APP.PY FULLY LOADED` - Everything worked!

3. **Error messages will show:**
   - **Which step failed** (the last SUCCESS message before ERROR)
   - **The exact error message**
   - **Full Python traceback** with line numbers
   - **Python path** (if import error)
   - **Current directory** (if path error)

### About Favicon Errors

**Favicon errors are harmless!** They're just 404 errors because browsers automatically request `/favicon.ico`. You can ignore these - they're not causing your FUNCTION_INVOCATION_FAILED error.

## Common Issues and Solutions

### Issue: "Failed to import app"
- **Cause**: Error in `app.py` during import
- **Check**: Look for syntax errors, missing imports, or initialization errors
- **Fix**: The error message will show the exact line and error

### Issue: "Schema initialization failed"
- **Cause**: Database connection or table creation failed
- **Check**: Verify `/tmp` is writable (it should be on Vercel)
- **Fix**: Check the specific error message in logs

### Issue: CSV files not found
- **Cause**: CSV files not included in deployment or wrong path
- **Check**: Look for "DEBUG: CSV folder exists: False" in logs
- **Fix**: Ensure CSV files are committed to git and included in deployment

## Testing Locally

Before deploying, test locally:
```bash
# Set Vercel environment variable
export VERCEL=1

# Run Flask app
python app.py

# Or test the API handler
python -c "from api.index import handler; print('Handler loaded successfully')"
```

## Next Steps

1. **Deploy the updated code** with enhanced logging
2. **Check Vercel logs** using Method 1 above
3. **Look for the diagnostic messages** - they'll show exactly where it fails:
   - Find the last `SUCCESS` or `STARTING` message
   - The next `ERROR` message tells you what failed
   - The traceback shows the exact line number
4. **Share the error details** if you need help:
   - The last SUCCESS message you see
   - The ERROR message that follows
   - The full traceback (if available)

## Example: What Good Logs Look Like

```
================================================================================
STARTING API/INDEX.PY IMPORT
Python version: 3.9.x
Current directory: /var/task
Script location: /var/task/api/index.py
================================================================================
Adding to path: /var/task
Attempting to import app...
================================================================================
STARTING APP.PY IMPORT
================================================================================
Importing Flask...
Flask imported successfully
Importing flask_session...
flask_session imported successfully
Importing werkzeug...
werkzeug imported successfully
Importing helpers...
helpers imported successfully
Importing database...
database imported successfully
Creating Flask app...
Flask app created
Checking Vercel environment...
Is Vercel: True
Configuring for Vercel...
Vercel session config complete
Initializing database...
Database initialized
================================================================================
SUCCESS: APP.PY FULLY LOADED
================================================================================
SUCCESS: app imported
Setting up handler...
Handler assigned
Setting up error handler...
================================================================================
SUCCESS: API/INDEX.PY FULLY LOADED
================================================================================
```

If you see an error, it will look like:
```
Importing database...
ERROR importing database: [error message]
Traceback (most recent call last):
  File "app.py", line 50, in <module>
    from database import get_db, init_db, get_user_data
  ...
[full traceback]
```

This tells you **exactly** what failed and where!

