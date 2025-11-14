# REVA Final App - Complete Guide

## 🎯 What This Is

The **final, production-ready** CRE Deal Intelligence platform with:
- ✅ Real Deepgram speech-to-text
- ✅ Real AWS Bedrock AI extraction
- ✅ Real Merge CRM integration
- ✅ Auto-flow (one button runs everything)
- ✅ Typewriter aesthetic (blue/purple theme)
- ✅ Dark mode
- ✅ Film grain texture

## 🚀 Quick Start

### Option 1: Demo Mode (No Setup)
```bash
cd /Users/shrey/switchboard
source venv/bin/activate
streamlit run app_final.py
```

Works immediately with simulated responses!

### Option 2: Real APIs (10 min setup)

1. **Get API Keys:**
   - Deepgram: https://console.deepgram.com/
   - AWS: `aws configure` + enable Bedrock
   - Merge: https://app.merge.dev/

2. **Edit `.env`:**
```bash
DEMO_MODE=0
DEEPGRAM_API_KEY=your_key
AWS_REGION=us-east-1
S3_BUCKET=your-bucket
USE_BEDROCK=1
MERGE_API_KEY=your_key
MERGE_ACCOUNT_TOKEN=your_token
```

3. **Run:**
```bash
streamlit run app_final.py
```

See [SETUP_REAL_APIS.md](SETUP_REAL_APIS.md) for detailed instructions.

---

## 🎤 How to Use

### Method 1: Audio File (Voice Input)

1. Click "🎤 AUDIO FILE" radio button
2. Upload `.wav`, `.mp3`, `.m4a`, or `.flac` file
3. Click "🎤 TRANSCRIBE WITH DEEPGRAM"
4. Wait ~2-5 seconds
5. See transcript appear
6. Edit if needed
7. Click "🚀 RUN FULL ANALYSIS"
8. Watch automated pipeline!

**With Real Deepgram:**
- Uses Nova-2 model
- Accurate transcription
- Smart formatting
- Costs ~$0.26/hour of audio

**With Demo Mode:**
- Returns realistic fake transcript
- Instant response
- Free

### Method 2: Text Input

1. Click "📄 TEXT" radio button
2. Paste broker email, OM, or notes
3. Click "🚀 RUN FULL ANALYSIS"
4. Done!

### Method 3: Load Example

1. Click "📋 EXAMPLE" radio button
2. Select from 5 realistic deals
3. Click "🚀 RUN FULL ANALYSIS"
4. Done!

---

## ⚡ Auto-Flow Pipeline

When you click "RUN FULL ANALYSIS", it automatically:

```
► STEP 1/5: Analyzing deal structure...
  • Extracts fields (price, NOI, cap rate, location, broker, etc.)
  • Scores vs buy-box (0-100)
  • Generates verdict (Pass/Watch/Hard Pass)
  • Creates IC summary
  ✅ DEAL ANALYZED - 82/100 PASS

► STEP 2/5: Creating CRM records...
  • Creates contact (broker name, email, company)
  • Creates note with deal summary
  • Creates follow-up task
  ✅ CRM RECORDS CREATED: contact_12345

► STEP 3/5: Generating evidence packets...
  • Builds compliance packet
  • Sends to Vanta
  • Sends to Thoropass
  ✅ EVIDENCE SENT: Vanta vanta-abc, Thoropass thoropass-xyz

► STEP 4/5: Running daily summary job...
  • Reads all deals from ./runs/
  • Calculates avg score, verdicts
  • Finds top 3 deals
  ✅ PIPELINE SUMMARY: 5 deals, 73/100 avg

► STEP 5/5: Checking infrastructure...
  • Gets cluster health
  • Shows nodes, pods, CPU, memory
  ✅ CLUSTER STATUS: HEALTHY - 1 nodes, 3 pods

✅ ANALYSIS COMPLETE
```

Total time: 10-15 seconds (real APIs) or 2-3 seconds (demo)

---

## 🎨 Visual Style

### Theme: REVA Research Lab
- **Font**: IBM Plex Mono (typewriter everywhere)
- **Colors**: Blue → Purple gradient (`#0B5CFF` to `#7B2CBF`)
- **Texture**: Film grain overlay
- **Borders**: Dotted/dashed
- **Animation**: Typewriter flicker on title

### Dark Mode
Click "🌓 DARK" button to toggle

**Light Mode:**
- Background: `#F6F8FF` (off-white)
- Text: `#0B1020` (dark blue)

**Dark Mode:**
- Background: `#0B1020` (dark blue)
- Text: `#F6F8FF` (off-white)

---

## 📊 What Gets Created

### Local Files
```
./runs/
├── {run_id}.json         # Full deal analysis
└── evidence_log.jsonl    # Compliance trail
```

### S3 (if configured)
```
s3://your-bucket/cre-deals/
└── {run_id}.json
```

### CRM Records (if Merge configured)
- **Contact**: Broker name, email, company
- **Note**: Deal summary with score
- **Task**: "Follow up on [property] in [location]"

---

## 🔧 Configuration

### Buy-Box Settings (Sidebar)
- **Min/Max Cap Rate**: Target return range
- **Max LTV**: Maximum leverage
- **Min/Max Deal Size**: Price range
- **Markets**: Preferred cities
- **Property Types**: Asset classes

### Integration Status (Sidebar)
Shows ✅/❌ for each:
- AWS (Bedrock + S3)
- Deepgram (Speech-to-text)
- Merge (CRM)

---

## 🎯 Use Cases

### 1. Broker Call Analysis
1. Record broker call on phone
2. Export as `.mp3`
3. Upload to REVA
4. Transcribe → Analyze
5. Auto-creates CRM follow-up
6. Done!

### 2. Email OM Review
1. Copy/paste OM text
2. Click "RUN FULL ANALYSIS"
3. Get score + IC summary
4. Forward IC summary to team
5. Done!

### 3. Daily Pipeline Review
1. Run multiple deals through day
2. Click "Jobs" in sidebar
3. See aggregate stats
4. Review top deals
5. Done!

---

## 📱 Demo Script (3 Minutes)

### Opening (30s)
*"I'm going to show you how we turn a broker call into a complete investment package in under 3 minutes."*

### Demo (2m 30s)

**Step 1: Input** (30s)
- Click "🎤 AUDIO FILE"
- Upload broker call recording
- Click "TRANSCRIBE WITH DEEPGRAM"
- Watch transcript appear
- *"Real speech-to-text with Deepgram's Nova-2 model"*

**Step 2: Auto-Flow** (2m)
- Click "RUN FULL ANALYSIS"
- Watch progress:
  - STEP 1: AWS Bedrock extracts fields
  - STEP 2: Merge creates CRM records
  - STEP 3: Vanta/Thoropass evidence
  - STEP 4: Daily summary
  - STEP 5: Infrastructure check
- *"All 9 sponsors working together automatically"*

**Step 3: Results** (30s)
- Show verdict badge
- Show IC summary
- Show CRM records created
- *"From voice to CRM in 3 minutes"*

---

## 💰 Costs (Real APIs)

### Per Deal Analysis
- Deepgram: ~$0.01 (2-3 min audio)
- AWS Bedrock: ~$0.01 (extraction + summary)
- AWS S3: <$0.01 (storage)
- Merge: Included in plan
- **Total: ~$0.02/deal**

### Monthly (100 deals)
- Deepgram: ~$1
- AWS: ~$1
- Merge: $200/mo (CRM plan)
- **Total: ~$202/mo**

Free tiers available for all!

---

## 🐛 Troubleshooting

### Audio upload not working
- Check file format (WAV, MP3, M4A, FLAC)
- Max size: 200MB
- Try converting with: `ffmpeg -i input.m4a output.wav`

### Transcription fails
- Verify DEEPGRAM_API_KEY in `.env`
- Check API key at https://console.deepgram.com/
- Try demo mode first

### Analysis fails
- Check DEMO_MODE setting
- Verify AWS credentials: `aws sts get-caller-identity`
- Check Bedrock access approved in AWS Console

### CRM records not creating
- Verify MERGE_API_KEY and MERGE_ACCOUNT_TOKEN
- Check Merge dashboard for linked accounts
- Try demo mode first

---

## 🎯 Next Steps

### For Demo
1. Use demo mode (no setup)
2. Load example deals
3. Show auto-flow

### For Real Use
1. Set up API keys (10 min)
2. Record broker calls
3. Upload → analyze → done!

### For Production
1. Set up proper AWS IAM roles
2. Configure S3 lifecycle policies
3. Set up Merge webhooks
4. Add error monitoring (Sentry)
5. Deploy to Streamlit Cloud

---

## 📚 Related Docs

- [SETUP_REAL_APIS.md](SETUP_REAL_APIS.md) - Detailed API setup
- [START_HERE.md](START_HERE.md) - Quick start
- [README.md](README.md) - Full documentation
- [DEMO_FLOW_EXPLAINED.md](DEMO_FLOW_EXPLAINED.md) - What each step does

---

## 🎉 You're Ready!

```bash
streamlit run app_final.py
```

Then:
1. Upload audio OR paste text OR load example
2. Click "RUN FULL ANALYSIS"
3. Watch it go!

**Built for real CRE dealmaking. Powered by 9 sponsor integrations.** ⚡
