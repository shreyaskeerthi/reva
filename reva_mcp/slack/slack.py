from fastmcp import Client
import os
from dotenv import load_dotenv

load_dotenv()

MERGE_TOOL_PACK_URL = "https://ah-api.merge.dev/api/v1/tool-packs/a5bd55f5-e493-4193-8355-74b7a1dba2b0/registered-users/69ff5ba3-39e4-4485-be45-fb300da361b7/mcp"
MERGE_API_KEY = os.getenv("MERGE_API_KEY")
MERGE_ACCOUNT_TOKEN = os.getenv("MERGE_ACCOUNT_TOKEN")

client = Client(MERGE_TOOL_PACK_URL)

async def send_to_slack(channel: str, text: str):
    async with client:
        result = await client.call_tool(
            "slack_send_message",
            arguments={
                "channel": channel,
                "text": text
            },
            # headers={
            #     "Authorization": f"Bearer {MERGE_API_KEY}",
            #     "X-Account-Token": MERGE_ACCOUNT_TOKEN,
            # }
        )
    return result

