# Quick Start Guide

Get the CRE Deal Voice Agent running in under 2 minutes.

## Option 1: Fastest Start (Demo Mode - No Setup Required)

```bash
# Install dependencies
pip install streamlit pydantic pydantic-settings python-dotenv boto3 deepgram-sdk requests python-dateutil

# Run the app
streamlit run app.py
```

The app will run in **full demo mode** with zero configuration.

## Option 2: Using Virtual Environment (Recommended)

```bash
# Run the setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Run the app
streamlit run app.py
```

## Option 3: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template (optional)
cp .env.example .env

# Run the app
streamlit run app.py
```

## First Demo

Once the app is running at http://localhost:8501:

1. **Input Tab** → Select "Load Example" → Choose "Austin Multifamily"
2. **Analyze Tab** → Click "Run CRE Deal Agent"
3. See structured data, score, and verdict
4. **CRM Tab** → Click "Create CRM Records via Merge"
5. **Evidence Tab** → Click "Generate & Send Evidence Packet"
6. **Jobs Tab** → Click "Run Daily Summary Job"
7. **Security & Infra Tab** → Click "Check Cluster Health"

## Adding Real API Keys (Optional)

Edit `.env` file:

```bash
# For real transcriptions
DEEPGRAM_API_KEY=your_key_here

# For real AWS Bedrock + S3
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
USE_BEDROCK=1

# For real CRM integration
MERGE_API_KEY=your_merge_key
MERGE_ACCOUNT_TOKEN=your_account_token

# Turn off demo mode
DEMO_MODE=0
```

Restart the app after editing `.env`.

## Troubleshooting

**"No module named 'streamlit'"**
- Install dependencies: `pip install -r requirements.txt`

**"No module named 'cre_agent'"**
- Run from project root: `cd /path/to/switchboard && streamlit run app.py`

**Port already in use**
- Stop other Streamlit apps or use: `streamlit run app.py --server.port 8502`

## Next Steps

- Read the full [README.md](README.md) for all features
- Configure real API integrations in `.env`
- Review sponsor integration details
- Customize buy-box settings in the app sidebar
