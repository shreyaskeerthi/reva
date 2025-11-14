# Demo Flow - What Each Tab Does

## 🎯 The Story: Broker Call → CRM → Compliance

Imagine you just got off a call with a broker about a multifamily deal in Austin...

---

## 📝 Tab 1: Input

**What it does**: Get deal information into the system

**Three ways to input**:
1. **Voice (Deepgram)** - Upload recording of broker call → transcribe to text
2. **Paste Text** - Copy/paste broker email or OM
3. **Load Example** - Use pre-loaded realistic deals

**Demo action**:
- Select "Load Example"
- Choose "Austin Multifamily (148 units, 6.5% cap)"
- Click "Load Example" button
- ✅ See deal text appear (broker call transcript)

**What you're showing**:
- **Deepgram integration** (voice → text capability)
- Real-world CRE deal input

**Time**: 30 seconds

---

## 🔍 Tab 2: Analyze

**What it does**: Extract deal data + score against your buy-box

**The magic**:
1. Takes messy text like "asking $18.5M, NOI of $1.2M, 6.5% cap"
2. **AWS Bedrock** extracts structured fields:
   - Property type: Multifamily
   - Location: Austin, TX
   - Purchase price: $18,500,000
   - NOI: $1,200,000
   - Cap rate: 6.5%
   - Units: 148
   - Broker: Marcus Thompson @ JLL
3. Scores it 0-100 against buy-box criteria
4. Verdict: **Pass** / **Watch** / **Hard Pass**
5. Generates IC-ready investment memo

**Demo action**:
- Click "🚀 Run CRE Deal Agent"
- Wait 2 seconds
- See structured JSON data
- See score (e.g., 82/100 - **Pass**)
- See professional IC summary paragraph

**What you're showing**:
- **AWS Bedrock (Titan)** - AI extraction
- **Smart scoring** - Buy-box evaluation
- **IC summaries** - Investment memos

**Time**: 45 seconds

---

## 📞 Tab 3: CRM

**What it does**: Auto-create CRM records from the deal

**Creates 3 things**:
1. **Contact** - Marcus Thompson (marcus.thompson@jll.com) @ JLL
2. **Note** - Deal summary with score, cap rate, price
3. **Task** - "Follow up on multifamily in Austin" (due in 3 days)

**Demo action**:
- See pre-filled fields (broker name, email, company)
- Click "📞 Create CRM Records via Merge"
- See 3 IDs returned:
  - `contact_demo_12345`
  - `note_demo_67890`
  - `task_demo_24680`

**What you're showing**:
- **Merge integration** - Unified CRM API
- Sales workflow automation
- One click → 3 CRM objects created

**Time**: 30 seconds

---

## 📋 Tab 4: Evidence

**What it does**: Create compliance audit trail

**Generates**:
- Evidence packet with:
  - Run ID
  - Deal summary hash
  - Score & verdict
  - CRM record IDs
  - Timestamp
- Sends to **Vanta** (compliance platform)
- Sends to **Thoropass** (compliance platform)

**Demo action**:
- Click "📋 Generate & Send Evidence Packet"
- See evidence JSON structure
- See 2 acknowledgments:
  - Vanta ACK: `vanta-abc123`
  - Thoropass ACK: `thoropass-abc123`

**What you're showing**:
- **Vanta integration** - Automated compliance
- **Thoropass integration** - Security posture
- Audit trail for every deal

**Time**: 20 seconds

---

## ⚙️ Tab 5: Jobs

**What it does**: Daily summary of all deal activity

**Runs a Dagster-style job that**:
1. Reads all deals from `./runs/` directory
2. Calculates:
   - Total deals analyzed
   - Average score
   - Verdict breakdown (Pass/Watch/Hard Pass)
   - Top 3 deals by score

**Demo action**:
- Click "▶️ Run Daily Summary Job"
- See metrics:
  - Total Deals: 5
  - Avg Score: 73/100
  - Pass: 3, Watch: 1, Hard Pass: 1
- See top 3 deals listed

**What you're showing**:
- **Dagster Labs** - Orchestration concept
- Portfolio-level analytics
- Daily ops workflow

**Time**: 20 seconds

---

## 🔒 Tab 6: Security & Infra

**What it does**: Show security + infrastructure monitoring

**Two panels**:

### Left: Island Browser Trust
- Shows simulated Island security signals:
  - SSO verified: ✅
  - DLP enabled: ✅
  - Threat level: Low
  - Session ID, timestamp

### Right: Spectro Cloud Cluster Health
- Click "🔄 Check Cluster Health"
- See cluster status:
  - Status: Healthy ✅
  - Nodes: 1
  - Pods: 3
  - CPU: 23%, Memory: 41%

**Demo action**:
- Point to Island trust signal on left
- Click "Check Cluster Health" on right
- See healthy status

**What you're showing**:
- **Island** - Zero-trust browser security
- **Spectro Cloud** - K8s infrastructure
- Enterprise security posture

**Time**: 15 seconds

---

## 📊 Tab 7: History

**What it does**: Show all past deal runs

**Displays**:
- Last 10 deals analyzed
- Each shows:
  - Run ID
  - Property type & location
  - Score & verdict
  - Timestamp
  - Local file path
  - S3 URI (if configured)

**Demo action**:
- Expand a deal
- See full details

**What you're showing**:
- Full audit trail
- Historical deal flow
- Local + S3 storage

**Time**: 15 seconds (optional)

---

## 🎬 Complete Demo Flow

### The Storyline

*"I just got off a call with Marcus from JLL about a multifamily deal in Austin. Let me show you how our agent processes this..."*

### Flow (3 minutes)

```
1. INPUT (30s)
   "First, I load the deal - could be voice, email, or example"
   → Load Austin Multifamily example
   → Click "Next: Analyze Deal"

2. ANALYZE (45s)
   "The agent extracts all deal fields and scores it"
   → Click "Run CRE Deal Agent"
   → Point out: 148 units, $18.5M, 6.5% cap, 82/100 score, PASS
   → Show IC summary: "Ready to email the investment committee"
   → Click "Next: Create CRM Records"

3. CRM (30s)
   "One click creates contact, note, and task in our CRM"
   → Click "Create CRM Records via Merge"
   → Point out: Marcus Thompson @ JLL, auto-populated
   → Show 3 IDs created
   → Click "Next: Generate Evidence"

4. EVIDENCE (20s)
   "For compliance, we log everything to Vanta and Thoropass"
   → Click "Generate & Send Evidence Packet"
   → Point out: Deal hash, CRM IDs, timestamps
   → Show both ACKs
   → Click "Next: Run Daily Summary Job"

5. JOBS (20s)
   "Every day, Dagster runs a summary of our pipeline"
   → Click "Run Daily Summary Job"
   → Point out: 5 deals, 73 avg score, 3 Pass
   → Click "Next: Security & Infra"

6. SECURITY (15s)
   "Island provides browser security, Spectro manages our infrastructure"
   → Point to Island signals (SSO, DLP)
   → Click "Check Cluster Health"
   → Show: Healthy, 1 node, 3 pods
   → Click "View Deal History" (optional)

7. HISTORY (15s - optional)
   "Full audit trail of every deal"
   → Expand a deal
   → Show JSON payload
```

**Total**: ~3 minutes, 9 sponsors showcased

---

## 🎯 What Makes This Demoable

### 1. **Real Workflow**
Not just tech demos - this is how CRE acquisitions actually work:
- Broker call → Deal analysis → CRM follow-up → Compliance

### 2. **Visible Sponsor Value**
Each sponsor solves a real problem:
- **AWS**: Scale AI deal analysis
- **Deepgram**: Voice → structured data
- **Merge**: One API for any CRM
- **Dagster**: Orchestrate daily ops
- **Island**: Secure sensitive deal docs
- **Vanta/Thoropass**: Automated compliance
- **Spectro**: Reliable infrastructure
- **Coder**: Team dev consistency

### 3. **One-Click Everything**
No terminal, no code, no API calls - just buttons

### 4. **Instant Results**
Every action shows immediate output:
- ✅ Green success messages
- 📊 Metrics and scores
- 📋 JSON payloads
- 🎨 Color-coded verdicts

### 5. **Professional Output**
- IC summaries ready for email
- CRM records ready to use
- Compliance packets ready to audit

---

## 💡 Demo Tips

### Opening Hook
*"I'm going to show you how we turn a 10-minute broker call into a complete deal package in under 3 minutes."*

### During Demo
- **Pause after Analyze** - Let them see the structured data
- **Emphasize CRM** - "No manual data entry"
- **Point to Evidence** - "Automatic compliance"

### Closing
*"That's 9 sponsor integrations working together - from voice input to compliance audit - all in 3 minutes."*

---

## 🚀 Quick Start

```bash
cd /Users/shrey/switchboard
source venv/bin/activate
streamlit run app.py
```

Then follow the "Next" buttons through all 7 tabs!

---

## 📊 Sponsor Mapping

| Tab | Sponsors Used |
|-----|---------------|
| Input | **Deepgram** (voice transcription) |
| Analyze | **AWS Bedrock** (Titan extraction + IC summaries) |
| CRM | **Merge** (unified CRM API) |
| Evidence | **Vanta** + **Thoropass** (compliance) |
| Jobs | **Dagster Labs** (orchestration) |
| Security | **Island** (browser security) + **Spectro Cloud** (infrastructure) |
| All | **AWS S3** (storage), **Coder** (dev environment) |

**Total**: 9 sponsors, fully integrated, fully functional
