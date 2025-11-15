# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-15

### Added
- Added `ResetLandingZone` event trigger to ProducerEventTrigger to handle landing zone reset operations
- Documented resource retention policy in README Known Limitations section
- Added explanation of race condition prevention through resource retention

### Changed
- Updated ProducerEventTrigger EventPattern to include `ResetLandingZone` event alongside existing triggers (`UpdateLandingZone`, `CreateManagedAccount`, `UpdateManagedAccount`)

### Fixed
- Corrected incorrect log lines in consumer and producer Lambda functions ([#33](https://github.com/aws-samples/aws-control-tower-config-customization/pull/33))
- Fixed STS client to use regional endpoints for opt-in regions support - prevents `UnrecognizedClientException` in opt-in regions (me-south-1, ap-east-1, etc.)

### Documentation
- Added comprehensive "Resource Retention After Stack Deletion" section to README
- Documented all 6 resources with DeletionPolicy: Retain (Lambda Functions, IAM Roles, SQS Queue, Lambda Permissions, Event Source Mapping)
- Added manual cleanup instructions for retained resources
- Clarified that retention prevents race conditions during config rollback operations

## [1.0.0] - 2024

### Added
- Flexibility for AWS Config recording strategies supporting both INCLUSION and EXCLUSION lists for resource types
- `ConfigRecorderIncludedResourceTypes` parameter for inclusion-based recording
- `ConfigRecorderExcludedResourceTypes` parameter for exclusion-based recording
- Support for daily recording frequency for specific resource types ([#13](https://github.com/aws-samples/aws-control-tower-config-customization/pull/13))
- `ConfigRecorderDailyResourceTypes` parameter for resources recorded on daily cadence
- `ConfigRecorderDailyGlobalResourceTypes` parameter for global resources in Control Tower home region
- `ConfigRecorderDefaultRecordingFrequency` parameter (CONTINUOUS or DAILY)

### Fixed
- Maximum number of configuration recorders exceeded exception by using existing recorder name ([#24](https://github.com/aws-samples/aws-control-tower-config-customization/pull/24))
- Global resource recording now correctly limited to Control Tower home region ([#19](https://github.com/aws-samples/aws-control-tower-config-customization/pull/19))
- `includeGlobalResourceTypes` value properly set to true only in home region

### Changed
- Updated IAM role handling for configuration recorder

## [0.1.0] - Initial Release

### Added
- Initial CloudFormation template for AWS Config resource tracking customization in Control Tower environments
- Producer Lambda function for detecting Control Tower events
- Consumer Lambda function for updating Config Recorder settings
- SQS queue for event processing
- IAM roles and permissions for Lambda execution
- EventBridge rule for triggering on Control Tower lifecycle events
- Support for resource exclusion in Config Recorder
- Configurable excluded accounts list
