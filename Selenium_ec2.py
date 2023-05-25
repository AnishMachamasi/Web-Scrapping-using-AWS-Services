import json
import boto3
import paramiko
import time

def lambda_handler(event, context):
    # boto3 client
    client = boto3.client('ec2')
    s3_client = boto3.client('s3')
    
    # getting instance information
    describeInstance = client.describe_instances()
    
    # downloading pem file from S3 
    s3_client.download_file('bucket_name_containing_key_pair','key_pair_name.pem', 'new_location: /tmp/new_name.pem')

    # reading pem file and creating key object
    key = paramiko.RSAKey.from_private_key_file("/tmp/new_name.pem")
    # an instance of the Paramiko.SSHClient
    ssh_client = paramiko.SSHClient()
    # setting policy to connect to unknown host
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # connect using ec2 instance ID if requires
    ssh_client.connect(hostname="Public_DNS_Address of EC2", username="ubuntu", pkey=key)

    # command list
    commands = [
        "python3 ./selenium-code/SeleniumWebCrawler.py",
    ]

    # executing list of commands within server
    print("Starting execution")
    for command in commands:
        print("Executing command: " + command)
        stdin , stdout, stderr = ssh_client.exec_command(command)
        print(stdout.read())
        print(stderr.read())
    
    print("finished execution")
    
    return {
        'statusCode': 200
    }
