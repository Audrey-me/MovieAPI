# these is where i will create all the AWS services i will be using programmatically using Boto3
import boto3
import color
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

# create an s3 bucket
def create_s3():
    s3 = boto3.client('s3')
    bucket_name = 'my-movies-api-bucket'
    bucket_configuration = { "LocationConstraint" :"us-west-2"}

    try:
        response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=bucket_configuration)
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

def create_dynamodb():
        dynamodb = boto3.client("dynamodb", region_name = "us-west-2")
        table_name = "Movies-API"

        # Check if table exists
        existing_tables = dynamodb.list_tables()['TableNames']
        if table_name in existing_tables:
            print(f"{color.RED} Error: The table name '{table_name}' already exists.")
            return
        
        try:
            table = dynamodb.create_table(
            TableName= table_name,
            KeySchema=[
                {'AttributeName': 'title','KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'title','AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 10,'WriteCapacityUnits': 10}
        )
            # wait for the table to be created
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            # then it print the status
            print(f"Table status: {table.table_status}")

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


def upload_data_to_dynamodb(json_file, tablename):
    dynamodb = boto3.resource("dynamodb", region_name = "us-west-2")
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
        print(f'{color.RED} An error occurred: {e.response['Error']['Message']}')       
    except Exception as e:
        print(f'{color.RED}An unexpected error occurred {str(e)}')

def main():
    create_s3()
    create_dynamodb()
    json_file = input(f'{color.YELLOW} Enter json file path: {color.RESET}')
    upload_data_to_dynamodb(json_file, 'Movies-API')

if __name__ == "__main__":
    main()
