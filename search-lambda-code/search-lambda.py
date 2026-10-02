import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ.get('TABLE_NAME', 'Movies')


def decimal_to_int_or_float(obj):
    """Convert DynamoDB Decimal values into JSON-compatible numbers."""
    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, dict):
        return {
            key: decimal_to_int_or_float(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [decimal_to_int_or_float(item) for item in obj]

    return obj


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
    print("Received event: " + json.dumps(event))

    table = dynamodb.Table(TABLE_NAME)

    query_parameters = event.get('queryStringParameters') or {}
    movie_name = query_parameters.get('movieName', '').strip()

    if not movie_name:
        return build_response(
            400,
            {'error': 'movieName parameter is required'}
        )

    try:
        response = table.query(
            KeyConditionExpression=Key('movies').eq(movie_name)
        )

        items = decimal_to_int_or_float(
            response.get('Items', [])
        )

        return build_response(200, items)

    except Exception as error:
        print(f"Search error: {error}")

        return build_response(
            500,
            {'error': 'Unable to search for movies'}
        )