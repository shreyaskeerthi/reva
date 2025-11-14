from __future__ import print_function

import merge
from merge.client import Merge
import os
from dotenv import load_dotenv

load_dotenv()


# Swap YOUR_API_KEY below with your production key from:

# https://app.merge.dev/keys

# Swap YOUR_ACCOUNT_TOKEN with your account key from

# the linked account page.

merge_client = Merge(api_key=f"{os.getenv('MERGE_API_KEY')}", account_token=f"{os.getenv('MERGE_ACCOUNT_TOKEN')}")
print(merge_client)