 # AWS Toolbox
AWS Toolbox extends the AWS CLI commands with some handy solutions, such as
executing a command on every region and resources matching a given pattern.

## Installation
```
pip install aws-toolbox
```

## Usage

### DryRun Mode
Every command can be executed in dryrun mode, by adding the option `--dryrun`.
With dryrun mode, the actual AWS operations will be logged but not executed.

For example:
```
~> aws-toolbox s3 delete-bucket --name "integ-tests-.*" --dryrun
INFO:aws_toolbox.commands.s3.delete_bucket:Deleting Buckets with name pattern integ-tests-.*, dryrun True
INFO:botocore.credentials:Found credentials in shared credentials file: ~/.aws/credentials
INFO:aws_toolbox.commands.s3.delete_bucket:The following 2 buckets would be deleted, but dryrun mode is enabled and nothing will be done: test-1, test-2, test-3
```

### S3
Delete (emptying, if necessary) all buckets whose name matches the provided regular expression:
```
aws-toolbox s3 delete-bucket \
  --name "cdk-hnb659fds-assets-319414405305-(?\!us-east-1|eu-west-1)"
```

### Secrets Manager
List all secrets whose name and regions match the provided regular expressions:
```
aws-toolbox secretsmanager list-secrets \
  --region "us-west-.*" \
  --name ".*"
```

Delete all secrets whose name and regions match the provided regular expressions:
```
aws-toolbox secretsmanager delete-secrets \
  --region "us-west-.*" \
  --name "Sample.*"
```

### EC2 AMIs
```
aws-toolbox ec2 delete-ami \
  --region "eu-.*" \
  --owners 319414405305 \
  --name ".*aws-parallelcluster.*" \
  --before 2023-06-01T00:00:00.000Z
```

### EC2 Snapshots
Delete (emptying, if necessary) all snapshots whose name matches the provided regular expression:
```
aws-toolbox ec2 delete-snapshot \
  --region "eu-.*" \
  --owners 319414405305 \
  --description "Copied for DestinationAmi .*"
```

### CloudFormation Stacks
Delete all stacks whose name and region matches the provided patterns and have been created before given datetime:
```
aws-toolbox cloudformation delete-stacks \
  --region "us-.*" \
  --name "aws-parallelcluster-3-8-0-amzn2.*" 
  --before 2023-12-01T00:00:00.000Z
```
