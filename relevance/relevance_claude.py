import json
from botocore.exceptions import ClientError
from credentials import get_bedrock_client


def relevance_claude(article, comment):
    # Create an Amazon Bedrock Runtime client.
    brt = get_bedrock_client()

    # Set the model ID
    model_id = "arn:aws:bedrock:us-east-1:043309345392:inference-profile/us.anthropic.claude-3-5-sonnet-20240620-v1:0"

    # Define the prompt for the model
    prompt = f"""
    Look at the relevance of the <comment>, given relative to the {article} that they are assigned to based on the parameters listed below, and provide a score out of 100 for not only 
    how they progress deliberation on the matter but also relate to the topic and overall discussion of the article itself.

    <comment>
    {comment}

    You will be given:
    1. Only the total score an int. Total score is the {{sum}} of the scores that will get for each category bellow.

    You must produce, in order:

    **Α. Comment Evaluation & Scoring**  
    For each comment, assign a **Relevance Score** out of 100 according to these parameters:
    1. **Topical Focus (0–30)**  
       - +points for precision and depth on the article’s topic.  
       - +bonus if it introduces a related subtopic.  
       - –penalty if off-topic or irrelevant; mark “Remove” if completely unrelated.
    2. **Evidence Introduction (0–25)**  
       - +points if it brings new, relevant evidence.  
       - +bonus for expanding discussion into novel areas.
    3. **Evidence Validity (0–20)**  
       - +points if factually correct.  
       - –points if demonstrably false (cite a counter-source).
    4. **Engagement Impact (0–15)**  
       - +points if others reply or engage with the comment.  
       - If no engagement, score 0 here but do not penalize overall.
    5. **Originality (0–10)**  
       - +points if the idea is unique in the thread.  
       - –points if it repeats earlier arguments.

    return only the total score without any comments or explanations. If the comment is completely irelevant score it with 0. 

    1st Example of output:
    0 
    2nd Example of output:
    29
    """

    # Format the request payload (back to simple text)
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 131072,
        "top_k": 250,
        "stop_sequences": [],
        "temperature": 0,
        "top_p": 0.999,
        "system": "You are an assistant that is meant to act is a deliberation tool and moderate online forums and debates. You are associated with the AI4Deliberation group in the "
                  "University of Macedonia with the sole purpose of analyzing the articles and comments that are given to you, providing ratings and summaries of debates and deliberations, "
                  "and synthesizing reports",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }

    # Convert the native request to JSON
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request
        response = brt.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    # Decode the response body
    model_response = json.loads(response["body"].read())

    # Extract and print the response text
    response_text = model_response['content'][0]['text']

    return response_text