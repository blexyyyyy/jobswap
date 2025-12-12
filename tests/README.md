# Test Scripts

This folder contains various test and verification scripts used during development.

## Scripts

### `verify_groq.py`
Verifies that the Groq API key is working correctly.
```bash
python tests/verify_groq.py
```

### `test_app_groq.py`
End-to-end test for Groq integration through the full application stack.
```bash
python tests/test_app_groq.py
```

### `test_llm.py`
Tests LLM functionality (Gemini/Groq).
```bash
python tests/test_llm.py
```

### `checklist_verifier.py`
Runs a comprehensive checklist to verify API key configuration and connectivity.
```bash
python tests/checklist_verifier.py
```

### `diagnose_groq.py`
Diagnostic script for troubleshooting Groq API issues.
```bash
python tests/diagnose_groq.py
```

### `final_verify.py`
Final verification script for API key validation.
```bash
python tests/final_verify.py
```

## Usage

All test scripts should be run from the project root directory:
```bash
cd c:\Users\veerat\Desktop\jobswipe
python tests/script_name.py
```

## Note

These scripts are for development and testing only. They are not part of the production deployment.
