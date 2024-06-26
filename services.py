import boto3
import color
import json
import zipfile
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError


# Create an S3 bucket
def create_s3():
    s3 = boto3.client('s3')
    bucket_name = 'my-movies-api-bucket'
    bucket_configuration = {"LocationConstraint": "us-west-2"}

    try:
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=bucket_configuration)
        print(f"{color.GREEN}The bucket {bucket_name} was created successfully")

    except NoCredentialsError:
        print(f"{color.RED}Error: AWS Credentials NOT found.")

    except PartialCredentialsError:
        print(f"{color.RED}Error: Incomplete AWS Credentials.")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyExists':
            print(f"{color.RED}Error: The bucket name '{bucket_name}' is already in use.")
        elif error_code == 'BucketAlreadyOwnedByYou':
            print(f"{color.RED}Error: You already own the bucket '{bucket_name}'.")
        else:
            print(f"{color.RED}An error occurred: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


# Create a DynamoDB table
def create_dynamodb():
    dynamodb = boto3.client("dynamodb", region_name="us-west-2")
    table_name = "Movies-API"

    # Check if table exists
    existing_tables = dynamodb.list_tables()['TableNames']
    if table_name in existing_tables:
        print(f"{color.RED}Error: The table name '{table_name}' already exists.")
        return

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'title', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'title', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
        )
        # Wait for the table to be created
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        # Then it prints the status
        print(f"Table status: {table['TableDescription']['TableStatus']}")

    except NoCredentialsError:
        print("Error: AWS Credentials NOT found.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS Credentials.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceInUseException':
            print(f"Error: The table name '{table_name}' already exists.")
        else:
            print(f"An error occurred: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


# Upload data to DynamoDB
def upload_data_to_dynamodb(json_file, tablename):
    dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
    table = dynamodb.Table(tablename)

    try:
        with open(json_file) as file:
            movies = json.load(file)

        with table.batch_writer() as batch:
            for movie in movies:
                if 'title' in movie:
                    batch.put_item(Item=movie)
        print(f'{color.GREEN}Successfully uploaded movie data to {table}')

    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
    except json.JSONDecodeError:
        print("Error: JSON file is not properly formatted.")
    except ClientError as e:
        print(f"{color.RED} An error occurred: {e.response['Error']['Message']}")
    except Exception as e:
        print(f'{color.RED}An unexpected error occurred {str(e)}')


# Create a zip file for the Lambda function
def create_lambda_zip():
    with zipfile.ZipFile('lambda_function.zip', 'w') as z:
        z.write('lambda_function.py')


# Create the Lambda function
def create_lambda(role_arn, region_name):
    lambda_client = boto3.client('lambda', region_name=region_name)
    create_lambda_zip()

    with open('lambda_function.zip', 'rb') as f:
        lambda_function_code = f.read()

    lambda_function_name = 'my_lambda_function'
    try:
        lambda_response = lambda_client.create_function(
            FunctionName=lambda_function_name,
            Runtime='python3.8',
            Handler='lambda_function.lambda_handler',
            Role=role_arn,
            Code={'ZipFile': lambda_function_code},
            Description='A Lambda function for my REST API',
            Timeout=30,
            MemorySize=128
        )
        print(f"{color.GREEN}Lambda function created successfully.")
        return lambda_response['FunctionArn']
    except ClientError as e:
        print(f"{color.RED}An error occurred: {e.response['Error']['Message']}")
        raise


# Create API Gateway for the two endpoints and integrate with Lambda
def create_api_gateway(lambda_arn, region_name):
    apigateway_client = boto3.client('apigateway', region_name=region_name)
    api_response = apigateway_client.create_rest_api(
        name='serverlessAPI',
        description='This is my API for Lambda integration',
        endpointConfiguration={'types': ['REGIONAL']}
    )

    api_id = api_response['id']

    # Create the API Gateway resources
    resources = apigateway_client.get_resources(restApiId=api_id)
    root_id = [resource for resource in resources['items'] if resource['path'] == '/'][0]['id']

    # Create a new resource for get_movies
    get_movies_resource_response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='get_movies'
    )

    get_movies_resource_id = get_movies_resource_response['id']
    
    # Create a new resource for getmoviesbyyear
    get_movies_by_year_resource_response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='getmoviesbyyear'
    )

    get_movies_by_year_resource_id = get_movies_by_year_resource_response['id']

    # Create a GET method for the get_movies resource
    apigateway_client.put_method(
        restApiId=api_id,
        resourceId=get_movies_resource_id,
        httpMethod='GET',
        authorizationType='NONE'
    )

    # Integrate the GET method with the Lambda function
    integration_uri_get_movies = f'arn:aws:apigateway:{region_name}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
    
    apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=get_movies_resource_id,
        httpMethod='GET',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=integration_uri_get_movies
    )

    # Create a GET method for the getmoviesbyyear resource
    apigateway_client.put_method(
        restApiId=api_id,
        resourceId=get_movies_by_year_resource_id,
        httpMethod='GET',
        authorizationType='NONE'
    )

    # Integrate the GET method with the Lambda function
    integration_uri_get_movies_by_year = f'arn:aws:apigateway:{region_name}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'

    apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=get_movies_by_year_resource_id,
        httpMethod='GET',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=integration_uri_get_movies_by_year
    )

    # Grant API Gateway permission to invoke the Lambda function
    lambda_client = boto3.client('lambda', region_name=region_name)
    account_id = boto3.client("sts").get_caller_identity()["Account"]
   
    lambda_client.add_permission(
        FunctionName='my_lambda_function',
        StatementId='api-gateway-invoke-get-movies',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:{region_name}:{account_id}:{api_id}/*/GET/get_movies'
    )

    lambda_client.add_permission(
        FunctionName='my_lambda_function',
        StatementId='api-gateway-invoke-get-movies-by-year',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:{region_name}:{account_id}:{api_id}/*/GET/getmoviesbyyear'
    )

    # Deploy the API
    deployment_response = apigateway_client.create_deployment(
        restApiId=api_id,
        stageName='prod'
    )

    print(f'{color.GREEN}API Gateway created and deployed. Invoke URL: https://{api_id}.execute-api.{region_name}.amazonaws.com/prod')


# Main function to execute all steps with user alerts
def main():
    # create_s3()
    # input("Press Enter to continue...")

    # create_dynamodb()
    # input("Press Enter to continue...")

    # upload_data_to_dynamodb('movies.json', 'Movies-API')
    # input("Press Enter to continue...")

    region_name = "us-west-2"
    role_arn = input(f"{color.YELLOW}Please enter the ARN of the IAM role created in the AWS console: {color.RESET}")
    lambda_arn = create_lambda(role_arn, region_name)
    input("Press Enter to continue...")

    create_api_gateway(lambda_arn, region_name)
    input("Press Enter to finish...")


if __name__ == "__main__":
    main()
