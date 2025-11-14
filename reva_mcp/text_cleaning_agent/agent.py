import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def clean_text_with_aws(raw_text: str) -> str:
    prompt = f"""
    You are a text-cleaner agent.
    Clean, rewrite, and structure the following message for Slack.
    Preserve meaning but improve clarity.

    RAW MESSAGE:
    {raw_text}
    """

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ],
            }
        ],
    }

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps(payload).encode("utf-8"),
        contentType="application/json",
        accept="application/json",
    )

    response_json = json.loads(response["body"].read())
    result = response_json.get("content", [{}])[0].get("text", "")
    return result  # cleaned msg
