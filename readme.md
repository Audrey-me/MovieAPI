## Components Explanation
1. API Gateway:
- Acts as an entry point for your API.
- Routes incoming HTTP requests to the appropriate Lambda function.

2. AWS Lambda:
- Contains your lambda_function.py which includes handlers for different API endpoints.
- Executes your code in response to the API Gateway requests.

3. DynamoDB Table ("Movies-API"):
- Stores your movie data.
- Accessed by the Lambda function to get or put data.

4. S3 Bucket ("my-movies-api-bucket"):
- Used for storing any static files or data related to your project.
- Can be accessed by the Lambda function if necessary.

## File Descriptions
1. color.py:
   Contains definitions for color-coded messages.

2. movies.json:
- JSON file containing movie data.
- Used to upload initial data to DynamoDB.

3. services.py:
- Contains functions to create and manage AWS resources (S3, DynamoDB).
- Includes functions to upload data to DynamoDB.

4. lambda_function.py:
- The main Lambda function handler.
- Processes requests routed by API Gateway.
- Interacts with DynamoDB to fetch and manipulate movie data.

## Steps to Follow
Check this article []

