## Customize AWS Config resource tracking in AWS Control Tower environment
This github repository is part of AWS blog post https://aws.amazon.com/blogs/mt/customize-aws-config-resource-tracking-in-aws-control-tower-environment/

Please refer to the blog for what this sample code does and how to use it.

## CloudFormation Parameters

This solution uses CloudFormation parameters to customize the AWS Config Recorder behavior across your Control Tower environment. Parameters are organized into four categories:

## Account Selection Modes

This solution supports two modes for selecting which AWS accounts receive Config Recorder customizations:

### EXCLUSION Mode (Default)
In **EXCLUSION mode**, the solution applies Config Recorder changes to **all Control Tower managed accounts except** those explicitly listed in the `ExcludedAccounts` parameter. This is the default behavior and is ideal when you want to customize most accounts while protecting a few critical accounts.

**When to use EXCLUSION mode:**
- You want to apply Config Recorder customizations to the majority of your accounts
- You have a small number of accounts that should maintain default Control Tower Config settings
- You want to protect specific accounts (Management, Log Archive, Audit) from modifications

### INCLUSION Mode
In **INCLUSION mode**, the solution applies Config Recorder changes **only to accounts** explicitly listed in the `IncludedAccounts` parameter. All other accounts are automatically excluded. This mode is ideal when you want precise control over a specific subset of accounts.

**When to use INCLUSION mode:**
- You want to apply Config Recorder customizations to only a few specific accounts
- You're testing the solution in a limited scope before broader rollout
- You have a small number of workload accounts that need customization
- You want explicit control over which accounts are affected

### Important Warning

⚠️ **Critical Accounts**: Regardless of which mode you use, you should typically **NOT** include the following accounts in your customizations:
- **Management Account**: The Control Tower management account
- **Log Archive Account**: The centralized logging account
- **Audit Account**: The security audit account

These accounts have special roles in Control Tower governance and should generally maintain their default AWS Config Recorder settings to ensure proper Control Tower functionality.

### Mandatory Settings

#### CloudFormationVersion
- **Description**: Version number to force stack updates and rerun the solution
- **Type**: String
- **Default**: `1`
- **Usage**: Increment this value whenever you need to force the solution to re-execute across all accounts

#### SourceS3Bucket
- **Description**: S3 bucket containing Lambda deployment packages
- **Type**: String
- **Default**: `marketplace-sa-resources`
- **Usage**: Leave as default unless you've customized the Lambda function code and stored it in your own S3 bucket

### Account Selection Settings

#### AccountSelectionMode
- **Description**: Determines whether to use exclusion or inclusion mode for account targeting
- **Type**: String
- **Default**: `EXCLUSION`
- **Allowed Values**: `EXCLUSION`, `INCLUSION`
- **Usage**: 
  - `EXCLUSION`: Apply Config Recorder changes to all accounts except those in `ExcludedAccounts`
  - `INCLUSION`: Apply Config Recorder changes only to accounts in `IncludedAccounts`
- **Backward Compatibility**: Defaults to `EXCLUSION` to maintain existing behavior for upgraded deployments

#### ExcludedAccounts
- **Description**: List of AWS account IDs to exclude from Config Recorder customization
- **Type**: String (Python list format)
- **Default**: `['111111111111', '222222222222', '333333333333']`
- **Constraints**: 36-4096 characters
- **When Used**: Only applies when `AccountSelectionMode` is set to `EXCLUSION`
- **Required Accounts**: Should include Management account, Log Archive account, and Audit account at minimum
- **Usage**: Replace default values with your actual account IDs that should not have Config Recorder modifications
- **Example**: `['123456789012', '234567890123', '345678901234']`

#### IncludedAccounts
- **Description**: List of AWS account IDs to include for Config Recorder customization
- **Type**: String (Python list format)
- **Default**: `[]` (empty list)
- **Constraints**: 2-4096 characters
- **When Used**: Only applies when `AccountSelectionMode` is set to `INCLUSION`
- **Usage**: Specify the exact accounts that should receive Config Recorder customizations
- **Example**: `['123456789012', '234567890123']`
- **Note**: If empty while in INCLUSION mode, no accounts will be processed

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

### Example 4: Using INCLUSION mode to target specific workload accounts
```yaml
AccountSelectionMode: INCLUSION
IncludedAccounts: "['123456789012', '234567890123', '345678901234']"
ConfigRecorderStrategy: EXCLUSION
ConfigRecorderExcludedResourceTypes: "AWS::EC2::NetworkInterface,AWS::EC2::Volume"
ConfigRecorderDefaultRecordingFrequency: CONTINUOUS
```
**Use case**: Apply Config Recorder customizations only to three specific workload accounts while leaving all other accounts with default Control Tower settings.

### Example 5: Using EXCLUSION mode (default behavior)
```yaml
AccountSelectionMode: EXCLUSION
ExcludedAccounts: "['111111111111', '222222222222', '333333333333']"
ConfigRecorderStrategy: INCLUSION
ConfigRecorderIncludedResourceTypes: "AWS::IAM::Role,AWS::IAM::Policy,AWS::S3::Bucket"
ConfigRecorderDefaultRecordingFrequency: DAILY
```
**Use case**: Apply Config Recorder customizations to all Control Tower accounts except the Management, Log Archive, and Audit accounts (replace with your actual account IDs).

### Example 6: Switching from EXCLUSION to INCLUSION mode
If you have an existing deployment using EXCLUSION mode and want to switch to INCLUSION mode:

**Current configuration (EXCLUSION mode):**
```yaml
AccountSelectionMode: EXCLUSION
ExcludedAccounts: "['111111111111', '222222222222', '333333333333']"
```

**New configuration (INCLUSION mode):**
```yaml
AccountSelectionMode: INCLUSION
IncludedAccounts: "['123456789012', '234567890123']"
# ExcludedAccounts parameter is ignored when AccountSelectionMode is INCLUSION
```

**Steps to switch:**
1. Identify all Control Tower managed accounts in your organization
2. Determine which specific accounts need Config Recorder customizations
3. Update the CloudFormation stack with:
   - `AccountSelectionMode` set to `INCLUSION`
   - `IncludedAccounts` set to your target account list
4. The `ExcludedAccounts` parameter will be ignored in INCLUSION mode

## Backward Compatibility

This solution maintains full backward compatibility with existing deployments:

### Upgrading Existing Deployments

When you update an existing CloudFormation stack to a newer version of this solution:

- **No parameter changes required**: The stack will continue to operate in EXCLUSION mode with your existing `ExcludedAccounts` configuration
- **Default behavior preserved**: `AccountSelectionMode` defaults to `EXCLUSION`, maintaining identical behavior to previous versions
- **Zero-risk upgrade**: Simply updating the stack without changing parameters will not alter which accounts receive Config Recorder customizations
- **Gradual adoption**: You can adopt INCLUSION mode at your own pace by explicitly changing the `AccountSelectionMode` parameter

### Parameter Behavior by Mode

| Parameter | Used in EXCLUSION Mode | Used in INCLUSION Mode |
|-----------|------------------------|------------------------|
| `AccountSelectionMode` | ✅ Required (set to `EXCLUSION`) | ✅ Required (set to `INCLUSION`) |
| `ExcludedAccounts` | ✅ Used to filter accounts | ❌ Ignored |
| `IncludedAccounts` | ❌ Ignored | ✅ Used to filter accounts |

### Migration Safety

- **EXCLUSION to INCLUSION**: Switching modes requires explicit parameter changes - no accidental mode switches
- **INCLUSION to EXCLUSION**: Can switch back at any time by changing `AccountSelectionMode` to `EXCLUSION`
- **Empty lists**: 
  - Empty `ExcludedAccounts` in EXCLUSION mode = all accounts processed (safe default)
  - Empty `IncludedAccounts` in INCLUSION mode = no accounts processed (safe default)

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
