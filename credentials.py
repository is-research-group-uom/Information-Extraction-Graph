AWS_CREDENTIALS ={
    'aws_access_key_id':'',
    'aws_secret_access_key':'',
    'aws_session_token':'',
    'region_name':'us-east-1'
}

def get_bedrock_client():
    """
    Returns a configured boto3 bedrock-runtime client using the stored credentials.

    Returns:
        boto3.client: Configured bedrock-runtime client
    """
    import boto3

    return boto3.client('bedrock-runtime', **AWS_CREDENTIALS)

def get_credentials():
    """
    Returns the AWS credentials dictionary.

    Returns:
        dict: AWS credentials
    """
    return AWS_CREDENTIALS.copy()