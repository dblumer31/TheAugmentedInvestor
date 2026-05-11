# TDD Guide - Test Driven Development Workflow

This guide explains how to use Test Driven Development (TDD) in this project.

---

## What is TDD?

Test Driven Development is a development approach where you:

1. **Write a failing test first** (RED)
2. **Write minimal code to make it pass** (GREEN)
3. **Refactor while keeping tests green** (REFACTOR)

This cycle ensures code is testable, focused, and meets requirements.

---

## Project Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── unit/                # Fast, isolated tests
│   ├── __init__.py
│   ├── test_example.py  # Example tests demonstrating patterns
│   └── ...
└── integration/         # Tests requiring real dependencies
    ├── __init__.py
    └── ...
```

---

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Only Unit Tests (fast, no dependencies)

```bash
pytest tests/unit/
```

### Run Only Integration Tests (requires .env)

```bash
pytest tests/integration/
```

### Run with Verbose Output

```bash
pytest -v
```

### Run a Specific Test File

```bash
pytest tests/unit/test_example.py
```

### Run a Specific Test Function

```bash
pytest tests/unit/test_example.py::test_function_name
```

### Run Tests Matching a Pattern

```bash
pytest -k "keyword"
```

---

## Using Fixtures

Fixtures are reusable test data defined in `tests/conftest.py`. They are automatically available to all test functions.

### Example Fixtures

| Fixture | Description |
|---------|-------------|
| `mock_config` | Config object with test placeholders (no .env needed) |
| `sample_data` | Example data for testing |
| `sample_result` | Example result object |
| `tmp_path` | pytest built-in: temporary directory for file tests |

### Using Fixtures in Tests

```python
def test_my_function(mock_config, sample_data):
    """Test that uses fixtures."""
    # mock_config and sample_data are automatically provided
    Result = my_function(sample_data, mock_config)
    assert Result is not None
```

---

## TDD Workflow Example

### Step 1: Write a Failing Test (RED)

```python
# tests/unit/test_my_module.py

def test_process_data_returns_valid_result(sample_data):
    """Processing data should return a valid result."""
    Result = process_data(sample_data)
    
    assert Result is not None
    assert Result.IsValid is True
```

Run the test - it should fail because the function doesn't exist yet.

```bash
pytest tests/unit/test_my_module.py::test_process_data_returns_valid_result
# FAILED - NameError: name 'process_data' is not defined
```

### Step 2: Write Minimal Code (GREEN)

```python
# src/my_module.py

def process_data(Data):
    """Process input data and return result."""
    return Result(IsValid=True)
```

Run the test - it should pass now.

```bash
pytest tests/unit/test_my_module.py::test_process_data_returns_valid_result
# PASSED
```

### Step 3: Refactor

Add more tests, then expand the implementation:

```python
def test_process_data_handles_empty_input(sample_data):
    """Processing empty data should return invalid result."""
    Result = process_data([])
    
    assert Result.IsValid is False
```

Run tests, implement, repeat.

---

## Mocking External Dependencies

Use `pytest-mock` to mock external services in unit tests.

### Mocking a Function

```python
def test_with_mocked_database(mocker, mock_config):
    """Test that mocks database calls."""
    # Mock the query function
    MockQuery = mocker.patch("src.database.queries.query_data")
    MockQuery.return_value = [{"id": 1}, {"id": 2}]
    
    # Now query_data returns our mock data instead of hitting the database
    Result = my_function_that_uses_database(mock_config)
    
    assert Result is not None
    MockQuery.assert_called_once()
```

### Mocking an API Call

```python
def test_with_mocked_api(mocker, mock_config):
    """Test that mocks external API."""
    MockApi = mocker.patch("src.services.api_client.call_api")
    MockApi.return_value = {"status": "success", "data": []}
    
    Result = fetch_external_data(mock_config)
    
    assert Result["status"] == "success"
```

---

## Unit vs Integration Tests

### Unit Tests (`tests/unit/`)

- **Fast**: Run in milliseconds
- **Isolated**: No external dependencies
- **Mocked**: All external services are mocked
- **Always runnable**: Can run without VPN/database/API access

Example:
```python
def test_calculate_total(sample_data):
    """Unit test - uses fixture, no external dependencies."""
    Total = calculate_total(sample_data)
    assert Total == 100.00
```

### Integration Tests (`tests/integration/`)

- **Slower**: May take seconds
- **Real dependencies**: Use actual database/API
- **Require setup**: Need .env file and network access
- **Verify end-to-end**: Test real behavior

Example:
```python
def test_database_connection():
    """Integration test - requires real database."""
    Config = load_config()  # Loads real .env
    assert check_database_connection(Config) is True
```

---

## Best Practices

### 1. Test One Thing Per Test

```python
# Good - focused test
def test_total_is_calculated_correctly(sample_data):
    assert calculate_total(sample_data) == 100.00

# Bad - testing multiple things
def test_data_properties(sample_data):
    assert calculate_total(sample_data) == 100.00
    assert len(sample_data) == 5
    assert sample_data[0].Id == 1
```

### 2. Use Descriptive Test Names

```python
# Good - describes expected behavior
def test_empty_input_returns_zero_total():
    ...

# Bad - vague name
def test_data():
    ...
```

### 3. Arrange-Act-Assert Pattern

```python
def test_report_includes_timestamp(sample_data, tmp_path):
    # Arrange
    OutputPath = tmp_path / "report.json"
    
    # Act
    generate_report(sample_data, str(OutputPath))
    
    # Assert
    with open(OutputPath) as File:
        Data = json.load(File)
    assert "timestamp" in Data
```

### 4. Don't Test Implementation Details

```python
# Good - tests behavior
def test_report_contains_item_count(sample_data):
    Report = generate_report(sample_data)
    assert "Total Items: 5" in Report

# Bad - tests implementation
def test_report_uses_join_method(sample_data):
    # Don't test HOW the report is built, test WHAT it contains
    ...
```

---

## Troubleshooting

### Tests Not Found

- Ensure test files are named `test_*.py`
- Ensure test functions are named `test_*`
- Check `pytest.ini` configuration

### Import Errors

- Run pytest from the project root directory
- Ensure `src/` is importable (check `__init__.py` files)

### Fixture Not Found

- Ensure fixture is defined in `conftest.py`
- Check for typos in fixture name
- Fixtures are case-sensitive

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest tests/unit/` | Run unit tests only |
| `pytest -v` | Verbose output |
| `pytest -k "name"` | Run tests matching name |
| `pytest --tb=short` | Shorter tracebacks |
| `pytest --tb=long` | Full tracebacks |
| `pytest -x` | Stop on first failure |
| `pytest --lf` | Run last failed tests |
