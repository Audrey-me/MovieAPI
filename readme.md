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
       
        