import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import logging

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('Movies-API')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        if 'requestContext' not in event:
            raise KeyError('requestContext')

        # Handling HTTP API format
        if 'http' in event['requestContext']:
            path = event['rawPath']
            method = event['requestContext']['http']['method']
        # Handling REST API format
        else:
            path = event['path']
            method = event['httpMethod']
        
    except KeyError as e:
        logger.error("KeyError: %s", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps(f'Bad Request: Missing key in event: {str(e)}')
        }
    
    if path == '/get_movies' and method == 'GET':
        return get_movies()
    elif path == '/getmoviesbyyear' and method == 'GET':
        query_params = event.get('queryStringParameters', {})
        year = query_params.get('year')
        if year:
            return get_movies_by_year(year)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps('Bad Request: Missing query parameter "year"')
            }
    else:
        return {
            'statusCode': 404,
            'body': 'Not Found'
        }

def get_movies():
    try:
        response = table.scan()
        movies = response.get('Items', [])
        # Convert Decimal to int for JSON serialization
        for movie in movies:
            movie['year'] = int(movie['year'])
        return {
            'statusCode': 200,
            'body': json.dumps(movies)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error Fetching Movies: {str(e)}'
        }

def get_movies_by_year(year):
    try:
        response = table.scan(FilterExpression=Attr('year').eq(int(year)))
        movies = response.get('Items', [])
        # Convert Decimal to int for JSON serialization
        for movie in movies:
            movie['year'] = int(movie['year'])
        return {
            'statusCode': 200,
            'body': json.dumps(movies)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error getting movies for the year {year}: {str(e)}'
        }
