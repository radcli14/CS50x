#!/usr/bin/env python3
"""
Test script to simulate Vercel environment and test the import
This will help us see the actual error messages
"""
import os
import sys

# Set Vercel environment variable
os.environ["VERCEL"] = "1"

# Set SECRET_KEY if not set (Vercel would have this)
if "SECRET_KEY" not in os.environ:
    os.environ["SECRET_KEY"] = "test-secret-key-for-local-testing"

print("=" * 80)
print("TESTING VERCEL ENVIRONMENT IMPORT")
print("=" * 80)
print(f"VERCEL env var: {os.environ.get('VERCEL')}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print("=" * 80)
print()

# Try to import the handler
print("Attempting to import handler from api.index...")
print("-" * 80)

try:
    # Add the project root to path (same as api/index.py does)
    import os
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Try importing the handler
    from api.index import handler
    print("✅ SUCCESS: Handler imported successfully!")
    print(f"Handler type: {type(handler)}")
    print()
    print("The import worked! This means the error might be specific to Vercel's environment.")
    
except ImportError as e:
    print("❌ IMPORT ERROR:")
    print(f"   Error: {e}")
    print()
    import traceback
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print("❌ ERROR during import:")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error message: {e}")
    print()
    import traceback
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

