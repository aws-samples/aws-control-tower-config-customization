#
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


def lambda_handler(event, context):
    LOG_LEVEL = os.getenv('LOG_LEVEL')
    logging.getLogger().setLevel(LOG_LEVEL)

    try:
        logging.info(f'Event: {str(event).replace(chr(10), "").replace(chr(13), "")}')

        body = json.loads(event['Records'][0]['body'])
        account_id = body['Account']
        aws_region = body['Region']
        event = body['Event']

        logging.info(f'Extracted Account: {str(account_id).replace(chr(10), "").replace(chr(13), "")}')
        logging.info(f'Extracted Region: {str(aws_region).replace(chr(10), "").replace(chr(13), "")}')
        logging.info(f'Extracted Event: {str(event).replace(chr(10), "").replace(chr(13), "")}')

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
        logging.info(f'Existing Configuration Recorder: {configrecorder}')

        # Get the name of the existing recorder if it exists, otherwise use the default name
        recorder_name = 'aws-controltower-BaselineConfigRecorder'
        if configrecorder and 'ConfigurationRecorders' in configrecorder and len(configrecorder['ConfigurationRecorders']) > 0:
            recorder_name = configrecorder['ConfigurationRecorders'][0]['name']
            logging.info(f'Using existing recorder name: {recorder_name}')

        # ControlTower created configuration recorder with name "aws-controltower-BaselineConfigRecorder" and we will update just that
        try:
            role_arn = 'arn:aws:iam::' + account_id + ':role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig'

            CONFIG_RECORDER_DAILY_RESOURCE_STRING = os.getenv('CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST', '')
            CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST = CONFIG_RECORDER_DAILY_RESOURCE_STRING.split(
                ',') if CONFIG_RECORDER_DAILY_RESOURCE_STRING != '' else []
            
            CONFIG_RECORDER_DAILY_GLOBAL_RESOURCE_STRING = os.getenv('CONFIG_RECORDER_OVERRIDE_DAILY_GLOBAL_RESOURCE_LIST', '')
            CONFIG_RECORDER_DAILY_GLOBAL_RESOURCE_LIST = CONFIG_RECORDER_DAILY_GLOBAL_RESOURCE_STRING.split(
                ',') if CONFIG_RECORDER_DAILY_GLOBAL_RESOURCE_STRING != '' else []
            
            # Get resource lists for both strategies
            CONFIG_RECORDER_STRATEGY = os.getenv('CONFIG_RECORDER_STRATEGY', 'EXCLUSION')
            
            # Get exclusion list (original behavior)
            CONFIG_RECORDER_EXCLUSION_RESOURCE_STRING = os.getenv('CONFIG_RECORDER_OVERRIDE_EXCLUDED_RESOURCE_LIST', '')
            CONFIG_RECORDER_EXCLUSION_RESOURCE_LIST = CONFIG_RECORDER_EXCLUSION_RESOURCE_STRING.split(
                ',') if CONFIG_RECORDER_EXCLUSION_RESOURCE_STRING != '' else []
            
            # Get inclusion list (new behavior)
            CONFIG_RECORDER_INCLUSION_RESOURCE_STRING = os.getenv('CONFIG_RECORDER_OVERRIDE_INCLUDED_RESOURCE_LIST', '')
            CONFIG_RECORDER_INCLUSION_RESOURCE_LIST = CONFIG_RECORDER_INCLUSION_RESOURCE_STRING.split(
                ',') if CONFIG_RECORDER_INCLUSION_RESOURCE_STRING != '' else []
            
            CONFIG_RECORDER_DEFAULT_RECORDING_FREQUENCY = os.getenv('CONFIG_RECORDER_DEFAULT_RECORDING_FREQUENCY')

            # For exclusion strategy, remove any resource type from daily list that are in exclusion list
            if CONFIG_RECORDER_STRATEGY == 'EXCLUSION':
                res = [x for x in CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST if x not in CONFIG_RECORDER_EXCLUSION_RESOURCE_LIST]
                CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST[:] = res
            else:  # For inclusion strategy, make sure all daily resources are in the inclusion list
                for resource_type in CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST:
                    if resource_type not in CONFIG_RECORDER_INCLUSION_RESOURCE_LIST:
                        CONFIG_RECORDER_INCLUSION_RESOURCE_LIST.append(resource_type)

            # Event = Delete is when stack is deleted, we rollback changed made and leave it as ControlTower Intended
            home_region = os.getenv('CONTROL_TOWER_HOME_REGION') == aws_region
            if home_region:
                CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST += CONFIG_RECORDER_DAILY_GLOBAL_RESOURCE_LIST

            if event == 'Delete':
                response = configservice.put_configuration_recorder(
                    ConfigurationRecorder={
                        'name': recorder_name,
                        'roleARN': role_arn,
                        'recordingGroup': {
                            'allSupported': True,
                            'includeGlobalResourceTypes': home_region
                        }
                    })
                logging.info(f'Response for put_configuration_recorder :{response} ')

            else:
                if CONFIG_RECORDER_STRATEGY == 'EXCLUSION':
                    # Original exclusion-based code - EXACTLY as in the working version
                    logging.info(f'Using EXCLUSION strategy')
                    logging.info(f'Exclusion resource list: {CONFIG_RECORDER_EXCLUSION_RESOURCE_LIST}')
                    logging.info(f'Daily override resource list: {CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST}')
                    
                    config_recorder = {
                        'name': recorder_name,
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
                        },
                        'recordingMode': {
                            'recordingFrequency': CONFIG_RECORDER_DEFAULT_RECORDING_FREQUENCY,
                            'recordingModeOverrides': [
                                {
                                    'description': 'DAILY_OVERRIDE',
                                    'resourceTypes': CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST,
                                    'recordingFrequency': 'DAILY'
                                }
                            ] if CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST else []
                        }
                    }

                    if not CONFIG_RECORDER_EXCLUSION_RESOURCE_LIST:
                        config_recorder['recordingGroup'].pop('exclusionByResourceTypes')
                        config_recorder['recordingGroup'].pop('recordingStrategy')
                        config_recorder['recordingGroup']['allSupported'] = True
                        config_recorder['recordingGroup']['includeGlobalResourceTypes'] = True
                else:
                    # New inclusion-based code
                    logging.info(f'Using INCLUSION strategy')
                    # Make sure all resources in daily overrides are also in the inclusion list
                    for resource_type in CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST:
                        if resource_type not in CONFIG_RECORDER_INCLUSION_RESOURCE_LIST:
                            CONFIG_RECORDER_INCLUSION_RESOURCE_LIST.append(resource_type)
   
                    logging.info(f'Inclusion resource list: {CONFIG_RECORDER_INCLUSION_RESOURCE_LIST}')
                    logging.info(f'Daily override resource list: {CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST}')
                    
                    config_recorder = {
                        'name': recorder_name,
                        'roleARN': role_arn
                    }
                    
                    # Set up recording group
                    if not CONFIG_RECORDER_INCLUSION_RESOURCE_LIST:
                        config_recorder['recordingGroup'] = {
                            'allSupported': False,
                            'includeGlobalResourceTypes': False
                        }
                    else:
                        config_recorder['recordingGroup'] = {
                            'allSupported': False,
                            'includeGlobalResourceTypes': False,
                            'resourceTypes': CONFIG_RECORDER_INCLUSION_RESOURCE_LIST,
                            'recordingStrategy': {
                                'useOnly': 'INCLUSION_BY_RESOURCE_TYPES'
                            }
                        }
                    
                    # Set up recording mode only if we have daily overrides
                    if CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST:
                        config_recorder['recordingMode'] = {
                            'recordingFrequency': CONFIG_RECORDER_DEFAULT_RECORDING_FREQUENCY,
                            'recordingModeOverrides': [
                                {
                                    'description': 'DAILY_OVERRIDE',
                                    'resourceTypes': CONFIG_RECORDER_OVERRIDE_DAILY_RESOURCE_LIST,
                                    'recordingFrequency': 'DAILY'
                                }
                            ]
                        }

                response = configservice.put_configuration_recorder(
                    ConfigurationRecorder=config_recorder)
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
