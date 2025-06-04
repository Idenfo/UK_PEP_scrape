#!/usr/bin/env python3
"""
VS Code Test Integration Debug Script
This script helps diagnose VS Code test discovery and execution issues.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_environment():
    """Check Python environment and pytest availability."""
    print("🔍 Environment Check")
    print("=" * 50)
    
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    # Check pytest
    try:
        import pytest
        print(f"pytest version: {pytest.__version__}")
        print(f"pytest location: {pytest.__file__}")
    except ImportError:
        print("❌ pytest not available")
        return False
    
    return True

def check_pytest_discovery():
    """Test pytest test discovery."""
    print("\n🔎 Pytest Discovery Test")
    print("=" * 50)
    
    # Test discovery command
    cmd = [
        "/Users/solwarsop/miniforge3/envs/uk-pep-scraper/bin/pytest",
        "--collect-only",
        "--quiet",
        "test_simple.py"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pytest discovery: {e}")
        return False

def check_test_execution():
    """Test pytest execution."""
    print("\n🧪 Pytest Execution Test")
    print("=" * 50)
    
    # Test execution command
    cmd = [
        "/Users/solwarsop/miniforge3/envs/uk-pep-scraper/bin/pytest",
        "test_simple.py",
        "--no-cov",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False

def check_vscode_settings():
    """Check VS Code settings."""
    print("\n⚙️  VS Code Settings Check")
    print("=" * 50)
    
    settings_path = Path(".vscode/settings.json")
    if settings_path.exists():
        with open(settings_path) as f:
            try:
                settings = json.load(f)
                print("✅ Settings file is valid JSON")
                
                # Check key settings
                python_path = settings.get("python.defaultInterpreterPath")
                pytest_path = settings.get("python.testing.pytestPath")
                
                print(f"Python interpreter: {python_path}")
                print(f"Pytest path: {pytest_path}")
                
                # Verify paths exist
                if python_path and Path(python_path).exists():
                    print("✅ Python interpreter path exists")
                else:
                    print("❌ Python interpreter path not found")
                
                if pytest_path and Path(pytest_path).exists():
                    print("✅ Pytest path exists")
                else:
                    print("❌ Pytest path not found")
                    
                return True
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in settings file: {e}")
                return False
    else:
        print("❌ VS Code settings file not found")
        return False

def check_import_issues():
    """Check for import issues that might affect VS Code."""
    print("\n📦 Import Issues Check")
    print("=" * 50)
    
    try:
        # Test importing the main app
        from app import app, UKGovernmentScraper
        print("✅ Successfully imported app and UKGovernmentScraper")
        
        # Test Flask app creation
        with app.test_client() as client:
            response = client.get('/')
            print(f"✅ Flask app responds: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    print("🚀 VS Code Test Integration Diagnostics")
    print("=" * 60)
    
    checks = [
        ("Environment", check_environment),
        ("Pytest Discovery", check_pytest_discovery),
        ("Pytest Execution", check_test_execution),
        ("VS Code Settings", check_vscode_settings),
        ("Import Issues", check_import_issues)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error in {name} check: {e}")
            results[name] = False
    
    print("\n📊 Summary")
    print("=" * 50)
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    if all(results.values()):
        print("\n🎉 All checks passed! VS Code should work properly.")
    else:
        print("\n⚠️  Some checks failed. Review the output above.")

if __name__ == "__main__":
    main()
