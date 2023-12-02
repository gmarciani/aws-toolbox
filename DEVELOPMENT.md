# AWS Toolbox -- Development

## Requirements
```
pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Configure Pre-Commit
Install pre-commit hook for the local repo:
```
pre-commit install
```

For the first time, run pre-commit checks on the whole codebase:
```
pre-commit run --all-files
```

## Install
Install the package on your local environment:
```
pip install -e .
```

## Build
```
python -m build
```

## Publish
Publish to PyPI test repo at [TestPyPi:aws-toolbox](https://test.pypi.org/project/aws-toolbox):
```
python -m twine upload --repository testpypi dist/*
```

Publish to PyPI production repo at [PyPi:aws-toolbox](https://pypi.org/project/aws-toolbox):
```
python -m twine upload dist/*
```
