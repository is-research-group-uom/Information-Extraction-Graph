AWS_CREDENTIALS ={
    'aws_access_key_id':'',
    'aws_secret_access_key':'',
    'aws_session_token':'',
    'region_name':'us-east-1'
}

def get_bedrock_client(config=None):
    """
    Returns a configured boto3 bedrock-runtime client using the stored credentials.

    Returns:
        boto3.client: Configured bedrock-runtime client
    """
    import boto3
    from botocore.config import Config

    if config is None:
        config = Config(
            read_timeout=180,
            connect_timeout=60,
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            }
        )

    return boto3.client('bedrock-runtime', config=config, **AWS_CREDENTIALS)

    return boto3.client('bedrock-runtime', **AWS_CREDENTIALS)

def get_credentials():
    """
    Returns the AWS credentials dictionary.

    Returns:
        dict: AWS credentials
    """
    return AWS_CREDENTIALS.copy()