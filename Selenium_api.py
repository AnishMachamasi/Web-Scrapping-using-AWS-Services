import boto3
import csv
import json

s3 = boto3.resource('s3')

def lambda_handler(event, context):
    bucket_name = 'bucket-selenium-crawler'
    bucket = s3.Bucket(bucket_name)
    json_data = []

    # Iterate over all objects in the bucket
    for obj in bucket.objects.all():
        if obj.key.endswith('.csv'):
            # Retrieve the CSV file from the S3 bucket
            rows = obj.get()['Body'].read().decode('utf-8').splitlines()

            # Convert the CSV data to JSON format
            csv_data = csv.DictReader(rows)
            for row in csv_data:
                json_data.append(row)

    # Return the JSON data as the Lambda response
    return {
        'statusCode': 200,
        'body': json.dumps(json_data),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
}