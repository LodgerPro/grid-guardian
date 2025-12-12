# 🚀 Quick Start - Testing

## One Command Test Run

```bash
python run_tests.py
```

That's it! This will:
- ✅ Run all 92 tests
- ✅ Generate HTML report
- ✅ Generate coverage report
- ✅ Create test log

## View Results

### HTML Test Report
```bash
start tests/reports/test_report.html
```

### Coverage Report
```bash
start tests/reports/coverage/index.html
```

## Expected Results

```
======================== test session starts ========================
platform win32 -- Python 3.13.7, pytest-8.4.2
collected 92 items

tests/test_data_validation.py ........................    [ 26%]
tests/test_integration.py ...........                     [ 38%]
tests/test_model_validation.py ........                   [ 47%]
tests/test_performance.py ...........                     [ 58%]
tests/test_russian_language.py .....                      [ 64%]
tests/test_streamlit_app.py .................             [100%]

=================== 87 passed, 5 skipped in 30s ====================
```

## Reports Location

```
tests/reports/
├── test_report.html      ← Test execution report
├── coverage/
│   └── index.html        ← Code coverage report
└── test.log              ← Detailed log file
```

## Alternative Commands

### Quick Run (No Coverage)
```bash
pytest tests/ -v
```

### With Coverage Only
```bash
pytest tests/ --cov=app --cov=data --cov=src
```

### Specific Test File
```bash
pytest tests/test_data_validation.py -v
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

## Troubleshooting

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### pytest Not Found
```bash
pip install pytest pytest-cov pytest-html
```

---

**Need more details?** See [README.md](README.md)
