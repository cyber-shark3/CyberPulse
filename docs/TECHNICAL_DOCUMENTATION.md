# CyberPulse Technical Documentation

**Project:** CyberPulse  
**Tagline:** Detect. Analyse. Defend.  
**Author:** Guadiola Shikongo  
**Version:** 0.1.0  
**Document type:** Technical documentation  
**Project status:** Educational local HTTP honeypot prototype

---

## 1. Background

CyberPulse is a small cybersecurity monitoring prototype designed to help people understand how suspicious web activity can be observed and reviewed. It runs a harmless HTTP decoy service on the local computer. When someone or a test script requests one of the decoy routes, CyberPulse records basic details about the request, checks the event against simple detection rules, and shows the result on a web dashboard.

A honeypot is a system designed to attract or observe activity that may be suspicious. CyberPulse is an **HTTP decoy for learning and demonstrations**. It is not an SSH honeypot, a full Security Information and Event Management (SIEM) platform, or a production security product.

The project follows the tagline **Detect. Analyse. Defend.** These are the three main ideas behind the system.

## 2. The problem we are solving

Suspicious web activity can be difficult for a beginner to recognise. Repeated login attempts and requests for files or routes that commonly contain sensitive information may be lost in ordinary web-server logs. Raw logs can also be difficult to understand without a clear explanation of what happened and why it matters.

CyberPulse addresses this learning and visibility problem by providing one place to:

- Record requests made to selected decoy web routes.
- Highlight patterns that match clear, explainable rules.
- Display events and alerts in a dashboard.
- Keep an event history in a local database for review.

The current prototype does not protect a real website or prove that an attacker has compromised a system. It provides a safe, local way to demonstrate the basic monitoring workflow.

## 3. Design thinking process

The project uses the five stages of design thinking: **Empathise, Define, Ideate, Prototype, and Test**.

### 3.1 Empathise — understand the user

A learner, demonstrator, or junior security analyst needs to see what happened, rather than only receive a list of technical log entries. They need clear event details, visible alert levels, and plain-language reasons for alerts.

**Design response:** Use a dashboard that presents event counts, recent events, alert severity, and explanations in one place.

### 3.2 Define — state the problem

**Problem statement:** Beginners need a safe and understandable way to observe suspicious HTTP requests and learn how simple detection rules turn request activity into alerts.

The project is limited to local learning and demonstration. It does not attempt to monitor every device on a network or replace professional security tools.

### 3.3 Ideate — consider possible solutions

The project considered a small decoy web service, a database for event history, simple detection rules, and a browser dashboard. A local HTTP service was chosen because it can be run and tested on one computer without deliberately contacting external systems.

The first rules focus on two patterns:
- Repeated login attempts from the same source within a short period.
- Requests to sensitive-looking decoy paths, such as `/decoy/.env`.

### 3.4 Prototype — build a working version

The prototype is built with:
- **Python** for the application logic.
- **FastAPI** for HTTP routes and JSON API endpoints.
- **SQLite** for local event and alert storage.
- **HTML, CSS, and JavaScript** for the dashboard.
- **pytest** for automated tests.

The prototype includes a labelled demo simulator. Simulator records are marked as simulated so they can be distinguished from requests received by the decoy routes.

### 3.5 Test — check behaviour and improve it

The detection tests check that sensitive paths are listed explicitly, normal paths are not treated as sensitive, sensitive-path requests can create an explained alert, and the fifth recent login attempt can trigger a HIGH alert.

The automated test run completed with **4 tests passed**. This is evidence that these focused detection tests passed; it is not proof that the whole application is production-ready.

---

## 4. What CyberPulse does

1. **Receives a request:** A browser or local test client requests a decoy route.
2. **Records an event:** The backend records the time, source IP address, service, event type, path, severity, summary, and supporting details.
3. **Analyses the event:** The detection rules check the event against the configured patterns.
4. **Creates an alert when a rule matches:** Alerts include a severity, title, and plain-language reason.
5. **Stores the records:** Events and alerts are saved in a local SQLite database.
6. **Displays the results:** The dashboard obtains event counts, recent events, and alerts through the API.
7. **Supports controlled demonstrations:** The demo endpoint inserts clearly labelled synthetic events without scanning or contacting other systems.

### Current decoy routes

| Route | Purpose |
|---|---|
| `POST /decoy/login` | Records a login attempt. Authentication is disabled. Submitted passwords are deliberately discarded and are not stored. |
| `GET /decoy/admin` | Records a request to a decoy administration route. |
| `GET /decoy/.env` | Records a request to a sensitive-looking decoy path. No file or secret is served. |
| `/decoy/{requested_path}` | Records requests to other supported decoy paths. |

### Detection rules

**Repeated login attempts:** CyberPulse counts recent login events from the same source. Five or more attempts within approximately 60 seconds can generate a HIGH alert.

**Sensitive-path reconnaissance:** Requests to configured sensitive-looking paths, or events classified as sensitive-path probes, can generate a MEDIUM alert.

These rules identify patterns worth reviewing. They do not prove malicious intent or a successful compromise. Alert de-duplication is used to reduce repeated alerts with the same source and title over a short period.

## 5. The three pillars: Analyse, Detect, Protect

### 5.1 Analyse

**Purpose:** Turn individual requests into information that a person can understand.

CyberPulse stores event details such as timestamps, source IP addresses, request paths, event types, severity, and summaries. The dashboard and API make these records available for review. Detection reasons explain why an alert was raised.

**Example:** A request for `/decoy/.env` is recorded as a sensitive-path probe. The event can be reviewed alongside the alert explaining that the route resembles a location where secrets might be exposed, while confirming that CyberPulse served no secret data.

**Current limitation:** Analysis is based on recorded HTTP events and simple rules. The system does not yet perform advanced behaviour analysis, machine learning, threat-intelligence matching, or network-wide traffic analysis.

### 5.2 Detect

**Purpose:** Identify activity that matches known suspicious patterns.

CyberPulse checks events against explicit rules. Repeated login attempts can trigger a HIGH alert, while sensitive-path reconnaissance can trigger a MEDIUM alert. Each alert includes a reason to help the user understand the finding.

**Example:** Five or more login attempts from one source within approximately 60 seconds can trigger a repeated-login alert.

**Current limitation:** The rules cover a small number of patterns. They may miss other forms of suspicious activity and may sometimes flag harmless testing. An alert is an indication for review, not a final judgement.

### 5.3 Protect

**Purpose:** Reduce risk during the demonstration and support safe handling of observations.

In the current prototype, protection is mainly achieved through safe design choices:
- The server is intended to bind to `127.0.0.1`, keeping it local to the computer by default.
- Decoy routes do not perform real authentication or serve real secrets.
- Submitted passwords are discarded rather than stored.
- Demo events are labelled as simulated.
- The demo simulator does not scan external systems.
- Alerts can be marked as resolved through the API.

**Important limitation:** CyberPulse does **not** currently block IP addresses, stop attacks against other applications, patch systems, enforce access policies, or automatically respond to threats. The Protect pillar currently focuses on safe containment of the lab and clear alert handling. Automated response would need careful design, testing, access controls, and audit records before being considered.

---

## 6. Technical architecture

The main flow is:

`Browser or local test client → FastAPI decoy routes → event recording → SQLite database → detection rules → API endpoints → dashboard`

### Main components

| Component | Responsibility |
|---|---|
| `backend/main.py` | Creates the FastAPI application, serves the dashboard, handles decoy routes and API requests, and calls the detection logic. |
| `backend/database.py` | Creates the SQLite tables and provides functions to save and retrieve events and alerts. |
| `backend/detection.py` | Contains the explicit detection rules and creates alerts when events match. |
| `frontend/index.html` | Provides the dashboard layout and client-side requests to the API. |
| `tests/test_detection.py` | Tests the main detection rules. |
| `requirements.txt` | Lists the Python packages needed to run and test the prototype. |
| `data/` | Holds the local SQLite database at runtime. The database file is not intended to be committed to source control. |

### Data storage

SQLite stores events and alerts in separate tables. Event records include a timestamp, source IP, service, event type, path, severity, summary, a simulated flag, and additional details. Alert records include a timestamp, source IP, severity, title, reason, related event ID, status, and a simulated flag.

Timestamps are recorded in UTC. The database is stored locally by default. The `CYBERPULSE_DB_PATH` environment variable can be used to specify a different database path.

## 7. API reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Serves the dashboard. |
| `GET` | `/api/health` | Returns basic service health and local-lab mode. |
| `GET` | `/api/summary` | Returns event and alert counts. |
| `GET` | `/api/events?limit=100` | Returns recent events. The limit is capped by the backend. |
| `GET` | `/api/alerts?limit=100` | Returns recent alerts. |
| `POST` | `/api/demo/run` | Inserts labelled synthetic events for a safe demonstration. |
| `POST` | `/api/alerts/{alert_id}/resolve` | Marks an alert as resolved. |
| `POST` | `/decoy/login` | Records a decoy login attempt without storing the submitted password. |
| `GET` | `/decoy/admin` | Records a request to the decoy admin route. |
| `GET` | `/decoy/.env` | Records a sensitive-looking path request. |

FastAPI's interactive API documentation is available locally at `/docs` while the application is running.

## 8. Installation and running

### Requirements

- Windows, macOS, or Linux.
- Python 3.10 or newer is recommended.
- Internet access may be needed to install the required Python packages.
- A modern web browser.

### Windows PowerShell

From the extracted project folder, run:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` in the browser. Keep the server terminal open while using the application.

To run the automated tests, open a second PowerShell window, activate the same virtual environment, and run:

```powershell
py -m pytest -v
```

### Safe local traffic test

The following PowerShell command sends a request to the local decoy. A 404 response is expected because the decoy does not serve a real `.env` file; the purpose is to verify that the request is recorded.

```powershell
try {
    Invoke-WebRequest "http://127.0.0.1:8000/decoy/.env" -UseBasicParsing
} catch {
    Write-Host "The decoy returned an error response, as expected for this route."
}
```

PowerShell versions differ in the parameters they support. If a request returns an expected 401 or 404, check the events API or dashboard to confirm whether it was recorded.

## 9. Development problems and fixes

The following problems were encountered while setting up and testing the project on Windows. These are environment and compatibility issues, rather than evidence of failures in the detection rules.

### 9.1 Python command did not resolve correctly

**Problem:** The `python` command initially resolved to a Windows Store alias or reported that Python could not be found, even though Python was installed.

**Fix:** Python was installed through Windows Package Manager. The Python launcher command `py` was used for the remaining setup commands because `py --version` correctly identified the installed Python version.

### 9.2 PowerShell blocked virtual-environment activation

**Problem:** PowerShell's execution policy prevented the virtual environment activation script from running.

**Fix:** The policy was bypassed for the current PowerShell process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

This is temporary for that terminal session; it does not permanently change the machine-wide execution policy.

### 9.3 Package installation failed because of a certificate path

**Problem:** Package installation was affected by an environment variable pointing to a certificate bundle path that did not exist.

**Fix:** The certificate-related environment variables were cleared for the current terminal session, then pip was upgraded and the project dependencies were installed successfully. On other computers, certificate configuration should be checked carefully rather than disabling certificate verification.

### 9.4 FastAPI rejected the alert-resolution route's return annotation

**Problem:** During startup, FastAPI reported that the return annotation `dict[str, Any] | JSONResponse` could not be used to build a response model for the alert-resolution route.

**Fix:** The route decorator was updated to explicitly disable automatic response-model generation:

```python
@app.post("/api/alerts/{alert_id}/resolve", response_model=None)
```

The application then started successfully and returned HTTP 200 for the dashboard and the demo endpoint. The route should still be tested for both successful resolution and a missing alert ID.

### 9.5 PowerShell did not recognise `-SkipHttpErrorCheck`

**Problem:** A test command used `Invoke-WebRequest -SkipHttpErrorCheck`, but the installed PowerShell version did not support that parameter.

**Fix:** The command was changed to use a `try/catch` block with `-UseBasicParsing`, which is compatible with older Windows PowerShell versions. Expected 401 and 404 responses from the decoy are handled as part of the test rather than mistaken for a server startup failure.

### 9.6 Verifying that the detection logic works

**Problem:** A dashboard can look active even when its data is synthetic. It is important to separate generated demonstration records from real requests received by the local decoy.

**Fix:** The demo simulator marks its events as simulated. Local HTTP requests can also be sent directly to the decoy routes and checked in the events and alerts APIs. The automated detection test suite completed with four passing tests.

## 10. Testing and current results

The recorded automated test run reported:

```text
4 passed in 0.89s
```

The four tests cover:
1. Sensitive decoy paths are explicitly listed.
2. A normal decoy path is not listed as sensitive.
3. A sensitive-path probe can create an explained MEDIUM alert.
4. The fifth recent login attempt can trigger a HIGH alert.

The application was also observed starting successfully with Uvicorn, serving the dashboard with HTTP 200, and accepting a demo simulation request with HTTP 200.

These checks do not constitute a full security assessment. Further integration tests should verify real decoy requests, event persistence, alert resolution, malformed requests, and dashboard refresh behaviour.

## 11. Limitations and future improvements

### Current limitations

- Local HTTP decoy only; it does not monitor all network traffic.
- Detection uses a small set of fixed rules.
- No user accounts, authentication, or role-based access control.
- No automatic IP blocking or incident response.
- No external threat-intelligence integration.
- The dashboard is a prototype and may require refreshes to show updated data.
- SQLite is suitable for this small local prototype, but not necessarily for high-volume shared monitoring.
- The system has not undergone a formal penetration test or independent security review.

### Recommended next steps

1. Clearly separate live events from synthetic demo events in every dashboard view.
2. Add automatic dashboard refresh or a WebSocket/server-sent event stream.
3. Add integration tests for the full request-to-event-to-alert flow.
4. Improve alert filtering, event search, time-range selection, and alert resolution feedback.
5. Add configurable detection rules and better alert de-duplication.
6. Add authentication and audit logging before allowing access by multiple users.
7. If broader honeypot collection is required, run a dedicated honeypot such as Cowrie in a separate, isolated virtual machine and connect it through a carefully controlled integration.
8. Perform a security review before any deployment outside a local learning environment.

## 12. Safety and responsible use

CyberPulse is intended for education, controlled testing, and demonstration. Keep it bound to `127.0.0.1` unless a properly isolated lab environment has been designed and reviewed. Do not expose the current prototype directly to the public internet. Do not enter real passwords or secrets into decoy forms. Only test systems and networks for which permission has been granted.

## 13. Conclusion

CyberPulse demonstrates a simple security-monitoring workflow: **Analyse** recorded requests, **Detect** patterns that match transparent rules, and **Protect** the learning environment through safe decoy behaviour and clear handling of alerts.

The prototype provides a foundation for learning about event logging and basic threat detection. Its present scope is intentionally limited, and further testing and security work are required before it could be considered for use beyond a local educational demonstration.

---

**Author:** Guadiola Shikongo  
**Project:** CyberPulse — Detect. Analyse. Defend.
