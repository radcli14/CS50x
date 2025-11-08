import sys
import os
import traceback

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app with error handling
try:
    from app import app
    
    # Vercel's Python runtime expects the app to be exported as 'handler'
    # This will be used as the WSGI application
    handler = app
    
    # Add error handler to log errors
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

