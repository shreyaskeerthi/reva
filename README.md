# CRE Deal Voice Agent (Sponsor-Integrated)

A **real-time commercial real estate deal assistant** that lets you speak or paste deal notes, and automatically structures, scores, and manages CRE deals with full sponsor integrations.

## What It Does

This agent transforms messy broker calls, emails, and offering memorandums into structured, actionable deal intelligence:

- **Voice → Text**: Transcribe broker calls using Deepgram
- **Text → Structure**: Extract deal metrics with AWS Bedrock (Titan) or intelligent heuristics
- **Score**: Evaluate deals against your buy-box criteria
- **CRM**: Auto-create contacts, notes, and tasks in your CRM via Merge
- **IC Summaries**: Generate investment committee memos ready for email
- **Compliance**: Create evidence packets for Vanta/Thoropass
- **Orchestration**: Daily summary jobs (Dagster-style)
- **Security**: Browser trust signals (Island-style)
- **Infrastructure**: Cluster health monitoring (Spectro Cloud-style)

Built for CRE/REPE professionals doing acquisitions, sourcing, and deal evaluation.

---

## Sponsor Integrations

This project integrates with 9 sponsors, using **real APIs where configured** and **demo mode** with realistic mock responses as fallback:

| Sponsor | Integration | Purpose |
|---------|-------------|---------|
| **AWS** | Bedrock (Titan Text) + S3 | Deal extraction, IC summaries, artifact storage |
| **Deepgram** | Speech-to-Text API | Voice transcription from broker calls |
| **Merge** | CRM API | Create contacts, notes, tasks in your CRM |
| **Dagster Labs** | Orchestration (simulated) | Daily summary job for deal pipeline |
| **Island** | Browser trust shim | Security telemetry and SSO verification |
| **Vanta** | Evidence API (simulated) | Compliance evidence logging |
| **Thoropass** | Evidence API (simulated) | Compliance evidence logging |
| **Spectro Cloud** | Cluster health (simulated) | Infrastructure monitoring |
| **Coder** | Dev environment (`coder.yaml`) | Reproducible development setup |

### Real vs Demo Mode

- **Real mode**: If you provide API keys and configuration, all integrations use actual APIs
- **Demo mode**: Set `DEMO_MODE=1` or omit credentials to use intelligent mock responses
- **Mixed mode**: Configure only the integrations you want (e.g., real AWS + Deepgram, demo Merge)

The app works **fully** in demo mode with zero configuration.

---

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys:
# - DEEPGRAM_API_KEY (from https://console.deepgram.com/)
# - AWS credentials (via ~/.aws/credentials or AWS_PROFILE)
# - S3_BUCKET (for artifact storage)
# - MERGE_API_KEY + MERGE_ACCOUNT_TOKEN (from https://app.merge.dev/)
```

**Note**: The app works in full demo mode without any configuration!

### 3. Run the Application

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 3-Minute Demo Script

Perfect for presenting to investors, partners, or your team:

### Step 1: Load Example Deal (30 seconds)
1. Go to **Input** tab
2. Select "Load Example"
3. Choose "Austin Multifamily (148 units, 6.5% cap)"
4. Click "Load Example"

### Step 2: Analyze Deal (45 seconds)
1. Go to **Analyze** tab
2. Click "Run CRE Deal Agent"
3. Watch as the agent:
   - Extracts property type, location, price, NOI, cap rate
   - Scores against buy-box (5-8% cap, $5M-$50M, preferred markets)
   - Shows verdict: Pass/Watch/Hard Pass
4. Review the structured data and metrics

### Step 3: Generate IC Summary (20 seconds)
1. Scroll to "Investment Committee Summary"
2. See the auto-generated 2-3 paragraph memo
3. Click "Copy IC Summary" to use in email

### Step 4: Create CRM Records (30 seconds)
1. Go to **CRM** tab
2. See pre-filled broker info (Marcus Thompson, JLL, email)
3. Click "Create CRM Records via Merge"
4. View created contact, note, and task IDs

### Step 5: Generate Evidence (20 seconds)
1. Go to **Evidence** tab
2. Click "Generate & Send Evidence Packet"
3. See compliance packets sent to Vanta and Thoropass
4. Review evidence structure

### Step 6: Run Daily Summary (20 seconds)
1. Go to **Jobs** tab
2. Click "Run Daily Summary Job"
3. See aggregated stats: total deals, avg score, verdicts
4. Review top 3 deals by score

### Step 7: Check Security & Infra (15 seconds)
1. Go to **Security & Infra** tab
2. See Island browser trust signal (SSO, DLP status)
3. Click "Check Cluster Health"
4. View Spectro Cloud-style health metrics

**Total time: ~3 minutes** to demonstrate the full sponsor-integrated workflow!

---

## Sponsor Integration Details

### AWS (Bedrock + S3)

**What it does:**
- Bedrock Titan Text extracts structured deal data from free-form text
- Generates professional IC summaries
- S3 stores run artifacts for audit trails

**Configuration:**
```bash
AWS_REGION=us-east-1
AWS_PROFILE=default  # or use IAM role
S3_BUCKET=my-cre-deals
USE_BEDROCK=1
```

**Fallback:** If not configured, uses regex/heuristic extraction and template summaries

### Deepgram

**What it does:**
- Transcribes audio files (WAV, MP3, M4A, FLAC) to text
- Uses Nova-2 model with smart formatting

**Configuration:**
```bash
DEEPGRAM_API_KEY=your_key_here
```

**Fallback:** Returns realistic demo transcript of an Austin multifamily deal

### Merge (CRM)

**What it does:**
- Creates/updates contacts from broker info
- Logs deal notes with score and verdict
- Creates follow-up tasks

**Configuration:**
```bash
MERGE_API_KEY=your_api_key
MERGE_ACCOUNT_TOKEN=your_account_token
```

**Fallback:** Returns demo IDs but logs intended payloads

### Dagster Labs

**What it does:**
- Simulates daily orchestration job
- Analyzes all deals in `./runs/`
- Computes avg score, verdict distribution, top deals

**Implementation:**
- Function: `cre_agent.storage.run_daily_summary_job()`
- In production, this would be a scheduled Dagster asset

**Trigger:** Click "Run Daily Summary Job" in Jobs tab

### Island

**What it does:**
- Provides browser trust telemetry (SSO, DLP, threat level)
- Simulates zero-trust security signals

**Implementation:**
- JavaScript shim: `static/island-shim.js`
- Sends POST to `/island/signal` endpoint (conceptual)
- Displays latest trust signal in UI

**Note:** Real Island integration would use their browser extension

### Vanta & Thoropass

**What they do:**
- Receive compliance evidence packets
- Include deal hash, score, verdict, CRM IDs, S3 URI

**Implementation:**
- Functions: `send_to_vanta()`, `send_to_thoropass()`
- Logs to `./runs/evidence_log.jsonl`
- Returns ACK with evidence ID

**Trigger:** Click "Generate & Send Evidence Packet" in Evidence tab

### Spectro Cloud

**What it does:**
- Monitors cluster health (status, nodes, pods, resources)
- Simulates Kubernetes infrastructure check

**Implementation:**
- Function: `get_cluster_health()`
- Returns healthy status with CPU/memory/disk metrics

**Trigger:** Click "Check Cluster Health" in Security & Infra tab

### Coder

**What it does:**
- Defines reproducible dev environment
- Specifies Python 3.11, dependencies, startup commands

**Usage:**
```bash
# With Coder CLI
coder create --template coder.yaml

# Or manually reference coder.yaml for environment setup
```

**File:** [coder.yaml](coder.yaml)

---

## Project Structure

```
.
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── coder.yaml                      # Coder dev environment definition
├── README.md                       # This file
├── cre_agent/
│   ├── __init__.py
│   ├── config.py                   # Settings and env var handling
│   ├── deepgram_client.py          # Deepgram STT integration
│   ├── bedrock_client.py           # AWS Bedrock (Titan) integration
│   ├── merge_client.py             # Merge CRM integration
│   ├── deal_parser.py              # Regex-based deal extraction
│   ├── scoring.py                  # Buy-box scoring logic
│   ├── storage.py                  # Local JSON + S3 + evidence + jobs
│   ├── agent_orchestrator.py       # Main agent pipeline
│   └── examples.py                 # Sample CRE deal texts
├── static/
│   └── island-shim.js              # Island browser trust telemetry
└── runs/                           # Auto-created: deal logs and evidence
    ├── {run_id}.json               # Individual run payloads
    └── evidence_log.jsonl          # Compliance evidence log
```

---

## Buy-Box Configuration

Customize your investment criteria via the sidebar:

- **Min/Max Cap Rate**: Target return range (e.g., 5-8%)
- **Max LTV**: Maximum leverage (e.g., 75%)
- **Deal Size Range**: Min/max purchase price (e.g., $5M-$50M)
- **Preferred Markets**: Cities you target (e.g., Austin, Phoenix, Denver)
- **Preferred Property Types**: Asset classes (e.g., multifamily, industrial)

Deals are scored out of 100 based on how well they fit your criteria.

---

## Deal Scoring

Starting from 100 points, the agent applies penalties for:

- Cap rate below minimum (-30 pts max)
- Cap rate above maximum (-20 pts max)
- Deal size outside range (-20 to -25 pts)
- Market not preferred (-15 pts)
- Property type not preferred (-10 pts)
- LTV above maximum (-20 pts max)
- Missing critical data (-10 to -15 pts per field)

**Verdict:**
- **Pass**: 75-100 points
- **Watch**: 50-74 points
- **Hard Pass**: 0-49 points

---

## Example Deal Texts

The app includes 5 realistic CRE deal examples:

1. **Austin Multifamily** - 148 units, 6.5% cap, Class B+, good fit
2. **Phoenix Industrial** - 125k SF, Amazon tenant, triple-net, solid
3. **Miami Office** - High vacancy, low cap (3.4%), likely pass
4. **Dallas Retail** - Kroger-anchored, 7.1% cap, stable
5. **Denver Mixed-Use** - Retail + apartments, 6.5% cap, unique

Load these via **Input → Load Example** to test the agent.

---

## Development

### Running Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Start the app
streamlit run app.py
```

### Using Coder

```bash
# Create a Coder workspace
coder create cre-agent --template coder.yaml

# SSH into workspace
coder ssh cre-agent

# Start the app
streamlit run app.py
```

### Project Structure Notes

- **cre_agent/**: All business logic (clients, parsers, scoring)
- **app.py**: Streamlit UI only (no business logic)
- **static/**: Front-end assets (Island shim)
- **runs/**: Auto-created directory for run logs

### Adding New Sponsors

1. Create new client in `cre_agent/{sponsor}_client.py`
2. Add config vars to `cre_agent/config.py`
3. Integrate into `agent_orchestrator.py` or `storage.py`
4. Add UI controls in `app.py`
5. Update this README

---

## Key Features

### Voice Input
- Upload WAV/MP3/M4A/FLAC files
- Real Deepgram transcription or demo fallback
- Editable transcripts

### Smart Extraction
- AWS Bedrock (Titan) for LLM-based extraction
- Fallback regex parser for 12+ deal fields
- Handles price, NOI, cap rate, units, SF, occupancy, broker info

### Buy-Box Scoring
- Configurable investment criteria
- 100-point scoring system with detailed reasons
- Pass/Watch/Hard Pass verdicts

### CRM Integration
- Auto-create contacts from broker details
- Log deal notes with full context
- Create follow-up tasks with due dates

### IC Summaries
- Professional 2-3 paragraph memos
- Focus on fundamentals, metrics, risks
- Copy-paste ready for emails

### Compliance
- Evidence packets with deal hash
- Sent to Vanta and Thoropass
- Audit trail in JSONL format

### Orchestration
- Daily summary jobs (Dagster-style)
- Aggregate stats across all deals
- Top deals by score

### Security & Infra
- Island browser trust signals
- Spectro Cloud cluster health
- Real-time telemetry

---

## Troubleshooting

### "No module named 'cre_agent'"

Make sure you're running from the project root:
```bash
cd /path/to/switchboard
streamlit run app.py
```

### AWS Credentials Issues

If using Bedrock or S3:
```bash
# Configure AWS CLI
aws configure

# Or set profile in .env
AWS_PROFILE=your-profile-name
```

### Deepgram Transcription Fails

- Check API key is correct
- Verify audio file format (WAV, MP3, M4A, FLAC)
- Falls back to demo mode automatically

### Merge CRM Errors

- Verify both API key and Account Token are set
- Check Merge dashboard for account status
- Falls back to demo IDs automatically

---

## Production Deployment

### Environment Variables

**Required for production:**
- `DEMO_MODE=0`
- `AWS_REGION`, `S3_BUCKET`
- `DEEPGRAM_API_KEY`
- `MERGE_API_KEY`, `MERGE_ACCOUNT_TOKEN`

**Optional:**
- `AWS_PROFILE` (if not using IAM role)
- `USE_BEDROCK` (set to 0 to disable Bedrock)

### Security Considerations

1. **Never commit .env** - already in `.gitignore`
2. **Use IAM roles** for AWS in production (not access keys)
3. **Rotate API keys** regularly
4. **Restrict S3 bucket** access to app only
5. **Enable CloudWatch** logging for Bedrock calls

### Scaling

- Streamlit can handle 10-50 concurrent users per instance
- For more, deploy behind load balancer
- Use Redis for session state persistence
- Consider serverless (AWS Lambda + API Gateway) for the agent pipeline

---

## Roadmap

Future enhancements:

- [ ] Real Island browser extension integration
- [ ] Actual Dagster deployment (not just simulation)
- [ ] PostgreSQL for run storage (not just JSON files)
- [ ] Email integration (auto-forward broker emails)
- [ ] Slack notifications for high-score deals
- [ ] Multi-user authentication
- [ ] Deal comparison view
- [ ] Export to Excel/PDF
- [ ] Mobile app

---

## License

MIT License - see LICENSE file for details

---

## Support

For issues, questions, or feature requests:

- **Email**: your-email@example.com
- **GitHub**: [your-repo-url]
- **Slack**: [your-slack-channel]

---

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - UI framework
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - LLM infrastructure
- [Deepgram](https://deepgram.com/) - Speech-to-text
- [Merge](https://merge.dev/) - Unified CRM API
- [Island](https://island.io/) - Browser security (simulated)
- [Spectro Cloud](https://spectrocloud.com/) - Kubernetes management (simulated)
- [Vanta](https://vanta.com/) - Security compliance (simulated)
- [Thoropass](https://thoropass.com/) - Security compliance (simulated)
- [Dagster](https://dagster.io/) - Orchestration (simulated)
- [Coder](https://coder.com/) - Dev environments

---

**Built for CRE/REPE professionals who want to close more deals, faster.**
