#!/usr/bin/env python3
"""Simple VS Code debug test."""

import sys
import os

print("🔍 VS Code Debug Test")
print("=" * 30)
print(f"Python: {sys.executable}")
print(f"Working dir: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

# Test basic import
try:
    from app import app
    print("✅ App import successful")
except Exception as e:
    print(f"❌ App import failed: {e}")

# Test pytest import
try:
    import pytest
    print(f"✅ pytest {pytest.__version__} available")
except Exception as e:
    print(f"❌ pytest import failed: {e}")

print("Debug test complete.")
