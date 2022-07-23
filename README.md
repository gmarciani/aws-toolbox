# AWS Toolbox
AWS Toolbox.

## Requirements
```
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
```

## Usage

### S3

Delete (emptying, if necessary) all buckets whose name matches the provided regular expression:
```
aws-toolbox s3 delete-bucket --name "cdk-hnb659fds-assets-319414405305-(?\!us-east-1|eu-west-1)"
aws-toolbox s3 delete-bucket --name "cdk-hnb659fds-assets-319414405305-(?\!us-east-1|eu-west-1)" --dryrun
```
