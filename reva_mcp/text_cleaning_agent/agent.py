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
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.2,
        "top_p": 0.9,
    }

    response = bedrock.invoke_model(
        modelId="meta.llama3-70b-instruct-v1:0",
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json",
    )

    response_json = json.loads(response["body"].read())
    result = response_json.get("generation", "")
    return result
