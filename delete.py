# ['805741416284','326930160498', '255007049728']

import boto3
import json
import botocore
print(botocore.__version__)
print(boto3.__version__)

account_id = '476494407737'
aws_region = 'us-west-2'
event = 'Update'
CONFIG_RECORDER_EXCLUSION_RESOURCE_STRING = 'AWS::HealthLake::FHIRDatastore,AWS::Pinpoint::Segment,AWS::Pinpoint::ApplicationSettings'

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
    except:
        print('Unable to assume role')
        pass


sts_session = assume_role(account_id)
print(f'Printing STS session: {sts_session}')

# Use the session and create a client for configservice
configservice = sts_session.client('config', region_name=aws_region)

# Describe for config recorder
configrecorder = configservice.describe_configuration_recorders()
print(f'Existing Configuration Recorder :', configrecorder)

# ControlTower created configuration recorder with name "aws-controltower-BaselineConfigRecorder" update that
role_arn = 'arn:aws:iam::' + account_id + ':role/aws-controltower-ConfigRecorderRole'

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
    print(response)
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
    print(f'Response for put_configuration_recorder :{response} ')

# Describe for configuration recorder after the update
configrecorder = configservice.describe_configuration_recorders()
print(f'Post Change Configuration recorder : {configrecorder}')
