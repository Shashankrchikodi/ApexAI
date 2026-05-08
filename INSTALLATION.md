# ApexAI — Complete Installation Guide

Comprehensive setup instructions for all platforms.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation (All Platforms)](#installation-all-platforms)
3. [Verify Installation](#verify-installation)
4. [Getting Your API Key](#getting-your-api-key)
5. [Run the Application](#run-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## System Requirements

### Minimum
- **Python 3.9+**
- **4GB RAM**
- **Modern browser** (Chrome, Safari, Firefox, Edge)
- **Internet connection** (for live AI; optional for demo)

### Recommended
- **Python 3.11+**
- **8GB RAM**
- **SSD storage** (for faster operations)
- **Anthropic API Key** (for live Claude integration)

---

## Installation (All Platforms)

### 1. Clone the Repository

```bash
git clone https://github.com/Shashankrchikodi/ApexAI.git
cd ApexAI
```

### 2. Create Python Virtual Environment

#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Verify Installation

Check everything installed correctly:

```bash
python -c "import fastapi; import uvicorn; import anthropic; print('✅ All dependencies installed!')"
```

Expected output: `✅ All dependencies installed!`

---

## Getting Your API Key

**Optional but recommended** for live AI features.

### Step-by-Step:

1. Go to: https://console.anthropic.com
2. Sign up or log in with your GitHub account
3. Navigate to **"API Keys"** section
4. Click **"Create New API Key"**
5. Give it a name: `ApexAI Local`
6. Copy the key (it starts with `sk-ant-`)
7. Keep it safe — never share or commit to Git

### Set the API Key:

#### macOS/Linux:
```bash
export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
```

#### Windows (PowerShell):
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-YOUR-KEY"
```

#### Windows (Command Prompt):
```cmd
set ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
```

#### Permanently (all platforms):
Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
```

Then the app will load it automatically.

---

## Run the Application

### macOS/Linux (Easiest):

```bash
chmod +x start.sh
./start.sh
```

### macOS/Linux (Manual):

```bash
source venv/bin/activate
cd backend
python -m uvicorn main:app --port 8000 --reload
```

### Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
cd backend
python -m uvicorn main:app --port 8000 --reload
```

### Windows (Command Prompt):

```cmd
venv\Scripts\activate.bat
cd backend
python -m uvicorn main:app --port 8000 --reload
```

### Output Should Look Like:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     Press CTRL+C to quit
```

---

## Open in Browser

Go to: **http://localhost:8000**

You should see the ApexAI interface.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### "Port 8000 already in use"

**Solution:** Use a different port:
```bash
python -m uvicorn main:app --port 8001 --reload
# Then open http://localhost:8001
```

### "ANTHROPIC_API_KEY not set"

**This is OK!** The app works in demo mode without an API key.

To enable live AI:
```bash
export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
```

Then restart the server.

### "Nothing happens when I click Send"

**Possible causes:**
1. Backend not running (check console for `INFO: Application startup complete`)
2. No API key set (works in demo mode, but slower)
3. Network issue (try refreshing the page)

**Solution:**
1. Stop the server (Ctrl+C)
2. Restart it with: `python -m uvicorn main:app --port 8000 --reload`
3. Refresh the browser

### "Python command not found"

**Solution:**
- **macOS:** Install Python from https://www.python.org/downloads/
- **Windows:** Install Python from https://www.python.org/downloads/ (check "Add Python to PATH")
- **Linux:** `sudo apt-get install python3 python3-venv`

### "Permission denied: ./start.sh"

**Solution (macOS/Linux):**
```bash
chmod +x start.sh
./start.sh
```

---

## Advanced Configuration

### Custom Port

Edit `start.sh` or run directly:

```bash
python -m uvicorn main:app --port 9000 --reload
```

Then open: **http://localhost:9000**

### Production Deployment

For production, use a production-grade ASGI server:

```bash
pip install gunicorn
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Custom Agents

Edit `backend/prompts.py` to add or modify agent system prompts.

### Database Integration

Replace in-memory stores in `backend/tools.py` with real databases (PostgreSQL, MongoDB, etc.)

### Environment Variables

Create `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000,https://example.com
DATABASE_URL=postgresql://user:pass@localhost/apexai
```

Then load with:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Verify It's Working

### Dashboard Test:

1. Open http://localhost:8000
2. Click **`+ New Search`**
3. Fill in any values
4. Click **`Launch Search`**
5. Select an Agent
6. Click Send

You should see a response! ✅

### API Test:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ok","version":"1.0.0","agents":12}
```

---

## Next Steps

1. **Customize Agents:** Edit `backend/prompts.py`
2. **Add Data:** Integrate CRM in `backend/tools.py`
3. **Deploy:** Follow production deployment section
4. **Document:** Update README.md with your changes

---

## Support

- 📖 Check `QUICK_START.md` for quick help
- 📝 Read `README.md` for project overview
- 🔍 Review `backend/main.py` for API documentation
- 💬 Debug: Check console output for error messages

---

## License & Credits

Built with ❤️ using:
- FastAPI (backend framework)
- Anthropic Claude (AI)
- Vanilla JS (frontend)

Enjoy! 🚀
