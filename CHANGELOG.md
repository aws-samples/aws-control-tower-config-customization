# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added `ResetLandingZone` event trigger to ProducerEventTrigger to handle landing zone reset operations
- Documented resource retention policy in README Known Limitations section
- Added explanation of race condition prevention through resource retention

### Changed
- Updated ProducerEventTrigger EventPattern to include `ResetLandingZone` event alongside existing triggers (`UpdateLandingZone`, `CreateManagedAccount`, `UpdateManagedAccount`)

### Documentation
- Added comprehensive "Resource Retention After Stack Deletion" section to README
- Documented all 6 resources with DeletionPolicy: Retain (Lambda Functions, IAM Roles, SQS Queue, Lambda Permissions, Event Source Mapping)
- Added manual cleanup instructions for retained resources
- Clarified that retention prevents race conditions during config rollback operations

## [1.0.0] - Initial Release

### Added
- Initial CloudFormation template for AWS Config resource tracking customization in Control Tower environments
- Producer Lambda function for detecting Control Tower events
- Consumer Lambda function for updating Config Recorder settings
- SQS queue for event processing
- IAM roles and permissions for Lambda execution
- EventBridge rule for triggering on Control Tower lifecycle events
- Support for EXCLUSION and INCLUSION recording strategies
- Support for daily recording frequency for specific resource types
- Configurable excluded accounts list
