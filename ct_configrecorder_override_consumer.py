# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify,merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import boto3
import json
import logging
import botocore.exceptions
import os

ALL_AWS_RESOURCES = 'AWS::EC2::CustomerGateway,AWS::EC2::EIP,AWS::EC2::Host,AWS::EC2::Instance,AWS::EC2::InternetGateway,AWS::EC2::NetworkAcl,AWS::EC2::NetworkInterface,AWS::EC2::RouteTable,AWS::EC2::SecurityGroup,AWS::EC2::Subnet,AWS::CloudTrail::Trail,AWS::EC2::Volume,AWS::EC2::VPC,AWS::EC2::VPNConnection,AWS::EC2::VPNGateway,AWS::EC2::RegisteredHAInstance,AWS::EC2::NatGateway,AWS::EC2::EgressOnlyInternetGateway,AWS::EC2::VPCEndpoint,AWS::EC2::VPCEndpointService,AWS::EC2::FlowLog,AWS::EC2::VPCPeeringConnection,AWS::Elasticsearch::Domain,AWS::IAM::Group,AWS::IAM::Policy,AWS::IAM::Role,AWS::IAM::User,AWS::ElasticLoadBalancingV2::LoadBalancer,AWS::ACM::Certificate,AWS::RDS::DBInstance,AWS::RDS::DBSubnetGroup,AWS::RDS::DBSecurityGroup,AWS::RDS::DBSnapshot,AWS::RDS::DBCluster,AWS::RDS::DBClusterSnapshot,AWS::RDS::EventSubscription,AWS::S3::Bucket,AWS::S3::AccountPublicAccessBlock,AWS::Redshift::Cluster,AWS::Redshift::ClusterSnapshot,AWS::Redshift::ClusterParameterGroup,AWS::Redshift::ClusterSecurityGroup,AWS::Redshift::ClusterSubnetGroup,AWS::Redshift::EventSubscription,AWS::SSM::ManagedInstanceInventory,AWS::CloudWatch::Alarm,AWS::CloudFormation::Stack,AWS::ElasticLoadBalancing::LoadBalancer,AWS::AutoScaling::AutoScalingGroup,AWS::AutoScaling::LaunchConfiguration,AWS::AutoScaling::ScalingPolicy,AWS::AutoScaling::ScheduledAction,AWS::DynamoDB::Table,AWS::CodeBuild::Project,AWS::WAF::RateBasedRule,AWS::WAF::Rule,AWS::WAF::RuleGroup,AWS::WAF::WebACL,AWS::WAFRegional::RateBasedRule,AWS::WAFRegional::Rule,AWS::WAFRegional::RuleGroup,AWS::WAFRegional::WebACL,AWS::CloudFront::Distribution,AWS::CloudFront::StreamingDistribution,AWS::Lambda::Function,AWS::NetworkFirewall::Firewall,AWS::NetworkFirewall::FirewallPolicy,AWS::NetworkFirewall::RuleGroup,AWS::ElasticBeanstalk::Application,AWS::ElasticBeanstalk::ApplicationVersion,AWS::ElasticBeanstalk::Environment,AWS::WAFv2::WebACL,AWS::WAFv2::RuleGroup,AWS::WAFv2::IPSet,AWS::WAFv2::RegexPatternSet,AWS::WAFv2::ManagedRuleSet,AWS::XRay::EncryptionConfig,AWS::SSM::AssociationCompliance,AWS::SSM::PatchCompliance,AWS::Shield::Protection,AWS::ShieldRegional::Protection,AWS::Config::ConformancePackCompliance,AWS::Config::ResourceCompliance,AWS::ApiGateway::Stage,AWS::ApiGateway::RestApi,AWS::ApiGatewayV2::Stage,AWS::ApiGatewayV2::Api,AWS::CodePipeline::Pipeline,AWS::ServiceCatalog::CloudFormationProvisionedProduct,AWS::ServiceCatalog::CloudFormationProduct,AWS::ServiceCatalog::Portfolio,AWS::SQS::Queue,AWS::KMS::Key,AWS::QLDB::Ledger,AWS::SecretsManager::Secret,AWS::SNS::Topic,AWS::SSM::FileData,AWS::Backup::BackupPlan,AWS::Backup::BackupSelection,AWS::Backup::BackupVault,AWS::Backup::RecoveryPoint,AWS::ECR::Repository,AWS::ECS::Cluster,AWS::ECS::Service,AWS::ECS::TaskDefinition,AWS::EFS::AccessPoint,AWS::EFS::FileSystem,AWS::EKS::Cluster,AWS::OpenSearch::Domain,AWS::EC2::TransitGateway,AWS::Kinesis::Stream,AWS::Kinesis::StreamConsumer,AWS::CodeDeploy::Application,AWS::CodeDeploy::DeploymentConfig,AWS::CodeDeploy::DeploymentGroup,AWS::EC2::LaunchTemplate,AWS::ECR::PublicRepository,AWS::GuardDuty::Detector,AWS::EMR::SecurityConfiguration,AWS::SageMaker::CodeRepository,AWS::Route53Resolver::ResolverEndpoint,AWS::Route53Resolver::ResolverRule,AWS::Route53Resolver::ResolverRuleAssociation,AWS::DMS::ReplicationSubnetGroup,AWS::DMS::EventSubscription,AWS::MSK::Cluster,AWS::StepFunctions::Activity,AWS::WorkSpaces::Workspace,AWS::WorkSpaces::ConnectionAlias,AWS::SageMaker::Model,AWS::ElasticLoadBalancingV2::Listener,AWS::StepFunctions::StateMachine,AWS::Batch::JobQueue,AWS::Batch::ComputeEnvironment,AWS::AccessAnalyzer::Analyzer,AWS::Athena::WorkGroup,AWS::Athena::DataCatalog,AWS::Detective::Graph,AWS::GlobalAccelerator::Accelerator,AWS::GlobalAccelerator::EndpointGroup,AWS::GlobalAccelerator::Listener,AWS::EC2::TransitGatewayAttachment,AWS::EC2::TransitGatewayRouteTable,AWS::DMS::Certificate,AWS::AppConfig::Application,AWS::AppSync::GraphQLApi,AWS::DataSync::LocationSMB,AWS::DataSync::LocationFSxLustre,AWS::DataSync::LocationS3,AWS::DataSync::LocationEFS,AWS::DataSync::Task,AWS::DataSync::LocationNFS,AWS::EC2::NetworkInsightsAccessScopeAnalysis,AWS::EKS::FargateProfile,AWS::Glue::Job,AWS::GuardDuty::ThreatIntelSet,AWS::GuardDuty::IPSet,AWS::SageMaker::Workteam,AWS::SageMaker::NotebookInstanceLifecycleConfig,AWS::ServiceDiscovery::Service,AWS::ServiceDiscovery::PublicDnsNamespace,AWS::SES::ContactList,AWS::SES::ConfigurationSet,AWS::Route53::HostedZone,AWS::IoTEvents::Input,AWS::IoTEvents::DetectorModel,AWS::IoTEvents::AlarmModel,AWS::ServiceDiscovery::HttpNamespace,AWS::Events::EventBus,AWS::ImageBuilder::ContainerRecipe,AWS::ImageBuilder::DistributionConfiguration,AWS::ImageBuilder::InfrastructureConfiguration,AWS::DataSync::LocationObjectStorage,AWS::DataSync::LocationHDFS,AWS::Glue::Classifier,AWS::Route53RecoveryReadiness::Cell,AWS::Route53RecoveryReadiness::ReadinessCheck,AWS::ECR::RegistryPolicy,AWS::Backup::ReportPlan,AWS::Lightsail::Certificate,AWS::RUM::AppMonitor,AWS::Events::Endpoint,AWS::SES::ReceiptRuleSet,AWS::Events::Archive,AWS::Events::ApiDestination,AWS::Lightsail::Disk,AWS::FIS::ExperimentTemplate,AWS::DataSync::LocationFSxWindows,AWS::SES::ReceiptFilter,AWS::GuardDuty::Filter,AWS::SES::Template,AWS::AmazonMQ::Broker,AWS::AppConfig::Environment,AWS::AppConfig::ConfigurationProfile,AWS::Cloud9::EnvironmentEC2,AWS::EventSchemas::Registry,AWS::EventSchemas::RegistryPolicy,AWS::EventSchemas::Discoverer,AWS::FraudDetector::Label,AWS::FraudDetector::EntityType,AWS::FraudDetector::Variable,AWS::FraudDetector::Outcome,AWS::IoT::Authorizer,AWS::IoT::SecurityProfile,AWS::IoT::RoleAlias,AWS::IoT::Dimension,AWS::IoTAnalytics::Datastore,AWS::Lightsail::Bucket,AWS::Lightsail::StaticIp,AWS::MediaPackage::PackagingGroup,AWS::Route53RecoveryReadiness::RecoveryGroup,AWS::ResilienceHub::ResiliencyPolicy,AWS::Transfer::Workflow,AWS::EKS::IdentityProviderConfig,AWS::EKS::Addon,AWS::Glue::MLTransform,AWS::IoT::Policy,AWS::IoT::MitigationAction,AWS::IoTTwinMaker::Workspace,AWS::IoTTwinMaker::Entity,AWS::IoTAnalytics::Dataset,AWS::IoTAnalytics::Pipeline,AWS::IoTAnalytics::Channel,AWS::IoTSiteWise::Dashboard,AWS::IoTSiteWise::Project,AWS::IoTSiteWise::Portal,AWS::IoTSiteWise::AssetModel,AWS::IVS::Channel,AWS::IVS::RecordingConfiguration,AWS::IVS::PlaybackKeyPair,AWS::KinesisAnalyticsV2::Application,AWS::RDS::GlobalCluster,AWS::S3::MultiRegionAccessPoint,AWS::DeviceFarm::TestGridProject,AWS::Budgets::BudgetsAction,AWS::Lex::Bot,AWS::CodeGuruReviewer::RepositoryAssociation,AWS::IoT::CustomMetric,AWS::Route53Resolver::FirewallDomainList,AWS::RoboMaker::RobotApplicationVersion,AWS::EC2::TrafficMirrorSession,AWS::IoTSiteWise::Gateway,AWS::Lex::BotAlias,AWS::LookoutMetrics::Alert,AWS::IoT::AccountAuditConfiguration,AWS::EC2::TrafficMirrorTarget,AWS::S3::StorageLens,AWS::IoT::ScheduledAudit,AWS::Events::Connection,AWS::EventSchemas::Schema,AWS::MediaPackage::PackagingConfiguration,AWS::KinesisVideo::SignalingChannel,AWS::AppStream::DirectoryConfig,AWS::LookoutVision::Project,AWS::Route53RecoveryControl::Cluster,AWS::Route53RecoveryControl::SafetyRule,AWS::Route53RecoveryControl::ControlPanel,AWS::Route53RecoveryControl::RoutingControl,AWS::Route53RecoveryReadiness::ResourceSet,AWS::RoboMaker::SimulationApplication,AWS::RoboMaker::RobotApplication,AWS::HealthLake::FHIRDatastore,AWS::Pinpoint::Segment,AWS::Pinpoint::ApplicationSettings,AWS::Events::Rule,AWS::EC2::DHCPOptions,AWS::EC2::NetworkInsightsPath,AWS::EC2::TrafficMirrorFilter,AWS::EC2::IPAM,AWS::IoTTwinMaker::Scene,AWS::NetworkManager::TransitGatewayRegistration,AWS::CustomerProfiles::Domain,AWS::AutoScaling::WarmPool,AWS::Connect::PhoneNumber,AWS::AppConfig::DeploymentStrategy,AWS::AppFlow::Flow,AWS::AuditManager::Assessment,AWS::CloudWatch::MetricStream,AWS::DeviceFarm::InstanceProfile,AWS::DeviceFarm::Project,AWS::EC2::EC2Fleet,AWS::EC2::SubnetRouteTableAssociation,AWS::ECR::PullThroughCacheRule,AWS::GroundStation::Config,AWS::ImageBuilder::ImagePipeline,AWS::IoT::FleetMetric,AWS::IoTWireless::ServiceProfile,AWS::NetworkManager::Device,AWS::NetworkManager::GlobalNetwork,AWS::NetworkManager::Link,AWS::NetworkManager::Site,AWS::Panorama::Package,AWS::Pinpoint::App,AWS::Redshift::ScheduledAction,AWS::Route53Resolver::FirewallRuleGroupAssociation,AWS::SageMaker::AppImageConfig,AWS::SageMaker::Image,AWS::ECS::TaskSet,AWS::Cassandra::Keyspace,AWS::Signer::SigningProfile,AWS::Amplify::App,AWS::AppMesh::VirtualNode,AWS::AppMesh::VirtualService,AWS::AppRunner::VpcConnector,AWS::AppStream::Application,AWS::CodeArtifact::Repository,AWS::EC2::PrefixList,AWS::EC2::SpotFleet,AWS::Evidently::Project,AWS::Forecast::Dataset,AWS::IAM::SAMLProvider,AWS::IAM::ServerCertificate,AWS::Pinpoint::Campaign,AWS::Pinpoint::InAppTemplate,AWS::SageMaker::Domain,AWS::Transfer::Agreement,AWS::Transfer::Connector,AWS::KinesisFirehose::DeliveryStream,AWS::Amplify::Branch,AWS::AppIntegrations::EventIntegration,AWS::AppMesh::Route,AWS::Athena::PreparedStatement,AWS::EC2::IPAMScope,AWS::Evidently::Launch,AWS::Forecast::DatasetGroup,AWS::GreengrassV2::ComponentVersion,AWS::GroundStation::MissionProfile,AWS::MediaConnect::FlowEntitlement,AWS::MediaConnect::FlowVpcInterface,AWS::MediaTailor::PlaybackConfiguration,AWS::MSK::Configuration,AWS::Personalize::Dataset,AWS::Personalize::Schema,AWS::Personalize::Solution,AWS::Pinpoint::EmailTemplate,AWS::Pinpoint::EventStream,AWS::ResilienceHub::App,AWS::ACMPCA::CertificateAuthority,AWS::AppConfig::HostedConfigurationVersion,AWS::AppMesh::VirtualGateway,AWS::AppMesh::VirtualRouter,AWS::AppRunner::Service,AWS::CustomerProfiles::ObjectType,AWS::DMS::Endpoint,AWS::EC2::CapacityReservation,AWS::EC2::ClientVpnEndpoint,AWS::Kendra::Index,AWS::KinesisVideo::Stream,AWS::Logs::Destination,AWS::Pinpoint::EmailChannel,AWS::S3::AccessPoint,AWS::NetworkManager::CustomerGatewayAssociation,AWS::NetworkManager::LinkAssociation,AWS::IoTWireless::MulticastGroup,AWS::Personalize::DatasetGroup,AWS::IoTTwinMaker::ComponentType,AWS::CodeBuild::ReportGroup,AWS::SageMaker::FeatureGroup,AWS::MSK::BatchScramSecret,AWS::AppStream::Stack,AWS::IoT::JobTemplate,AWS::IoTWireless::FuotaTask,AWS::IoT::ProvisioningTemplate,AWS::InspectorV2::Filter,AWS::Route53Resolver::ResolverQueryLoggingConfigAssociation,AWS::ServiceDiscovery::Instance,AWS::Transfer::Certificate,AWS::MediaConnect::FlowSource,AWS::APS::RuleGroupsNamespace,AWS::CodeGuruProfiler::ProfilingGroup,AWS::Route53Resolver::ResolverQueryLoggingConfig,AWS::Batch::SchedulingPolicy,AWS::ACMPCA::CertificateAuthorityActivation,AWS::AppMesh::GatewayRoute,AWS::AppMesh::Mesh,AWS::Connect::Instance,AWS::Connect::QuickConnect,AWS::EC2::CarrierGateway,AWS::EC2::IPAMPool,AWS::EC2::TransitGatewayConnect,AWS::EC2::TransitGatewayMulticastDomain,AWS::ECS::CapacityProvider,AWS::IAM::InstanceProfile,AWS::IoT::CACertificate,AWS::IoTTwinMaker::SyncJob,AWS::KafkaConnect::Connector,AWS::Lambda::CodeSigningConfig,AWS::NetworkManager::ConnectPeer,AWS::ResourceExplorer2::Index,AWS::AppStream::Fleet,AWS::Cognito::UserPool,AWS::Cognito::UserPoolClient,AWS::Cognito::UserPoolGroup,AWS::EC2::NetworkInsightsAccessScope,AWS::EC2::NetworkInsightsAnalysis,AWS::Grafana::Workspace,AWS::GroundStation::DataflowEndpointGroup,AWS::ImageBuilder::ImageRecipe,AWS::KMS::Alias,AWS::M2::Environment,AWS::QuickSight::DataSource,AWS::QuickSight::Template,AWS::QuickSight::Theme,AWS::RDS::OptionGroup,AWS::Redshift::EndpointAccess,AWS::Route53Resolver::FirewallRuleGroup,AWS::SSM::Document,AWS::AppConfig::ExtensionAssociation,AWS::DMS::ReplicationInstance,AWS::DMS::ReplicationTask,AWS::MSK::ClusterPolicy,AWS::MSK::VpcConnection,AWS::Redshift::ClusterSubnetGroup,AWS::NetworkFirewall::TLSInspectionConfiguration,AWS::Redshift::EndpointAuthorization,AWS::SageMaker::EndpointConfig,AWS::SageMaker::NotebookInstance,AWS::Transfer::Profile'

def lambda_handler(event, context):


    LOG_LEVEL = os.getenv('LOG_LEVEL')
    logging.getLogger().setLevel(LOG_LEVEL)

    try:

        logging.info('Event Body:')

        body = json.loads(event['Records'][0]['body'])
        account_id = body['Account']
        aws_region = body['Region']
        event = body['Event']

        logging.info(f'Extracted Account: {account_id}')
        logging.info(f'Extracted Region: {aws_region}')
        logging.info(f'Extracted Event: {event}')

        bc = botocore.__version__
        b3 = boto3.__version__

        logging.info(f'Botocore : {bc}')
        logging.info(f'Boto3 : {b3}')

        STS = boto3.client("sts")

        def assume_role(account_id, role='AWSControlTowerExecution'):
            '''
            Return a session in the target account using Control Tower Role
            '''
            try:
                curr_account = STS.get_caller_identity()['Account']
                if curr_account != account_id:
                    part = STS.get_caller_identity()['Arn'].split(":")[1]

                    role_arn = 'arn:' + part + ':iam::' + account_id + ':role/' + role
                    ses_name = str(account_id + '-' + role)
                    response = STS.assume_role(RoleArn=role_arn, RoleSessionName=ses_name)
                    sts_session = boto3.Session(
                        aws_access_key_id=response['Credentials']['AccessKeyId'],
                        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                        aws_session_token=response['Credentials']['SessionToken'])

                    return sts_session
            except botocore.exceptions.ClientError as exe:
                logging.error('Unable to assume role')
                raise exe

        sts_session = assume_role(account_id)
        logging.info(f'Printing STS session: {sts_session}')

        # Use the session and create a client for configservice
        configservice = sts_session.client('config', region_name=aws_region)

        # Describe configuration recorder
        configrecorder = configservice.describe_configuration_recorders()
        logging.info(f'Existing Configuration Recorder :', configrecorder)

        # ControlTower created configuration recorder with name "aws-controltower-BaselineConfigRecorder" and we will update just that
        try:
            role_arn = 'arn:aws:iam::' + account_id + ':role/aws-controltower-ConfigRecorderRole'

            CONFIG_RECORDER_EXCLUSION_RESOURCE_STRING = os.getenv('CONFIG_RECORDER_EXCLUDED_RESOURCE_LIST')
            if CONFIG_RECORDER_EXCLUSION_RESOURCE_STRING.lower() == "all":
                CONFIG_RECORDER_EXCLUSION_RESOURCE_STRING = ALL_AWS_RESOURCES

            logging.info(f'Excluding resources: {CONFIG_RECORDER_EXCLUSION_RESOURCE_STRING}')

            CONFIG_RECORDER_EXCLUSION_RESOURCE_LIST = CONFIG_RECORDER_EXCLUSION_RESOURCE_STRING.split(',')

            # Event = Delete is when stack is deleted, we rollback changed made and leave it as ControlTower Intended
            if event == 'Delete':
                response = configservice.put_configuration_recorder(
                    ConfigurationRecorder={
                        'name': 'aws-controltower-BaselineConfigRecorder',
                        'roleARN': role_arn,
                        'recordingGroup': {
                            'allSupported': True,
                            'includeGlobalResourceTypes': False
                        }
                    })
                logging.info(f'Response for put_configuration_recorder :{response} ')

            else:
                response = configservice.put_configuration_recorder(
                    ConfigurationRecorder={
                        'name': 'aws-controltower-BaselineConfigRecorder',
                        'roleARN': role_arn,
                        'recordingGroup': {
                            'allSupported': False,
                            'includeGlobalResourceTypes': False,
                            'exclusionByResourceTypes': {
                                'resourceTypes': CONFIG_RECORDER_EXCLUSION_RESOURCE_LIST
                            },
                            'recordingStrategy': {
                                'useOnly': 'EXCLUSION_BY_RESOURCE_TYPES'
                            }
                        }
                    })
                logging.info(f'Response for put_configuration_recorder :{response} ')

            # lets describe for configuration recorder after the update
            configrecorder = configservice.describe_configuration_recorders()
            logging.info(f'Post Change Configuration recorder : {configrecorder}')

        except botocore.exceptions.ClientError as exe:
            logging.error('Unable to Update Config Recorder for Account and Region : ', account_id, aws_region)
            configrecorder = configservice.describe_configuration_recorders()
            logging.info(f'Exception : {configrecorder}')
            raise exe

        return {
            'statusCode': 200
        }

    except Exception as e:
        exception_type = e.__class__.__name__
        exception_message = str(e)
        logging.exception(f'{exception_type}: {exception_message}')
