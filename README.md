## Customize AWS Config resource tracking in AWS Control Tower environment
This github repository is part of AWS blog post https://aws.amazon.com/blogs/mt/customize-aws-config-resource-tracking-in-aws-control-tower-environment/

Please refer to the blog for what this sample code does and how to use it.

## CloudFormation Parameters

This solution uses CloudFormation parameters to customize the AWS Config Recorder behavior across your Control Tower environment. Parameters are organized into three categories:

### Mandatory Settings

#### CloudFormationVersion
- **Description**: Version number to force stack updates and rerun the solution
- **Type**: String
- **Default**: `1`
- **Usage**: Increment this value whenever you need to force the solution to re-execute across all accounts

#### ExcludedAccounts
- **Description**: List of AWS account IDs to exclude from Config Recorder customization
- **Type**: String (Python list format)
- **Default**: `['111111111111', '222222222222', '333333333333']`
- **Constraints**: 36-4096 characters
- **Required Accounts**: Must include Management account, Log Archive account, and Audit account at minimum
- **Usage**: Replace default values with your actual account IDs that should not have Config Recorder modifications

#### SourceS3Bucket
- **Description**: S3 bucket containing Lambda deployment packages
- **Type**: String
- **Default**: `marketplace-sa-resources`
- **Usage**: Leave as default unless you've customized the Lambda function code and stored it in your own S3 bucket

### Recording Strategy Settings

#### ConfigRecorderStrategy
- **Description**: Strategy for resource recording in AWS Config
- **Type**: String
- **Default**: `EXCLUSION`
- **Allowed Values**: `EXCLUSION`, `INCLUSION`
- **Usage**: 
  - `EXCLUSION`: Record all resources except those specified in `ConfigRecorderExcludedResourceTypes`
  - `INCLUSION`: Only record resources specified in `ConfigRecorderIncludedResourceTypes`

#### ConfigRecorderExcludedResourceTypes
- **Description**: Comma-separated list of AWS resource types to exclude from recording
- **Type**: String
- **Default**: `AWS::HealthLake::FHIRDatastore,AWS::Pinpoint::Segment,AWS::Pinpoint::ApplicationSettings`
- **Usage**: Only applies when `ConfigRecorderStrategy` is set to `EXCLUSION`
- **Example**: `AWS::EC2::Volume,AWS::S3::Bucket,AWS::RDS::DBInstance`

#### ConfigRecorderIncludedResourceTypes
- **Description**: Comma-separated list of AWS resource types to include in recording
- **Type**: String
- **Default**: `AWS::S3::Bucket,AWS::CloudTrail::Trail`
- **Usage**: Only applies when `ConfigRecorderStrategy` is set to `INCLUSION`
- **Example**: `AWS::IAM::Role,AWS::IAM::Policy,AWS::EC2::Instance`

### Recording Frequency Settings

#### ConfigRecorderDefaultRecordingFrequency
- **Description**: Default frequency for recording configuration changes
- **Type**: String
- **Default**: `CONTINUOUS`
- **Allowed Values**: `CONTINUOUS`, `DAILY`
- **Usage**:
  - `CONTINUOUS`: Records configuration changes as they occur (higher AWS Config costs)
  - `DAILY`: Records configuration once per day (lower costs, 24-hour detection delay)

#### ConfigRecorderDailyResourceTypes
- **Description**: Comma-separated list of resource types to record on a daily cadence
- **Type**: String
- **Default**: `AWS::AutoScaling::AutoScalingGroup,AWS::AutoScaling::LaunchConfiguration`
- **Usage**: Resources listed here will be recorded daily regardless of `ConfigRecorderDefaultRecordingFrequency` setting
- **Example**: `AWS::EC2::Volume,AWS::Lambda::Function`

#### ConfigRecorderDailyGlobalResourceTypes
- **Description**: Comma-separated list of global resource types to record daily in the Control Tower home region
- **Type**: String
- **Default**: `AWS::IAM::Policy,AWS::IAM::User,AWS::IAM::Role,AWS::IAM::Group`
- **Usage**: Global resources (IAM, CloudFront, etc.) are only recorded in the home region to avoid duplication
- **Note**: These resources are automatically added to daily recording in the Control Tower home region only

## Usage Examples

### Example 1: Exclude specific high-volume resource types
```yaml
ConfigRecorderStrategy: EXCLUSION
ConfigRecorderExcludedResourceTypes: "AWS::EC2::NetworkInterface,AWS::EC2::Volume,AWS::Lambda::Function"
ConfigRecorderDefaultRecordingFrequency: CONTINUOUS
```

### Example 2: Only track security-critical resources with daily recording
```yaml
ConfigRecorderStrategy: INCLUSION
ConfigRecorderIncludedResourceTypes: "AWS::IAM::Role,AWS::IAM::Policy,AWS::S3::Bucket,AWS::KMS::Key"
ConfigRecorderDefaultRecordingFrequency: DAILY
```

### Example 3: Mixed recording frequencies for cost optimization
```yaml
ConfigRecorderStrategy: EXCLUSION
ConfigRecorderExcludedResourceTypes: "AWS::EC2::NetworkInterface"
ConfigRecorderDefaultRecordingFrequency: DAILY
ConfigRecorderDailyResourceTypes: "AWS::EC2::Instance,AWS::RDS::DBInstance"
```

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
