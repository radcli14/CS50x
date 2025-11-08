import sys
import os
import traceback

# Force output to stderr immediately (Vercel captures this)
print("=" * 80, file=sys.stderr)
print("STARTING API/INDEX.PY IMPORT", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Current directory: {os.getcwd()}", file=sys.stderr)
print(f"Script location: {__file__}", file=sys.stderr)
print("=" * 80, file=sys.stderr)

# Add parent directory to path so we can import app
try:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Adding to path: {parent_dir}", file=sys.stderr)
    sys.path.insert(0, parent_dir)
    print(f"Python path: {sys.path}", file=sys.stderr)
except Exception as e:
    print(f"ERROR setting up path: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    raise

# Import the Flask app with granular error handling
print("Attempting to import app...", file=sys.stderr)
try:
    from app import app
    print("SUCCESS: app imported", file=sys.stderr)
    
    print("Setting up handler...", file=sys.stderr)
    # Vercel's Python runtime expects the app to be exported as 'handler'
    # This will be used as the WSGI application
    handler = app
    print("Handler assigned", file=sys.stderr)
    
    # Add error handler to log errors
    print("Setting up error handler...", file=sys.stderr)
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
    
    print("=" * 80, file=sys.stderr)
    print("SUCCESS: API/INDEX.PY FULLY LOADED", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
        
except ImportError as e:
    # Specific handling for import errors
    error_msg = f"IMPORT ERROR: Failed to import app\n"
    error_msg += f"Error: {str(e)}\n"
    error_msg += f"Traceback:\n{traceback.format_exc()}\n"
    error_msg += f"Python path: {sys.path}\n"
    error_msg += f"Current dir: {os.getcwd()}\n"
    print(error_msg, file=sys.stderr)
    raise
except Exception as e:
    # If import fails, log the error
    # Note: We can't create a proper handler here because the app import failed
    # Vercel will show this error in the function logs
    error_msg = f"CRITICAL: Failed to import app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
    
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

