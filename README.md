# Gmail Inbox Agent

Gmail Inbox Agent is a polished dark Streamlit dashboard for reviewing a Gmail inbox more quickly. It can run in Demo Mode with fake email data, or in Gmail Mode with local OAuth so you can fetch, cluster, search, prioritize, label, mark read, and archive recent inbox messages.

The project is designed to be safe for GitHub. Real Gmail OAuth files stay local and are ignored by Git.

## What The App Does

- Loads demo emails from `data/mock_emails.csv`
- Optionally connects to Gmail locally with OAuth
- Fetches the last 200 Gmail inbox messages in Gmail Mode
- Parses sender, subject, date, snippet, body, labels, message ID, and thread ID
- Groups similar emails with TF-IDF and KMeans
- Adds priority labels: high, medium, low
- Explains each priority decision with `priority_reason`
- Lets you search and filter by text, priority, cluster, sender, and unread status
- Shows email metrics, cluster summaries, dark Plotly charts, grouped tables, and expandable previews
- Exports processed emails, cluster summaries, and high priority emails as CSV
- Provides safe Gmail actions on selected clusters

## File Structure

```text
Gmail-Inbox-Agent-1/
  app.py                       Streamlit app entry point
  requirements.txt             Python dependencies
  README.md                    Beginner setup and usage guide
  .gitignore                   Keeps private files out of Git
  .streamlit/config.toml       Streamlit display/runtime config
  .streamlit/secrets.toml.example
  data/mock_emails.csv         Fake emails for Demo Mode
  src/
    actions.py                 Safe Gmail archive/read/label actions
    clustering.py              TF-IDF and KMeans grouping
    config.py                  App constants and local paths
    dashboard.py               Small dashboard helper functions
    email_parser.py            Demo CSV loading and Gmail message parsing
    gmail_auth.py              Local OAuth authentication
    gmail_client.py            Gmail inbox fetching
    priority.py                Rule-based priority scoring and reasons
```

## Privacy And Security

Never commit these files:

- `credentials.json`
- `token.json`
- `.env`

`credentials.json` contains your local OAuth client configuration. `token.json` is created after your first successful Gmail login and grants local access according to the app scope. Both are ignored in `.gitignore`.

This app does not support permanent deletion. Archive only removes the `INBOX` label.

## Local Setup

```bash
cd /Users/aryanbaki/Documents/Buildathon/Gmail-Inbox-Agent-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Demo Mode

Demo Mode is the safest way to run the app locally or on Streamlit Cloud.

1. Start the app.
2. Choose `Demo Mode` in the sidebar.
3. Use search, filters, charts, exports, and simulated action buttons.

Demo Mode does not require `credentials.json` or `token.json`.

## Gmail Setup

Gmail Mode is intended for local VS Code or local terminal use.

1. Go to Google Cloud Console.
2. Create or choose a project.
3. Enable the Gmail API.
4. Configure the OAuth consent screen.
5. Create OAuth credentials for a desktop app.
6. Download the OAuth client JSON file.
7. Rename the downloaded file to `credentials.json`.
8. Place `credentials.json` in the project root next to `app.py`.
9. Run the app locally and choose `Gmail Mode`.
10. Complete the browser login.

After login, the app creates `token.json` locally. Keep both files private.

## Gmail Mode

Gmail Mode fetches the last 200 inbox messages using:

```python
https://www.googleapis.com/auth/gmail.modify
```

The `gmail.modify` scope is needed because the app can archive, mark as read, and apply labels. If `credentials.json` is missing, the app shows a helpful setup message and Demo Mode keeps working.

## Safe Gmail Actions

Actions apply only to the messages in the selected cluster and require confirmation.

- Archive this group: removes the `INBOX` label. It does not delete emails.
- Mark group as read: removes the `UNREAD` label.
- Apply label to group: creates the label if needed, then applies it.

Suggested labels include:

- `Gmail Assistant/Promotions`
- `Gmail Assistant/Receipts`
- `Gmail Assistant/Urgent`
- `Gmail Assistant/School`
- `Gmail Assistant/Finance`
- `Gmail Assistant/Newsletters`

Test actions on a small obvious cluster first, such as newsletters or promotions. Reload Gmail Mode after an action to refresh the inbox view.

## CSV Exports

The app can export:

- Processed email table
- Cluster summary
- High priority emails

Exports contain email analysis data only. They do not export `credentials.json`, `token.json`, or secrets.

## Streamlit Cloud Deployment

This repository can be deployed in Demo Mode.

Important: local Gmail OAuth with `credentials.json` is for local use. Streamlit Cloud should run Demo Mode only unless web OAuth is implemented later.

Do not upload `credentials.json` or `token.json` to GitHub or Streamlit Cloud.

## Troubleshooting

Missing `credentials.json`:
The app will show setup instructions in Gmail Mode. Demo Mode still works.

OAuth opens a browser but fails:
Check that the Gmail API is enabled and that your OAuth credentials are for a desktop app.

Token problems:
Stop the app, delete local `token.json`, and try Gmail Mode again. Do not commit the new token.

No messages appear:
Your inbox may be empty, or Gmail may not return messages for the selected account. Demo Mode can still be used.

Gmail actions do not appear to change the dashboard:
Reload Gmail Mode after an action. Archive removes messages from the inbox, so archived messages should disappear from the fetched inbox list.

## GitHub Notes

This project should live in its own repository, not inside another project repo.

Recommended Git commands:

```bash
cd /Users/aryanbaki/Documents/Buildathon/Gmail-Inbox-Agent-1
git status
git add .
git commit -m "Polish final Gmail Inbox Agent project"
git remote set-url origin https://github.com/aryanbaki/Gmail_Inbox_Agent1.git
git push -u origin main
```

Before pushing, make sure these files are not present in `git status`:

- `credentials.json`
- `token.json`
- `.env`
