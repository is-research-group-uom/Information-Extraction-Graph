AWS_CREDENTIALS ={
    'aws_access_key_id':'ASIAQUFLQFJYJVAJNMBN',
    'aws_secret_access_key':'x9wW4fhowXipdEMn8TzlpBD3v96pnJe6B7yfXED9',
    'aws_session_token':'IQoJb3JpZ2luX2VjEHcaDGV1LWNlbnRyYWwtMSJHMEUCIB3ghYZFrotXHwCQWkmmL4I7SlVNxPSs16mQv9aAyM79AiEA5IbipAQT/A3he3kjJHerodrQ1fDBaEP6305kkm7x92Aq7gIIoP//////////ARAAGgwwNDMzMDkzNDUzOTIiDJb8YIOPN0U7VW2rdSrCAtpHz/Gw1Fe3+/ofSz9xuA2aFM5DHgpSboakYToEVc2MUu08CLXRjbz3zplculkEvp7qSXry2DTmD2Z3RmYDPIhZPKelbJy8okQ3a4cFh9TmETlm7UqPMYSKNgRg+Wya/4xekm8o3JRq5biNBvvliHKsf16KzrMnvMjQF4kmInrioNy9uJtEXX7qn+DMJEVFr7LZW9fungZoceRlVLF1NkzS7IiCow/tIgyCwVg0yxTZC0GPINs5ITnsrvrJm9YbaJf2nHi0kGeLNxtBJNVvYVwaEeEwV8nPo3I0Hnsd+4JFyzVUOLliZ9nlICz1TR8EQQbPdVcL94tTO2X+N6b6eD8O3gNsrOcd8QbUjCxZ6cla8ele8oA0UgGBG0WhZUH1jOeTA5teQt00beHr3EbqoGL0haWux8XzMQeSSliy+fq/WwgwudahxAY6pwHPSuMd/Fa63IvHOE8MQVn5DVoU+KR4t+mlC4T/S7/z3rU+ml8ALDSGvZEzUpsIpl4Do9pLfFnzUykKvoy2wIIqKRUXV7c3fLktAGrutPfh6onl0LbUUcZUGvdz9o7U9mMSqChm5m1PriTXjEQdyfy+McLLTtCbjecZnkCAL5hiAAgQhIc9T6RJw04aRQ/2vszlU29o8bwrQQIky8uTvQTaQ/Lbb2cCog==',
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