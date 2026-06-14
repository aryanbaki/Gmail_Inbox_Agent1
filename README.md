# Gmail Inbox Agent

Gmail Inbox Agent is a Streamlit app that will help review recent Gmail inbox messages. Future versions will connect to Gmail, fetch recent emails, group similar messages, assign priority labels, and let the user review or archive email groups.

## Privacy and Security

Do not commit `credentials.json` or `token.json` to GitHub.

The app will eventually expect a local `credentials.json` file in the project root after Gmail API setup is added. That file should stay only on your machine. A generated `token.json` file may also appear later after authentication and must also remain local.

This starter scaffold does not include Gmail API logic and does not require Gmail credentials.

## Local Setup

```bash
cd Gmail_Inbox_Agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Current Status

Starter scaffold only. The app currently runs in demo mode using fake email data from `data/mock_emails.csv`.
