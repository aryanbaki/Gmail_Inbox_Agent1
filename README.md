# Gmail Inbox Agent

Gmail Inbox Agent is a Streamlit app that helps review recent inbox messages. It can run with fake demo data or connect to Gmail through local OAuth, fetch the last 200 inbox messages, group similar emails, and assign priority labels.

## Privacy and Security

Do not commit `credentials.json` or `token.json` to GitHub.

For Gmail Mode, place your downloaded Google OAuth client file in the project root and name it `credentials.json`. The app creates `token.json` after your first successful browser login. Both files are private, local-only files and are already ignored by Git.

Demo Mode does not require Gmail credentials.

## Local Setup

```bash
cd Gmail_Inbox_Agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Gmail Mode

1. Create OAuth credentials for the Gmail API in Google Cloud.
2. Download the OAuth client JSON file.
3. Rename it to `credentials.json`.
4. Place it in the project root next to `app.py`.
5. Run the app and choose Gmail Mode in the sidebar.
6. Complete the browser login. The app will create `token.json` locally.

Gmail Mode fetches the last 200 inbox messages and analyzes them locally. This iteration is read/analyze only; archive and label actions are not implemented yet.

## Current Status

Demo Mode and Gmail Mode are available. Demo Mode uses fake email data from `data/mock_emails.csv`; Gmail Mode uses local OAuth and your private `credentials.json`.
