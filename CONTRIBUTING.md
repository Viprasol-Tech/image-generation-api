# Contributing to Image Generation API

Thanks for your interest in improving this project, maintained by
[Viprasol Tech](https://viprasol.com)! 🎉

## Getting started

```bash
git clone https://github.com/Viprasol-Tech/image-generation-api.git
cd image-generation-api
pip install -e ".[dev]"
```

## Quality gates

Everything below runs fully offline and must pass before a PR is merged:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

## Guidelines

- Keep changes focused; one logical change per PR.
- Add or update tests for any behavior change (target 10+ offline tests stays green).
- New provider adapters should subclass `ImageProvider` and lazy-import heavy deps.
- Run the quality gates locally before pushing.
- Be respectful — see our [Code of Conduct](CODE_OF_CONDUCT.md).

## Reporting bugs / requesting features

Use the GitHub issue templates. For security issues, see [SECURITY.md](SECURITY.md).

Questions? Reach us at [support@viprasol.com](mailto:support@viprasol.com).
