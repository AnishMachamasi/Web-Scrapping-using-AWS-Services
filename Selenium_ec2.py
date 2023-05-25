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
    s3_client.download_file('macha-key','Macha.pem', '/tmp/machakey.pem')

    # reading pem file and creating key object
    key = paramiko.RSAKey.from_private_key_file("/tmp/machakey.pem")
    # an instance of the Paramiko.SSHClient
    ssh_client = paramiko.SSHClient()
    # setting policy to connect to unknown host
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # connect using ec2 instance ID if requires
    ssh_client.connect(hostname="15.206.122.33", username="ubuntu", pkey=key)

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