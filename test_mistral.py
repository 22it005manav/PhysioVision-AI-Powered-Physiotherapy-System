#!/usr/bin/env python3
import sys
sys.path.insert(0, r'd:\NEW PROJECT\PhysioVision-AI-Powered-Physiotherapy-System\Backend\Backend\venv\Lib\site-packages')

print("Trying different mistralai imports...")

try:
    from mistralai import Mistral
    print("✓ Found: from mistralai import Mistral")
except ImportError as e:
    print(f"✗ from mistralai import Mistral: {e}")

try:
    from mistralai.client import Mistral
    print("✓ Found: from mistralai.client import Mistral")
except ImportError as e:
    print(f"✗ from mistralai.client import Mistral: {e}")

try:
    import mistralai
    print(f"Mistralai package attributes: {dir(mistralai)}")
except ImportError as e:
    print(f"Cannot import mistralai: {e}")
