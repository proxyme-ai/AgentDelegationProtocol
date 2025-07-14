# Contributing to Agent Delegation Protocol

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- Git

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/agent-delegation-protocol.git
   cd agent-delegation-protocol
   ```

2. Set up Python environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up frontend:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

5. Run tests:
   ```bash
   pytest -v
   cd frontend && npm test
   ```

## Code Style

### Python
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maximum line length: 88 characters
- Use `black` for code formatting:
  ```bash
  pip install black
  black .
  ```

### TypeScript/React
- Use TypeScript for all new code
- Follow React best practices
- Use ESLint configuration provided
- Format with Prettier:
  ```bash
  cd frontend
  npm run lint
  npm run format
  ```

## Testing

### Python Tests
- Write tests for all new functionality
- Maintain test coverage above 80%
- Use pytest fixtures for common setup
- Include both unit and integration tests

### Frontend Tests
- Write unit tests with Vitest
- Write E2E tests with Playwright
- Test user interactions and API integration

### Running Tests
```bash
# Python tests
pytest -v --cov=. --cov-report=html

# Frontend tests
cd frontend
npm test
npm run test:e2e
```

## Pull Request Process

1. **Fork and Branch**: Create a feature branch from `main`
2. **Implement**: Make your changes with appropriate tests
3. **Test**: Ensure all tests pass
4. **Document**: Update documentation if needed
5. **Commit**: Use conventional commit messages
6. **Pull Request**: Submit PR with clear description

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(auth): add PKCE support for enhanced security`
- `fix(token): handle expired delegation tokens properly`
- `docs(readme): update installation instructions`

## Issue Guidelines

### Bug Reports
Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

### Feature Requests
Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation approach
- Potential breaking changes

## Security

- Never commit secrets or credentials
- Report security issues privately
- Follow security best practices
- Update dependencies regularly

## Documentation

- Update README for user-facing changes
- Add docstrings for new functions/classes
- Update API documentation
- Include examples for new features

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release PR
4. Tag release after merge
5. Publish to package registries

## Community

- Be respectful and inclusive
- Help others learn and contribute
- Follow the code of conduct
- Participate in discussions

## Getting Help

- Check existing issues and documentation
- Ask questions in GitHub Discussions
- Join our community chat (if available)
- Reach out to maintainers

Thank you for contributing to make this project better!