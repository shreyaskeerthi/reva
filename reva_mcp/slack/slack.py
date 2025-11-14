import os
import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

from dotenv import load_dotenv
load_dotenv()

MERGE_API_KEY = os.getenv("MERGE_API_KEY")            # Your Merge Production/Test Access Key
MERGE_ACCOUNT_TOKEN = os.getenv("MERGE_ACCOUNT_TOKEN") # Your Registered User Account Token

TOOL_PACK_ID = "a5bd55f5-e493-4193-8355-74b7a1dba2b0"
REGISTERED_USER_ID = "69ff5ba3-39e4-4485-be45-fb300da361b7"

MCP_URL = (
    f"https://ah-api.merge.dev/api/v1/tool-packs/{TOOL_PACK_ID}"
    f"/registered-users/{REGISTERED_USER_ID}/mcp"
)

async def send_to_slack(channel: str, text: str):
    headers = {
        "Authorization": f"Bearer {MERGE_API_KEY}",
        "X-Account-Token": MERGE_ACCOUNT_TOKEN,
        "Mcp-Session-Id": "session-001",
        "X-Chat-Id": "chat-001",
    }

    async with streamablehttp_client(MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            return await session.call_tool(
                "slack_post_message",
                {
                    "channel": channel,
                    "text": text
                }
            )

async def main():
    result = await send_to_slack("general", "Hello from MCP!")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
