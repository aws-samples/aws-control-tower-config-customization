## Customize AWS Config resource tracking in AWS Control Tower environment
This github repository is part of AWS blog post https://aws.amazon.com/blogs/mt/customize-aws-config-resource-tracking-in-aws-control-tower-environment/

Please refer to the blog for what this sample code does and how to use it.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.


## Known limitations

### Resource Retention After Stack Deletion

When you delete the CloudFormation stack, the following resources are intentionally retained to prevent race conditions and allow for complete rollback of AWS Config settings to their default Control Tower configuration:

- **Lambda Functions**: `ProducerLambda` and `ConsumerLambda`
- **Lambda Permissions**: `ProducerLambdaPermissions`
- **Lambda Event Source Mapping**: `ConsumerLambdaEventSourceMapping`
- **IAM Roles**: `ProducerLambdaExecutionRole` and `ConsumerLambdaExecutionRole`
- **SQS Queue**: `SQSConfigRecorder`

**Important**: These retained resources will continue to incur minimal costs. If you want to completely remove all resources after stack deletion, you must manually delete these retained resources from the AWS Console or using the AWS CLI.

To manually clean up retained resources after stack deletion:
1. Delete the Lambda functions via the Lambda console
2. Delete the IAM roles via the IAM console
3. Delete the SQS queue via the SQS console
4. Lambda permissions and event source mappings will be automatically removed when their associated functions are deleted


## License

This library is licensed under the MIT-0 License. See the LICENSE file.
