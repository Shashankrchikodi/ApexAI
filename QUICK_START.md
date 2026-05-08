# ⚡ ApexAI — Quick Start (2 Minutes)

Get ApexAI running in under 2 minutes.

## Prerequisites

- **Python 3.9+** installed
- **Git** installed (optional, but recommended)

---

## Step 1: Clone & Navigate (30 seconds)

```bash
git clone https://github.com/Shashankrchikodi/ApexAI.git
cd ApexAI
```

---

## Step 2: Choose Your OS

### macOS/Linux (EASIEST) ⭐

```bash
chmod +x start.sh
./start.sh
```

**That's it!** Skip to **Step 3**.

---

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd backend
python -m uvicorn main:app --port 8000 --reload
```

---

### Windows (Command Prompt)

```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
cd backend
python -m uvicorn main:app --port 8000 --reload
```

---

## Step 3: Open in Browser

Go to: **http://localhost:8000**

You should see the ApexAI interface! ✅

---

## Step 4: Try It Out (90 seconds)

1. **Click `+ New Search`** (top-right)
2. **Fill in:**
   - Client Name: `Acme Corp`
   - Role Title: `Chief Financial Officer`
   - Codename: `Project Alpha`
3. **Click `Launch Search`**
4. **Pick an Agent** (e.g., `Position Spec 📄`)
5. **Type:** `"Write a position specification for this role"`
6. **Click Send** (→ button)
7. **Watch it work!** 🎉

---

## ✅ You're Running ApexAI!

**No API key required** for demo mode.

### Optional: Add Live AI

To enable real Claude AI responses:

1. Get API key: https://console.anthropic.com
2. Copy your key (starts with `sk-ant-`)
3. Set it:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
   ```
4. Restart the server
5. Done!

---

## 📚 Next Steps

- **Full setup:** Read `INSTALLATION.md`
- **Project overview:** Read `README.md`
- **Customize agents:** Edit `backend/prompts.py`

---

## 🆘 Stuck?

- **Port 8000 in use?** Use `--port 8001` instead
- **ModuleNotFoundError?** Run `pip install -r requirements.txt` again
- **Nothing happening?** Check backend console for errors

**All good?** Enjoy ApexAI! 🚀
