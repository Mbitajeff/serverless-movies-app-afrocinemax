import boto3
import csv
import os
import urllib.parse

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

TABLE_NAME = os.environ['TABLE_NAME'].strip()
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN'].strip()

table = dynamodb.Table(TABLE_NAME)


def delete_existing_items():
    """Delete all existing items from the DynamoDB table."""
    scan_kwargs = {}

    while True:
        response = table.scan(**scan_kwargs)

        with table.batch_writer() as batch:
            for item in response.get('Items', []):
                batch.delete_item(
                    Key={
                        'movies': item['movies']
                    }
                )

        last_evaluated_key = response.get('LastEvaluatedKey')

        if not last_evaluated_key:
            break

        scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

    print('All existing items deleted.')


def send_notification(subject, message):
    """Send an SNS notification."""
    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject=subject
    )


def lambda_handler(event, context):
    try:
        delete_existing_items()

        total_records = 0

        for record in event.get('Records', []):
            bucket = record['s3']['bucket']['name']

            key = urllib.parse.unquote_plus(
                record['s3']['object']['key']
            )

            response = s3_client.get_object(
                Bucket=bucket,
                Key=key
            )

            content = (
                response['Body']
                .read()
                .decode('utf-8-sig')
                .splitlines()
            )

            csv_reader = csv.DictReader(content)

            with table.batch_writer() as batch:
                for row in csv_reader:
                    if not row:
                        continue

                    movie_name = row.get('movies')

                    if not movie_name:
                        continue

                    item = {
                        key: value
                        for key, value in row.items()
                        if key and value is not None
                    }

                    batch.put_item(Item=item)
                    total_records += 1

        message = (
            f'Successfully processed and uploaded '
            f'{total_records} records to DynamoDB.'
        )

        send_notification(
            'AfroCinemax Movie Update Completed',
            message
        )

        print(message)

        return {
            'statusCode': 200,
            'body': message
        }

    except Exception as error:
        error_message = (
            f'Error occurred while processing records: {str(error)}'
        )

        print(error_message)

        try:
            send_notification(
                'AfroCinemax Movie Update Failed',
                error_message
            )
        except Exception as notification_error:
            print(
                f'Unable to send SNS notification: '
                f'{str(notification_error)}'
            )

        return {
            'statusCode': 500,
            'body': error_message
        }