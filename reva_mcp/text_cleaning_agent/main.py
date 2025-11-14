import asyncio
from reva_mcp.merge_handler.merge_client_test import merge_client
from reva_mcp.slack.slack import send_to_slack
from reva_mcp.text_cleaning_agent.agent import clean_text_with_aws

async def process_and_send(raw_text: str, slack_channel: str):
    # 1. clean with AWS
    cleaned = clean_text_with_aws(raw_text)

    # 2. send with Merge Slack tool
    # async with merge_client:
    result = await send_to_slack(slack_channel, cleaned)

    print("Message sent:", result)


raw = """
The property is a 75,000-square-foot office building in Miami, Florida, purchased for 32 million.The NOI is 2.3 million, the cap rate is 4.7%, and the occupancy is 68%. The property was built in 2019 and has floor-to-ceiling glass, high-end finishes, and structured parking. The seller is a private equity firm, and the broker is Cushman & Wakefield. The property is in a good location and has potential for growth, but there are some risks associated with the market and the economy. The recommendation is to proceed with the purchase.
"""

asyncio.run(process_and_send(
    raw_text=raw,
    slack_channel="general"
))
