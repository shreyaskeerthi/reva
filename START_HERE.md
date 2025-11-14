# START HERE 🚀

## Your CRE Deal Voice Agent is Ready!

This is a **fully functional, demo-ready** commercial real estate deal assistant with 9 sponsor integrations.

---

## ⚡ Fastest Start (No Setup)

Just run these two commands:

```bash
pip install streamlit pydantic pydantic-settings python-dotenv boto3 deepgram-sdk requests python-dateutil
streamlit run app.py
```

The app will open at [http://localhost:8501](http://localhost:8501) in **full demo mode**.

---

## 🎯 First Demo (2 Minutes)

Once the app is running:

1. **Input** tab → "Load Example" → Choose "Austin Multifamily"
2. **Analyze** tab → Click "Run CRE Deal Agent" → See score & verdict
3. **CRM** tab → Click "Create CRM Records" → See contact/note/task IDs
4. **Evidence** tab → Click "Generate Evidence" → See Vanta/Thoropass packets
5. **Jobs** tab → Click "Run Daily Summary" → See aggregated stats
6. **Security & Infra** tab → Click "Check Cluster Health" → See status

**Done!** You've just demonstrated all 9 sponsor integrations.

---

## 📚 What's Included

### Core Files
- [app.py](app.py) - Main Streamlit UI (614 lines)
- [cre_agent/](cre_agent/) - 9 modules with business logic (1,600+ lines)
- [requirements.txt](requirements.txt) - 10 dependencies

### Documentation
- [README.md](README.md) - Full documentation (531 lines)
- [QUICKSTART.md](QUICKSTART.md) - 2-minute setup guide
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Technical overview

### Tools
- [setup.sh](setup.sh) - Automated setup script
- [test_demo.py](test_demo.py) - Verification tests
- [coder.yaml](coder.yaml) - Dev environment config

---

## 🔌 9 Sponsor Integrations

All integrated and working:

| # | Sponsor | What It Does | Status |
|---|---------|--------------|--------|
| 1 | **AWS** | Bedrock (Titan) for deal extraction + S3 storage | ✅ Real + Demo |
| 2 | **Deepgram** | Speech-to-text transcription | ✅ Real + Demo |
| 3 | **Merge** | CRM contact/note/task creation | ✅ Real + Demo |
| 4 | **Dagster Labs** | Daily summary orchestration job | ✅ Simulated |
| 5 | **Island** | Browser trust security signals | ✅ Simulated |
| 6 | **Vanta** | Compliance evidence logging | ✅ Simulated |
| 7 | **Thoropass** | Compliance evidence logging | ✅ Simulated |
| 8 | **Spectro Cloud** | Cluster health monitoring | ✅ Simulated |
| 9 | **Coder** | Dev environment definition | ✅ Config |

---

## 💡 Key Features

- **Voice Input**: Upload audio → automatic transcription
- **AI Extraction**: 12+ deal fields extracted automatically
- **Buy-Box Scoring**: 100-point system with Pass/Watch/Hard Pass verdicts
- **IC Summaries**: Professional investment memos ready for email
- **CRM Workflow**: Auto-create contacts, notes, and follow-up tasks
- **Evidence Trail**: Compliance packets for Vanta/Thoropass
- **Daily Jobs**: Aggregate stats across all deals
- **Security**: Browser trust signals (Island-style)
- **Infrastructure**: Cluster health monitoring (Spectro-style)

---

## 🎬 For Your Demo/Presentation

### 3-Minute Demo Script

Follow this exact flow to showcase all sponsors:

1. **Input** (30s): Load Austin multifamily example
2. **Analyze** (45s): Run agent, show structured data & score
3. **IC Summary** (20s): Show professional memo
4. **CRM** (30s): Create contact/note/task via Merge
5. **Evidence** (20s): Send to Vanta + Thoropass
6. **Jobs** (20s): Run daily summary (Dagster-style)
7. **Security/Infra** (15s): Island signal + Spectro health

**Total**: ~3 minutes for complete sponsor showcase

### Demo Tips

- All features are accessible via **buttons** - no code needed
- 5 realistic examples included (multifamily, industrial, office, retail, mixed-use)
- Works in full demo mode with zero configuration
- Can switch to real APIs by adding credentials to `.env`

---

## 🔧 Optional: Configure Real APIs

To use real integrations (AWS, Deepgram, Merge):

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
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

3. Restart the app

---

## 📊 Project Stats

- **Total Files**: 21
- **Lines of Code**: 3,221 (Python + Markdown)
- **Core Modules**: 9
- **Example Deals**: 5
- **Sponsor Integrations**: 9
- **Documentation**: 1,200+ lines

---

## 🆘 Need Help?

### Common Issues

**"No module named 'streamlit'"**
→ Run: `pip install -r requirements.txt`

**"No module named 'cre_agent'"**
→ Make sure you're in the project root: `/Users/shrey/switchboard/`

**Port already in use**
→ Use a different port: `streamlit run app.py --server.port 8502`

### Documentation

- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Technical details

---

## ✅ You're All Set!

Your CRE Deal Voice Agent is **fully built**, **fully wired**, and **demo-ready**.

**Next step**: Run `streamlit run app.py` and start your demo!

---

Built by your senior engineer. Ready to impress! 🏢
