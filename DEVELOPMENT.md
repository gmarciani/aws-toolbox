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

## Release
To release a new version you need to push the release tag.
Such a push triggers the automatic release to PyPI and the publication of the release on GitHub.

```
RELEASE=X.Y.Z
git tag v${RELEASE} && git push origin v${RELEASE}
```

To delete the release tag and release notes (this does not delete the release from PyPI):
```
RELEASE=X.Y.Z
gh release delete v${RELEASE} --cleanup-tag
```