# Contributing to RiverCityClean SaaS CRM

Thank you for your interest in contributing to the RiverCityClean SaaS CRM project! This document provides guidelines and best practices for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Conventions](#commit-conventions)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

## Code of Conduct

- **Be respectful** and considerate in all interactions
- **Provide constructive feedback** with actionable suggestions
- **Welcome newcomers** and help them get started
- **Focus on what is best** for the community and project

## Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **Git** 2.30+
- **Docker** and Docker Compose (optional)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/your-org/Saas-CRM---Claude.git
cd Saas-CRM---Claude

# Install frontend dependencies
cd crm && npm install
cd ../ops-console && npm install

# Install Python dependencies (if working on backend)
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Review docs
cat README.md
cat POLICY.md
```

### Pre-commit Hooks (Recommended)

Install pre-commit hooks to automatically check code quality:

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Pre-push Quality Gates

Install the pre-push hook to run quality gates before pushing:

```bash
cp hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description

# Or for documentation
git checkout -b docs/what-you-are-documenting
```

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run type checking
cd crm && npx tsc --noEmit
cd ops-console && npx tsc --noEmit

# Run unit tests
cd crm && npm test
cd ops-console && npm test

# Run quality gates
./scripts/prepush.sh
```

### 4. Commit Your Changes

Follow the [Conventional Commits](#commit-conventions) specification:

```bash
git add .
git commit -m "feat: add user authentication"
```

### 5. Push and Create Pull Request

```bash
# Push your branch
git push -u origin feature/your-feature-name

# Create pull request on GitHub
# Fill out the PR template completely
```

## Commit Conventions

This project follows the **[Conventional Commits](https://www.conventionalcommits.org/)** specification for commit messages. This ensures clear commit history and enables automatic changelog generation.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type** (required): The kind of change

**Scope** (optional): What part of the codebase is affected

**Subject** (required): Short description

**Body** (optional): Detailed explanation

**Footer** (optional): Breaking changes, issue references

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add user dashboard` |
| `fix` | Bug fix | `fix: resolve login redirect issue` |
| `docs` | Documentation only | `docs: update API documentation` |
| `style` | Code style/formatting (no logic change) | `style: format with prettier` |
| `refactor` | Code refactoring | `refactor: simplify auth logic` |
| `perf` | Performance improvement | `perf: optimize database queries` |
| `test` | Add or update tests | `test: add unit tests for auth` |
| `build` | Build system or dependencies | `build: upgrade React to 18.2` |
| `ci` | CI/CD changes | `ci: add GitHub Actions workflow` |
| `chore` | Maintenance tasks | `chore: update dependencies` |
| `revert` | Revert previous commit | `revert: feat: add user dashboard` |

### Commit Examples

#### Feature

```bash
git commit -m "feat: add password reset functionality

Implement password reset flow with email verification.
Users can now request a password reset link via email.

Closes #123"
```

#### Bug Fix

```bash
git commit -m "fix: resolve dashboard loading spinner

The loading spinner was not hiding after data load completed.
Fixed by properly awaiting the async data fetch.

Fixes #456"
```

#### Documentation

```bash
git commit -m "docs: add API authentication guide

Created comprehensive guide for API authentication including:
- JWT token generation
- Token refresh flow
- Error handling examples"
```

#### Breaking Change

```bash
git commit -m "feat!: migrate to new authentication system

BREAKING CHANGE: The old auth endpoints are no longer supported.
Clients must update to use the new /api/v2/auth endpoints.

Migration guide: docs/AUTH_MIGRATION.md

Closes #789"
```

#### Multiple Changes

```bash
git commit -m "feat: implement role-based access control

- Add Role and Permission models
- Implement RBAC middleware
- Update user model with role assignment
- Add permission checking utilities

Closes #234"
```

### Scope Examples

Use scope to specify what part of the project is affected:

```bash
feat(crm): add lead scoring algorithm
fix(ops-console): correct dashboard metrics
docs(api): document webhook endpoints
test(auth): add integration tests for login
refactor(database): optimize query performance
style(ui): update button hover states
```

### Best Practices

✅ **DO:**
- Use imperative mood ("add feature" not "added feature")
- Keep the subject line under 72 characters
- Separate subject from body with a blank line
- Wrap body at 72 characters
- Use body to explain "what" and "why" vs "how"
- Reference issues and PRs in footer
- Use `BREAKING CHANGE:` for breaking changes

❌ **DON'T:**
- Use past tense ("added" or "adding")
- End subject line with a period
- Make vague commits ("fix stuff", "update code")
- Commit incomplete work (use feature branches)
- Mix unrelated changes in one commit

### Commit Message Anti-Patterns

```bash
# ❌ Bad
git commit -m "fix"
git commit -m "update"
git commit -m "WIP"
git commit -m "Fixed the bug that John found"
git commit -m "feat: Added a new feature for users to login and also fixed some bugs and updated docs"

# ✅ Good
git commit -m "fix: resolve null pointer in user service"
git commit -m "docs: update authentication guide"
git commit -m "feat: add email verification for new users"
git commit -m "refactor: extract validation logic to separate module"
```

## Pull Request Process

### Before Submitting

1. **Run quality gates**: `./scripts/prepush.sh`
2. **Update documentation**: Reflect any API or behavior changes
3. **Add tests**: Ensure new code has test coverage
4. **Review your own code**: Check the diff for issues
5. **Fill out PR template**: Provide complete context

### PR Title Format

Use conventional commit format for PR titles:

```
feat: add user notification system
fix: resolve memory leak in data processing
docs: improve quickstart guide
```

### PR Description Requirements

Your PR must include:

- **Summary**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Implementation**: How did you implement it?
- **Testing**: How did you test this?
- **Screenshots**: If UI changes, include before/after
- **Breaking Changes**: Document any breaking changes
- **Related Issues**: Link to related issues

### Review Process

- PRs require **at least one approval** from a maintainer
- Address all review comments before merging
- Keep PRs focused and reasonably sized (< 500 lines preferred)
- Respond to feedback within 48 hours
- Be open to suggestions and alternative approaches

### Merging

- **Squash and merge** is preferred for feature branches
- **Merge commit** is used for release branches
- Ensure PR title follows conventional commits format
- Delete branch after merging

## Coding Standards

### TypeScript/React (Frontend)

- **TypeScript**: Use strict mode, avoid `any`
- **Components**: Functional components with hooks
- **Naming**: PascalCase for components, camelCase for functions
- **Props**: Define explicit interfaces for component props
- **Imports**: Organize imports (React first, then libraries, then local)

### Python (Backend)

- **Style**: Follow PEP 8
- **Type hints**: Use type annotations
- **Docstrings**: Use Google-style docstrings
- **Naming**: snake_case for functions and variables, PascalCase for classes
- **Line length**: Max 100 characters

### General

- **DRY**: Don't repeat yourself
- **KISS**: Keep it simple
- **YAGNI**: You aren't gonna need it
- **Comments**: Explain "why", not "what"
- **Security**: Never commit secrets or credentials

## Testing Requirements

### Unit Tests

- Write unit tests for all new functions and components
- Aim for **80%+ code coverage**
- Test edge cases and error conditions
- Use descriptive test names

### Integration Tests

- Test critical user flows end-to-end
- Verify API contracts
- Test error handling and edge cases

### Running Tests

```bash
# Frontend tests
cd crm && npm test
cd ops-console && npm test

# Run with coverage
cd crm && npm test -- --coverage

# Backend tests (if applicable)
pytest
pytest --cov=app tests/
```

## Documentation

### Code Documentation

- Add JSDoc/TSDoc comments for public APIs
- Include examples in documentation
- Document complex algorithms and business logic
- Keep comments up-to-date with code changes

### Project Documentation

- Update README.md if adding new features
- Document new environment variables in .env.example
- Add examples to docs/ directory
- Update CHANGELOG.md (handled by maintainers)

### API Documentation

- Document all API endpoints
- Include request/response examples
- Document error codes and responses
- Keep OpenAPI/Swagger specs updated

## Questions and Support

- **Documentation**: Check docs/ directory first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Slack**: Join our Slack workspace (if applicable)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

**Thank you for contributing!** 🎉

Your efforts help make this project better for everyone.
