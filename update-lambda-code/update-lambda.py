import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ.get('TABLE_NAME', 'Movies')


def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps(body)
    }


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    try:
        movie_names = []
        scan_kwargs = {
            'ProjectionExpression': 'movies'
        }

        while True:
            response = table.scan(**scan_kwargs)

            movie_names.extend(
                item.get('movies')
                for item in response.get('Items', [])
                if item.get('movies')
            )

            last_evaluated_key = response.get('LastEvaluatedKey')

            if not last_evaluated_key:
                break

            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

        movie_names.sort()

        return build_response(200, movie_names)

    except Exception as error:
        print(f"Error retrieving movies: {error}")

        return build_response(
            500,
            {'error': 'Unable to retrieve movie list'}
        )