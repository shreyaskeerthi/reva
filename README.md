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
