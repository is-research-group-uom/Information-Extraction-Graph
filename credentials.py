AWS_CREDENTIALS ={
    'aws_access_key_id':'ASIAQUFLQFJYHQM63KZM',
    'aws_secret_access_key':'O3k87aAda1Y0TtUlY8M32qn2JKi8+ZnWUU/3Ui1y',
    'aws_session_token':'IQoJb3JpZ2luX2VjEH4aDGV1LWNlbnRyYWwtMSJGMEQCIGRlJYzvShGHVstsERHH1IWFC3182qsvVN6aXs/KvPjYAiA+VSTxwE4wtHlsXVNGPkdWiiXpe32FWrKC1WlY7h/QoCruAgin//////////8BEAAaDDA0MzMwOTM0NTM5MiIMuJL76RRMu2OBZ2MvKsICMSiwnZ7HrPuypg0eQ2+c4NzjJoLsnLoix/BCKNRaEkvdjZ6la9H+IiOa6v0JE2t1y+50dDYAXTGsIxUu6F3yNlP7JuPb53D4AE98bu/TruNYCI2IGig5Sg9O/W0EQjcXmzCAZKId9TKKdLlmmjdaU/JHNWHVJzYRvhJpeLlCz6ZXE6JWl9zkecNRH+kQUyUI+6JTUzoDH1W4iNfKEIzklg3DbQ/WO+ROUx1s17A+b6qM7iJNhGeXt3IB+LPoy/i88cBQhLkL7oD4rhH5xos3XYgFFAm4NYWAZ7XGTTx13VSjOeBLr98DQDFmRyXyrdGi49nvNF3zpglN9VUFaHAIWRK7vtCRltvsze9kM4P8WmVRH+eD0jREt8RzwcS/R4I8z105DTIAjasFsRNaGRtLjLPn9PcBfen4yPfd06wZGrMn7TCyrqPEBjqoAQOE5ndB/bfY+VlVAWiqVy3/YMUZ0wHbcE9FW8+0u8wamUpf/BrYKAk/iGypwkLSqZ7my7tLsdtunK8N6xOn5FKy4ODlK4gMfkrOXAGBsW++3+iX1SlOm5ABlBdfnVORVLHrugVb4PPlDXOV57Afl/5D+B18kjFQuVh6oNBs7Wf1zm8sATBt5H8aJ7vRem6wq3JsMeDJZNrtdPF7uByBK3nlshXulilyZg==',
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
        # Default configuration with reasonable timeouts
        config = Config(
            read_timeout=180,  # 3 minutes
            connect_timeout=60,  # 1 minute
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