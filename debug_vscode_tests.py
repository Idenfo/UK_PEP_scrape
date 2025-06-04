#!/usr/bin/env python3
"""
Debug script to test VS Code pytest integration
"""
import sys
import os
import subprocess

print("=== VS Code Test Environment Debug ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
print(f"PATH: {os.environ.get('PATH', 'Not set')}")

# Check if we can import the main modules
try:
    import app
    print("✅ Successfully imported app module")
except ImportError as e:
    print(f"❌ Failed to import app module: {e}")

try:
    import pytest
    print(f"✅ Successfully imported pytest from: {pytest.__file__}")
except ImportError as e:
    print(f"❌ Failed to import pytest: {e}")

try:
    import pandas
    print(f"✅ Successfully imported pandas from: {pandas.__file__}")
except ImportError as e:
    print(f"❌ Failed to import pandas: {e}")

try:
    import flask
    print(f"✅ Successfully imported flask from: {flask.__file__}")
except ImportError as e:
    print(f"❌ Failed to import flask: {e}")

# Test pytest discovery
print("\n=== Pytest Discovery Test ===")
try:
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "test_app.py", "--collect-only", "-q"
    ], capture_output=True, text=True, cwd=os.getcwd())
    
    if result.returncode == 0:
        print("✅ Pytest discovery successful")
        lines = result.stdout.strip().split('\n')
        test_count = len([line for line in lines if '::' in line])
        print(f"✅ Found {test_count} tests")
    else:
        print("❌ Pytest discovery failed")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
except Exception as e:
    print(f"❌ Error running pytest: {e}")

# Test simple test execution
print("\n=== Simple Test Execution ===")
try:
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "test_app.py::TestHealthEndpoints::test_health_endpoint", "-v", "--tb=short"
    ], capture_output=True, text=True, cwd=os.getcwd())
    
    if result.returncode == 0:
        print("✅ Simple test execution successful")
    else:
        print("❌ Simple test execution failed")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
except Exception as e:
    print(f"❌ Error running simple test: {e}")

print("\n=== Debug Complete ===")
