# GitHub Setup Guide

## 🚀 Quick Push (5 Minutes)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `reva-cre-deal-intelligence` (or your choice)
3. Description: `CRE Deal Intelligence Platform with voice transcription, AI extraction, and CRM automation`
4. Choose: **Private** or **Public**
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Initialize Git Locally

```bash
cd /Users/shrey/switchboard
git init
git add .
git commit -m "Initial commit: REVA CRE Deal Intelligence Platform

✅ Audio input with Deepgram speech-to-text
✅ Auto-flow pipeline (5 automated steps)
✅ Real API integrations (AWS, Deepgram, Merge)
✅ REVA typewriter aesthetic with blue/purple theme
✅ Dark mode toggle
✅ 9 sponsor integrations
✅ Buy-box scoring and IC summaries
✅ CRM automation (contact/note/task)
✅ Compliance evidence packets
✅ Demo mode for zero-config testing"
```

### Step 3: Push to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/reva-cre-deal-intelligence.git
git branch -M main
git push -u origin main
```

**That's it!** Your project is now on GitHub.

---

## 🔐 Authentication Options

### Option A: HTTPS (Easier)
GitHub will prompt for credentials:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your actual password)

**Get a token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `reva-project`
4. Scopes: Check `repo` (full control of private repositories)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again)
7. Use this token as your password when pushing

### Option B: SSH (More Secure)
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub:
# 1. Go to https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Paste the public key
# 4. Click "Add SSH key"

# Then push using SSH URL:
git remote set-url origin git@github.com:YOUR_USERNAME/reva-cre-deal-intelligence.git
git push -u origin main
```

---

## 📝 What Gets Pushed

### Files Included ✅
```
✅ app_final.py              (Main application)
✅ reva_theme.py             (Theme system)
✅ requirements.txt          (Dependencies)
✅ cre_agent/                (All business logic)
✅ static/                   (Browser telemetry)
✅ .env.example              (Config template)
✅ .gitignore                (Exclusions)
✅ coder.yaml                (Dev environment)
✅ setup.sh                  (Setup script)
✅ All documentation (*.md)
```

### Files Excluded ❌
```
❌ .env                      (Your secrets - in .gitignore)
❌ venv/                     (Virtual environment)
❌ __pycache__/              (Python cache)
❌ runs/                     (Local deal data)
❌ *.pyc                     (Compiled Python)
```

---

## 🔒 Security Check

Before pushing, verify `.gitignore` excludes sensitive files:

```bash
cat .gitignore
```

Should include:
```
.env
venv/
__pycache__/
*.pyc
runs/
*.log
.DS_Store
```

**IMPORTANT**: Never commit `.env` with real API keys!

---

## 📚 Add README for GitHub

The existing README.md will be your GitHub landing page. It already includes:
- Project description
- Features
- Setup instructions
- Usage guide
- Sponsor integrations

---

## 🔄 Future Updates

After initial push, make updates with:

```bash
# Make changes to your files...

# Stage changes
git add .

# Commit with message
git commit -m "Description of what you changed"

# Push to GitHub
git push
```

### Common Update Workflows

**Add new feature:**
```bash
git add .
git commit -m "feat: Add new feature name"
git push
```

**Fix bug:**
```bash
git add .
git commit -m "fix: Fix specific issue"
git push
```

**Update documentation:**
```bash
git add .
git commit -m "docs: Update setup guide"
git push
```

**Refactor code:**
```bash
git add .
git commit -m "refactor: Improve code structure"
git push
```

---

## 🌿 Branching (Optional)

For feature development:

```bash
# Create new branch
git checkout -b feature/new-feature

# Make changes...
git add .
git commit -m "Add new feature"

# Push branch
git push -u origin feature/new-feature

# Create Pull Request on GitHub
# Merge when ready
```

---

## 🔍 Check Status Anytime

```bash
# See what's changed
git status

# See commit history
git log --oneline

# See remote URL
git remote -v

# See current branch
git branch
```

---

## ❌ Undo Mistakes

**Undo last commit (keep changes):**
```bash
git reset --soft HEAD~1
```

**Undo changes to a file:**
```bash
git checkout -- filename.py
```

**Remove file from staging:**
```bash
git reset HEAD filename.py
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Initialize repo | `git init` |
| Check status | `git status` |
| Stage all files | `git add .` |
| Stage specific file | `git add filename.py` |
| Commit | `git commit -m "message"` |
| Push | `git push` |
| Pull latest | `git pull` |
| Clone repo | `git clone URL` |
| View history | `git log` |
| Create branch | `git checkout -b branch-name` |
| Switch branch | `git checkout branch-name` |
| Delete branch | `git branch -d branch-name` |

---

## 🐛 Troubleshooting

### "fatal: not a git repository"
```bash
git init
```

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/repo.git
```

### "failed to push some refs"
```bash
git pull origin main --rebase
git push
```

### "Permission denied (publickey)"
Use HTTPS instead of SSH, or set up SSH keys (see Option B above)

### "Large files not allowed"
GitHub has a 100MB file size limit. Check:
```bash
find . -type f -size +50M
```

---

## 🎉 You're Done!

Once pushed, your repo will be at:
```
https://github.com/YOUR_USERNAME/reva-cre-deal-intelligence
```

You can:
- ✅ Share the link with others
- ✅ Clone it on other machines
- ✅ Deploy from GitHub (Streamlit Cloud, Heroku, etc.)
- ✅ Set up CI/CD pipelines
- ✅ Collaborate with team members

---

## 📱 GitHub Desktop (Alternative)

If you prefer a GUI:

1. Download GitHub Desktop: https://desktop.github.com/
2. Sign in with your GitHub account
3. Click "Add" → "Add Existing Repository"
4. Select `/Users/shrey/switchboard`
5. Write commit message
6. Click "Publish repository"

Done!
