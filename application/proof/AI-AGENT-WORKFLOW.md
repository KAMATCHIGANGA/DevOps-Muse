# STAR-AGENT — Real-World Incident Investigation Scenarios

## Scenario 1: Real-User Login Issue

### 1. Problem Statement

A registered STARCOURT user is unable to log in. The application logs contain an `Invalid credentials` message. STAR-AGENT investigates the login failure by extracting the entered username from the logs and verifying the registered username against the RDS PostgreSQL database.

### 2. Example Scenario

- Registered email: `piper@piper.com`
- Username entered: `pipercam`
- Username registered in RDS: `piper`
- Application error: `Invalid credentials`

### 3. Investigation Workflow

1. Upload the application logs using `POST /logs/upload`.
2. STAR-AGENT stores the incident and log records in SQLite.
3. Submit a real-user incident investigation request with the incident ID, email address, and incident category.
4. The agent searches the stored logs for the `Invalid credentials` message.
5. It extracts the username entered during the login attempt.
6. It queries the RDS PostgreSQL database for the registered username associated with the supplied email.
7. It compares the entered username with the registered username.
8. It returns the finding and suggested action.

### 4. Finding

The username entered during login, `pipercam`, does not match the registered username, `piper`.

### 5. Suggested Action

Ask the user to sign in using the registered username, `piper`. If the email address cannot be found, verify the supplied email address. If the username matches but authentication still fails, investigate the password or other authentication conditions.

### 6. Technology Used

- FastAPI for the investigation API.
- SQLite for incident and log storage.
- RDS PostgreSQL for registered-user verification.
- SQLAlchemy for database access.
- Python for log parsing and username comparison.
- SSH tunnel for connecting to the private RDS database from the local development environment.

### 7. Limitations

The investigation depends on the relevant login event being present in the logs and the RDS database being accessible. A username mismatch explains a discrepancy but does not independently establish every possible cause of an authentication failure.

---

## Scenario 2: Application-Wide HTTP 502 Errors

### 1. Problem Statement

Users receive HTTP 502 Bad Gateway responses when accessing multiple STARCOURT pages, including the homepage, sign-in page, and cart page.

STAR-AGENT analyzes Nginx access logs, correlates a supplied request ID with its corresponding failed request, examines the available error and timing evidence, and recommends troubleshooting actions.

### 2. Example Scenario

The uploaded log file is `502Erros.txt`.

Example record:

```text
request_id=1b99b3707c79eb2968a59e24b79b6b2f
method=GET
uri="/cart"
status=502
request_time=0.001
upstream_time=0.000
upstream_status=502
```

Other log records show HTTP 502 responses for `/` and `/signIn`.

### 3. Investigation Workflow

1. Upload `502Erros.txt` using `POST /logs/upload`.
2. STAR-AGENT stores the incident and uploaded log content in SQLite.
3. Retrieve the incident ID returned by the upload endpoint.
4. Select a request ID from the Nginx access logs.
5. Submit the incident ID and request ID to `POST /investigate/{incident_id}/trace`.
6. The agent parses the stored JSON content and searches for the requested ID.
7. It retrieves the matching log record and analyzes the available evidence.
8. It combines the matching logs with error-rate, response-time, and service-level analysis.
9. The configured AI analyzer generates an investigation report with findings and recommended actions.

### 4. Finding

The supplied logs show repeated HTTP 502 responses across multiple application pages. The example `/cart` request has an upstream status of 502, with a recorded request time of approximately one millisecond.

This indicates that requests are failing at the gateway/upstream boundary. The access logs alone do not prove the underlying root cause.

### 5. Possible Causes to Investigate

- The Flask application or application server may be stopped or unhealthy.
- Nginx may be unable to connect to the configured upstream.
- The configured upstream address or port may be incorrect.
- A network or listener configuration may be preventing connectivity.

These are hypotheses to verify, not confirmed causes.

### 6. Suggested Action

1. Verify that the Flask application or Gunicorn process is running.
2. Inspect application logs around the timestamps of the failed requests.
3. Check the Nginx upstream address and port configuration.
4. Test connectivity from Nginx to the application server.
5. Inspect Nginx error logs for connection-refused, timeout, or upstream-availability errors.
6. Retry the affected pages after confirming application availability and connectivity.

### 7. Technology Used

- FastAPI for log upload and investigation endpoints.
- SQLite for incident and log persistence.
- Python for request-ID extraction and log analysis.
- Nginx access logs for request-level evidence.
- Ollama with the configured local language model for AI-generated investigation reports.

### 8. Limitations

The investigation can identify failed requests and recommend next steps, but Nginx access logs alone cannot establish the exact root cause. Confirmation requires additional evidence, such as application logs, Nginx error logs, or infrastructure diagnostics.

---

## Overall Project Outcome

STAR-AGENT demonstrates two incident investigation workflows:

1. **Real-user login issue:** Correlates application authentication logs with registered-user data in RDS PostgreSQL to identify a username mismatch.
2. **Application-wide 502 issue:** Correlates request IDs with Nginx access logs to investigate repeated gateway errors and recommend troubleshooting actions.

Together, these scenarios demonstrate log ingestion, incident persistence, request-level investigation, database verification, rule-based analysis, and AI-assisted troubleshooting.
