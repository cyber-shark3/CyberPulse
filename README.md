# CyberPulse

**Detect. Analyse. Defend.**

CyberPulse is an educational HTTP honeypot monitoring prototype. It runs a local decoy web service, records requests as security events, applies transparent rule-based detection, and presents events and alerts in a web dashboard.

> **Safety:** Keep the service bound to `127.0.0.1` for local use. Do not expose it directly to the public internet or enter real credentials. The decoy login is not a real login service. Never enter real passwords.

## Requirements
- Windows 10/11, macOS, or Linux
- Python 3.10 or newer
- Git (if cloning the repository)
- PowerShell on Windows, or Terminal on macOS/Linux
- A web browser

Check your tools:

**Windows PowerShell**
```powershell
py --version
git --version
```

**macOS/Linux**
```bash
python3 --version
git --version
```

Install Python from [python.org](https://www.python.org/downloads/) if needed. On Windows, use the `py` launcher if available. Install Git from [git-scm.com](https://git-scm.com/downloads/) if needed.

## Run CyberPulse on Windows

The following commands are for **PowerShell**, not Command Prompt. Follow them in order.

### 1. Download the project
```powershell
cd $HOME\Documents
git clone https://github.com/cyber-shark3/CyberPulse.git
cd CyberPulse
```

If you downloaded the ZIP instead, extract it and open PowerShell in the extracted `CyberPulse` folder; skip `git clone`. You must be in the project root, where `requirements.txt` and the `backend` folder are located. Check with `Get-ChildItem`.

### 2. Confirm Python
```powershell
py --version
```

If `py` is not recognised but `python` works, replace `py` with `python` in the commands below. If `python` opens the Microsoft Store, install Python from python.org and reopen PowerShell.

### 3. Create a virtual environment
```powershell
py -m venv .venv
```

This keeps CyberPulse's Python packages separate from other projects.

### 4. Activate the environment
```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell says script execution is disabled, allow scripts for this PowerShell process only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This is temporary and does not permanently change your computer's execution policy. When activation works, the prompt normally begins with `(.venv)`.

### 5. Install dependencies
```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

Wait for installation to finish. If pip reports a certificate error mentioning an invalid `CURL_CA_BUNDLE`, `REQUESTS_CA_BUNDLE`, or certificate path, check whether an environment variable is misconfigured. For the **current PowerShell window only**, clear these variables and retry:

```powershell
$env:PIP_CERT = $null
$env:REQUESTS_CA_BUNDLE = $null
$env:CURL_CA_BUNDLE = $null
$env:SSL_CERT_FILE = $null
$env:SSL_CERT_DIR = $null
py -m pip install -r requirements.txt
```

This is troubleshooting for a misconfigured local environment, not a reason to disable TLS verification. If the problem continues, check your network, proxy, Python installation, or organisation's certificate settings.

### 6. Start the server
Run this from the project root with the virtual environment activated:

```powershell
py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Keep this terminal open. A successful start should show a message similar to `Application startup complete`. The server is deliberately bound to `127.0.0.1`, making it available on your own computer rather than other devices on the network.

### 7. Open the dashboard
Open **http://127.0.0.1:8000** in your browser. Keep the server terminal open; closing it stops CyberPulse.

### 8. Check that the service is running
Open a **second** PowerShell window, leaving the server running in the first window. Run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:8000/api/summary
```

The health endpoint should return a successful response. The summary endpoint reports current event and alert counts.

### 9. Generate demo events
Click **Run demo simulation** in the dashboard. This creates synthetic records for a presentation without sending traffic from another system. Simulated records are not evidence of a real attack.

### 10. Send controlled local test requests
These requests are sent by you to your own local CyberPulse service. They are controlled tests, **not external attacks**.

Request a decoy sensitive-looking path:

```powershell
try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/decoy/.env' -UseBasicParsing } catch { Write-Host "Request completed; response: $($_.Exception.Message)" }
```

Then send six dummy login attempts to exercise the repeated-login detection rule. Use only made-up test details:

```powershell
1..6 | ForEach-Object {
    $body = '{"username":"demo-user-' + $_ + '","password":"dummy-not-a-real-password"}'
    try { Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/decoy/login' -ContentType 'application/json' -Body $body | Out-Null }
    catch { Write-Host "Request $_ returned: $($_.Exception.Message)" }
}
Write-Host 'Local test requests sent.'
```

Return to the dashboard and refresh if needed. Inspect recent events and alerts using:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/events?limit=20'
Invoke-RestMethod 'http://127.0.0.1:8000/api/alerts?limit=20'
```

The repeated-login rule checks attempts from the same source within its configured time window. These local requests may share the same source address. If no alert appears, check that the server is running, the requests completed, and the APIs show the events.

### 11. Run the automated tests
Stop the server with `Ctrl+C` in its terminal, or use another PowerShell window in the project folder. With the virtual environment activated, run:

```powershell
py -m pytest -v
```

The detection tests should report as passed. If pytest is missing, check that dependencies were installed in the active environment.

### 12. Stop and restart CyberPulse
To stop the service, go to the Uvicorn terminal and press **Ctrl+C**. To start it again later, open PowerShell and run:

```powershell
cd $HOME\Documents\CyberPulse
.\.venv\Scripts\Activate.ps1
py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

If you saved the project elsewhere, change the `cd` path to match your folder.

## Run CyberPulse on macOS or Linux
Open Terminal and run:

```bash
git clone https://github.com/cyber-shark3/CyberPulse.git
cd CyberPulse
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000** in your browser. Keep Terminal open while using the dashboard. To run tests, stop the server with `Ctrl+C` and run `python -m pytest -v` from the project root with the environment activated.

## Troubleshooting
| Problem | What to do |
|---|---|
| `py` is not recognised on Windows | Install Python, reopen PowerShell, and try `py --version`. If your installation uses `python`, replace `py` with `python`. |
| PowerShell blocks `Activate.ps1` | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. |
| `No module named uvicorn` or another missing package | Activate `.venv` and run `py -m pip install -r requirements.txt`. |
| Certificate or `CURL_CA_BUNDLE` error | Follow the certificate troubleshooting in Step 5; do not disable TLS verification. |
| Port 8000 is already in use | Stop the other process, or use `--port 8001` and open `http://127.0.0.1:8001`. |
| Browser cannot connect | Check that Uvicorn is running and that you entered `http://127.0.0.1:8000` exactly. |
| Dashboard has no events | Click **Run demo simulation** or send the controlled local requests in Step 10. |
| PowerShell does not recognise `-SkipHttpErrorCheck` | Do not use that parameter; use the `try/catch` example in Step 10. |

If the server reports a startup error, read the full traceback in the terminal and fix the first reported application error before retrying.

## Project structure
```text
CyberPulse/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, decoy routes, JSON APIs
│   ├── database.py      # SQLite persistence
│   └── detection.py     # Explainable alert rules
├── frontend/
│   └── index.html       # Dashboard UI
├── tests/
│   └── test_detection.py
├── data/                # Runtime SQLite database (gitignored)
├── .gitignore
└── requirements.txt
```

## The three pillars: Detect, Analyse, Protect
- **Detect:** identifies configured patterns such as repeated decoy login attempts and probes of sensitive-looking paths.
- **Analyse:** records request metadata and presents events, counts, severity, and alert explanations for review.
- **Protect:** supports security awareness and controlled testing by making suspicious patterns visible. The current prototype does **not** block attackers, replace a firewall, or provide production-grade protection.

## Architecture
Browser/local test client → isolated decoy HTTP routes → event logger → SQLite → rule-based detector → dashboard APIs → dashboard UI.

The current MVP is an HTTP decoy for local classroom demonstrations. It is not an SSH honeypot. Cowrie or other network-facing components would need to be added separately in an isolated lab environment.

## API reference
- `GET /` — dashboard
- `GET /api/health` — service status
- `GET /api/summary` — event and alert counts
- `GET /api/events?limit=100` — recent events
- `GET /api/alerts?limit=100` — recent alerts
- `POST /api/demo/run` — generate safe, labelled demo events
- `POST /api/alerts/{alert_id}/resolve` — resolve an alert
- `POST /decoy/login` — record a decoy login attempt without saving the submitted password
- `GET /decoy/admin` — record a probe of a decoy admin route
- `GET /decoy/.env` — record a probe of a sensitive-looking decoy path

## Security notes and limitations
- The default bind address is localhost only. Do not expose the port publicly for a casual demonstration.
- Decoy endpoints do not provide real authentication or access to real administrative functions.
- Never submit real passwords, API keys, or personal data.
- The demo simulator creates synthetic records; it does not scan or contact other systems.
- CyberPulse only observes requests that reach its own HTTP service. It does not automatically monitor all traffic on your computer or the wider internet.
- For any networked lab, use an isolated VM/network and restrictive firewall rules.
- This is an educational MVP, not a production security monitoring or incident-response system.

## Status
Educational MVP. Review and test before using it beyond a local demonstration.