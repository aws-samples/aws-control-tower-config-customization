
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
import cfnresponse
import os
import logging
import ast
import json

def lambda_handler(event, context):
    
    LOG_LEVEL = os.getenv('LOG_LEVEL')
    logging.getLogger().setLevel(LOG_LEVEL)

    try:
        logging.info('Event Data: ')
        logging.info(event)
        sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
        excluded_accounts = os.getenv('EXCLUDED_ACCOUNTS')
        logging.info(f'Excluded Accounts: {excluded_accounts}')

        # Check if the lambda was trigerred from EventBridge.
        # If so extract Account and Event info from the event data.
        
        is_eb_trigerred = 'source' in event
        
        logging.info(f'Is EventBridge Trigerred: {str(is_eb_trigerred)}')
        event_source = ''
        
        if is_eb_trigerred:
            event_source = event['source']
            logging.info(f'Control Tower Event Source: {event_source}')
            event_name = event['detail']['eventName']
            logging.info(f'Control Tower Event Name: {event_name}')
        
        if event_source == 'aws.controltower' and event_name == 'UpdateManagedAccount':    
            account = event['detail']['serviceEventDetails']['updateManagedAccountStatus']['account']['accountId']
            logging.info(f'overriding config recorder for SINGLE account: {account}')
            override_config_recorder(excluded_accounts, sns_topic_arn, account, 'controltower')
        elif event_source == 'aws.controltower' and event_name == 'CreateManagedAccount':  
            account = event['detail']['serviceEventDetails']['createManagedAccountStatus']['account']['accountId']
            logging.info(f'overriding config recorder for SINGLE account: {account}')
            override_config_recorder(excluded_accounts, sns_topic_arn, account, 'controltower')
        elif event_source == 'aws.controltower' and event_name == 'UpdateLandingZone':
            logging.info('overriding config recorder for ALL accounts due to UpdateLandingZone event')
            override_config_recorder(excluded_accounts, sns_topic_arn, '', 'controltower')
        elif ('LogicalResourceId' in event) and (event['RequestType'] == 'Create'):
            logging.info('CREATE CREATE')
            logging.info(
                'overriding config recorder for ALL accounts because of first run after function deployment from CloudFormation')
            override_config_recorder(excluded_accounts, sns_topic_arn, '', 'Create')
            response = {}
            ## Send signal back to CloudFormation after the first run
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response, "CustomResourcePhysicalID")
        elif ('LogicalResourceId' in event) and (event['RequestType'] == 'Update'):
            logging.info('Update Update')
            logging.info(
                'overriding config recorder for ALL accounts because of first run after function deployment from CloudFormation')
            override_config_recorder(excluded_accounts, sns_topic_arn, '', 'Update')
            response = {}
            update_excluded_accounts(excluded_accounts, sns_topic_arn)
            
            ## Send signal back to CloudFormation after the first run
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response, "CustomResourcePhysicalID")    
        elif ('LogicalResourceId' in event) and (event['RequestType'] == 'Delete'):
            logging.info('DELETE DELETE')
            logging.info(
                'overriding config recorder for ALL accounts because of first run after function deployment from CloudFormation')
            override_config_recorder(excluded_accounts, sns_topic_arn, '', 'Delete')
            response = {}
            ## Send signal back to CloudFormation after the final run
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response, "CustomResourcePhysicalID")
        else:
            logging.info("No matching event found")

        logging.info('Execution Successful')
        
        # TODO implement
        return {
            'statusCode': 200
        }

    except Exception as e:
        exception_type = e.__class__.__name__
        exception_message = str(e)
        logging.exception(f'{exception_type}: {exception_message}')


def override_config_recorder(excluded_accounts, sns_topic_arn, account, event):
    
    try:
        client = boto3.client('cloudformation')
        # Create a reusable Paginator
        paginator = client.get_paginator('list_stack_instances')
        
        # Create a PageIterator from the Paginator
        if account == '':
            page_iterator = paginator.paginate(StackSetName ='AWSControlTowerBP-BASELINE-CONFIG')
        else:
            page_iterator = paginator.paginate(StackSetName ='AWSControlTowerBP-BASELINE-CONFIG', StackInstanceAccount=account)
            
        sns_client = boto3.client('sns')
        for page in page_iterator:
            logging.info(page)
            
            for item in page['Summaries']:
                account = item['Account']
                region = item['Region']
                send_message_to_sns(event, account, region, excluded_accounts, sns_client, sns_topic_arn)
                    
    except Exception as e:
        exception_type = e.__class__.__name__
        exception_message = str(e)
        logging.exception(f'{exception_type}: {exception_message}')

def send_message_to_sns(event, account, region, excluded_accounts, sns_client, sns_topic_arn):
    
    try:

        #Proceed only if the account is not excluded
        if account not in excluded_accounts:

            #construct sns message
            sns_msg = {
                "Account": account,
                "Region": region,
                "Event": event
            }

            #send message to sns
            response = sns_client.publish(
                TopicArn=sns_topic_arn,
                Message=json.dumps(sns_msg)
            )
            logging.info(f'message sent to sns: {sns_msg}')

        else:
            logging.info(f'Account excluded: {account}')  
                
    except Exception as e:
        exception_type = e.__class__.__name__
        exception_message = str(e)
        logging.exception(f'{exception_type}: {exception_message}')
                   
def update_excluded_accounts(excluded_accounts, sns_topic_arn):
    
    try:
        acctid = boto3.client('sts')
        
        new_excluded_accounts = "['" + acctid.get_caller_identity().get('Account') + "']"
        
        logging.info(f'templist: {new_excluded_accounts}')
        
        templist=ast.literal_eval(excluded_accounts)
        
        templist_out=[]
        
        for acct in templist:
            
            if acctid.get_caller_identity().get('Account') != acct:
                templist_out.append(acct)
                logging.info(f'Delete request sent: {acct}')
                override_config_recorder(new_excluded_accounts, sns_topic_arn, acct, 'Delete')
        
    except Exception as e:
        exception_type = e.__class__.__name__
        exception_message = str(e)
        logging.exception(f'{exception_type}: {exception_message}')  