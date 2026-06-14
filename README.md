# Gmail Inbox Agent

Gmail Inbox Agent is a Streamlit app that helps review recent inbox messages. It can run with fake demo data or connect to Gmail through local OAuth, fetch the last 200 inbox messages, group similar emails, assign priority labels, and take safe actions on clustered messages.

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

Gmail Mode fetches the last 200 inbox messages and analyzes them locally. It uses the `gmail.modify` scope so it can safely archive, mark as read, and label selected messages.

## Gmail Actions

Actions are available only after messages are grouped by cluster.

- Archive this group: removes the `INBOX` label from messages in the selected cluster. This does not delete emails.
- Mark group as read: removes the `UNREAD` label from messages in the selected cluster.
- Apply label to group: creates the suggested label if it does not exist, then applies it to messages in the selected cluster.

Deleted emails are not supported in this app. There is no permanent delete action.

In Demo Mode, action buttons are simulated only. In Gmail Mode, actions affect only the messages in the selected cluster after you confirm the count shown in the app.

To test safely, start with a small, obvious cluster such as promotions or newsletters. Confirm the message count before clicking an action, then reload Gmail Mode to fetch the updated inbox.

## Current Status

Demo Mode and Gmail Mode are available. Demo Mode uses fake email data from `data/mock_emails.csv`; Gmail Mode uses local OAuth and your private `credentials.json`.
