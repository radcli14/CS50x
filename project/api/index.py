import sys
import os
import traceback

# Force output to stderr immediately (Vercel captures this)
# Also try writing to a file in /tmp as backup
def log(msg):
    # Write to stderr (Vercel should capture this)
    print(msg, file=sys.stderr, flush=True)
    # Also write to stdout (sometimes Vercel captures this better)
    print(msg, file=sys.stdout, flush=True)
    # Backup: write to file in /tmp (if on Vercel)
    if os.environ.get("VERCEL") == "1":
        try:
            with open("/tmp/vercel_debug.log", "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        except:
            pass  # Don't fail if we can't write to file

# Wrap entire module in try/except to catch ANY error
try:
    log("=" * 80)
    log("STARTING API/INDEX.PY IMPORT")
    log(f"Python version: {sys.version}")
    log(f"Current directory: {os.getcwd()}")
    log(f"Script location: {__file__}")
    log(f"VERCEL env var: {os.environ.get('VERCEL', 'NOT SET')}")
    log("=" * 80)
except Exception as e:
    # Even logging can fail, so use basic print
    print(f"CRITICAL: Failed to log startup: {e}", file=sys.stderr, flush=True)
    print(traceback.format_exc(), file=sys.stderr, flush=True)

# Add parent directory to path so we can import app
try:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log(f"Adding to path: {parent_dir}")
    sys.path.insert(0, parent_dir)
    log(f"Python path: {sys.path}")
except Exception as e:
    log(f"ERROR setting up path: {e}")
    log(traceback.format_exc())
    raise

# Import the Flask app with granular error handling
log("Attempting to import app...")
try:
    from app import app
    log("SUCCESS: app imported")
    
    log("Setting up handler...")
    # Vercel's Python runtime expects the app to be exported as 'handler'
    # This will be used as the WSGI application
    handler = app
    log("Handler assigned")
    
    # Add error handler to log errors
    log("Setting up error handler...")
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Log all exceptions for debugging"""
        from flask import jsonify
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        # Return a proper error response
        if app.debug:
            return jsonify({
                "error": "Internal Server Error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }), 500
        else:
            return jsonify({
                "error": "Internal Server Error",
                "message": "An error occurred"
            }), 500
    
    log("=" * 80)
    log("SUCCESS: API/INDEX.PY FULLY LOADED")
    log("=" * 80)
        
except ImportError as e:
    # Specific handling for import errors
    error_msg = f"IMPORT ERROR: Failed to import app\n"
    error_msg += f"Error: {str(e)}\n"
    error_msg += f"Traceback:\n{traceback.format_exc()}\n"
    error_msg += f"Python path: {sys.path}\n"
    error_msg += f"Current dir: {os.getcwd()}\n"
    log(error_msg)
    raise
except Exception as e:
    # If import fails, log the error
    # Note: We can't create a proper handler here because the app import failed
    # Vercel will show this error in the function logs
    error_msg = f"CRITICAL: Failed to import app: {str(e)}\n{traceback.format_exc()}"
    log(error_msg)
    
    # Create a minimal WSGI-compatible handler that will at least report the error
    from flask import Flask, jsonify
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        """Fallback handler that reports import error"""
        return jsonify({
            "error": "Application Import Failed",
            "message": str(e),
            "traceback": traceback.format_exc() if os.environ.get("VERCEL_ENV") != "production" else "Check Vercel logs for details"
        }), 500
    
    handler = error_app

# Final safety net - catch any unhandled exception
except BaseException as e:
    # Catch everything, including SystemExit and KeyboardInterrupt
    error_msg = f"FATAL ERROR in api/index.py: {type(e).__name__}: {str(e)}\n"
    error_msg += f"Traceback:\n{traceback.format_exc()}\n"
    error_msg += f"Python path: {sys.path}\n"
    error_msg += f"Current dir: {os.getcwd()}\n"
    error_msg += f"VERCEL env: {os.environ.get('VERCEL', 'NOT SET')}\n"
    # Try multiple ways to output
    try:
        print(error_msg, file=sys.stderr, flush=True)
        print(error_msg, file=sys.stdout, flush=True)
    except:
        pass
    # Write to file as last resort
    try:
        with open("/tmp/vercel_error.log", "w") as f:
            f.write(error_msg)
            f.flush()
    except:
        pass
    # Re-raise so Vercel sees the error
    raise

