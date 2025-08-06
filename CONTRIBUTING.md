# Contributing to Bystronic OPC

Thank you for your interest in contributing to Bystronic OPC! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/danielristo/bystronic-opc.git
cd bystronic-opc
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
pip install -e .
```

## Development Workflow

### Code Style

This project uses:
- **Black** for code formatting
- **flake8** for linting  
- **mypy** for type checking

Run before committing:
```bash
black src/ tests/ examples/
flake8 src/ tests/ examples/
mypy src/
```

### Testing

Run tests with:
```bash
pytest tests/
```

For async tests:
```bash
pytest tests/ -v --asyncio-mode=auto
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pre-commit install
```

This will run checks automatically before commits.

## Contributing Guidelines

### Issues

- Search existing issues before creating new ones
- Use descriptive titles and provide detailed information
- Include system information and error messages when reporting bugs
- Label issues appropriately (bug, feature request, documentation, etc.)

### Pull Requests

1. **Fork** the repository
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the code style guidelines
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Run tests** and ensure they pass
7. **Commit your changes** with descriptive messages
8. **Push to your fork** and create a pull request

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for historical data export

- Implement CSV export functionality
- Add JSON export option  
- Include timestamp formatting
- Add unit tests for export functions
```

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all public APIs
- Write docstrings for all public functions and classes
- Add unit tests for new functionality
- Ensure async/await patterns are used correctly
- Handle exceptions appropriately

### Documentation

- Update README.md for new features
- Add docstrings to all public functions
- Include usage examples
- Update API documentation

### Testing

- Write unit tests for all new functionality
- Include integration tests for OPC UA operations
- Mock external dependencies appropriately
- Ensure tests are deterministic and can run in isolation

## Project Structure

```
bystronic-opc/
├── src/bystronic_opc/          # Main package
│   ├── __init__.py
│   ├── client.py               # Main client class
│   ├── monitor.py              # Multi-machine monitoring
│   ├── data_types.py           # Data structures
│   ├── exceptions.py           # Exception classes
│   └── web/                    # Web interface
├── tests/                      # Test suite
├── examples/                   # Usage examples
├── docs/                       # Documentation
└── requirements*.txt           # Dependencies
```

## Areas for Contribution

### High Priority
- Web interface implementation
- Historical data analysis tools
- Error handling improvements
- Performance optimizations
- Documentation improvements

### Medium Priority
- Additional data export formats
- Configuration management
- Logging enhancements
- CLI tools
- Docker support

### Low Priority
- GUI applications
- Dashboard templates
- Integration examples
- Performance benchmarks

## Getting Help

- Check the documentation in `docs/`
- Look at examples in `examples/`
- Search existing issues
- Create a new issue for questions

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.