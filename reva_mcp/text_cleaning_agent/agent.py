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


raw = """
The property is a 75,000-square-foot office building in Miami, Florida, purchased for 32 million.The NOI is 2.3 million, the cap rate is 4.7%, and the occupancy is 68%. The property was built in 2019 and has floor-to-ceiling glass, high-end finishes, and structured parking. The seller is a private equity firm, and the broker is Cushman & Wakefield. The property is in a good location and has potential for growth, but there are some risks associated with the market and the economy. The recommendation is to proceed with the purchase.
"""

if __name__ == "__main__":
    print(clean_text_with_aws(raw))
