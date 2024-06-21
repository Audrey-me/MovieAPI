
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
1. Install AWS SDK (Boto3) to write your code locally
```bash
python3 -m pip install boto3
```

2. Run the services.py file to create the differemt AWS resources 
    ```bash
    python3 services.py
    ```

3. cd into the 'my_lambda' folder and run this command to install the dependencies
    ```bash
       pip install -r requirements.txt
    ```

4. Once you have all your files and dependencies in the same directory, you can create a ZIP file.
    ```bash
    zip -r ../lambda_function.zip .
    ```

5. Upload to AWS Lambda

6. since the lambda function will be accessing the dynamodb, you need to make sure it has the neccessary permissions    
       
        