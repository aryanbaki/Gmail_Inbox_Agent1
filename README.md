# Gmail Inbox Agent

Gmail Inbox Agent is a Streamlit dashboard for reviewing an inbox faster. It groups similar emails, adds priority labels, gives short reasons for each priority, and lets the user search, filter, export, and review messages from one screen.

The app has two modes:

- Demo Mode uses fake email data and is safe for public deployment.
- Gmail Mode uses local OAuth files to connect to a real Gmail inbox on your own computer.

## Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- scikit-learn
- Plotly
- Gmail API
- Google OAuth
- TF-IDF text features
- KMeans clustering

## Features

- Loads 200 fake emails for public demos.
- Connects to Gmail locally with OAuth when `credentials.json` is provided.
- Fetches recent inbox messages in Gmail Mode.
- Parses sender, subject, date, snippet, body, labels, message ID, and thread ID.
- Groups similar emails into clusters.
- Adds high, medium, and low priority labels.
- Explains why each email received its priority.
- Searches by text across sender, subject, body, and snippet.
- Filters by priority, cluster, sender, and unread status.
- Shows metrics for total emails, unread emails, priority counts, and cluster counts.
- Shows charts, grouped tables, expandable email previews, and a cluster map.
- Exports processed emails, cluster summaries, and high priority emails as CSV.
- Supports safe local Gmail actions: archive, mark as read, and apply labels.

## How I Built It

I built the project as a Streamlit app so the inbox workflow could be used from a browser without building a separate frontend. The app is split into modules so each part has a clear job:

- `app.py` builds the dashboard and connects the workflow.
- `src/email_parser.py` loads demo data and parses Gmail messages.
- `src/gmail_auth.py` handles local OAuth login.
- `src/gmail_client.py` fetches Gmail inbox messages.
- `src/clustering.py` groups similar emails with TF-IDF and KMeans.
- `src/priority.py` assigns priority labels and reasons.
- `src/actions.py` handles safe Gmail actions.
- `data/mock_emails.csv` powers the public demo.

The project started as a way to make an inbox easier to understand at a glance. Instead of reading every message one by one, the app summarizes the inbox into groups, priorities, charts, and searchable tables.

## What I Learned

- How to connect a Python app to the Gmail API.
- How OAuth works with local `credentials.json` and `token.json` files.
- How to keep private credentials out of GitHub.
- How to use TF-IDF to turn email text into features.
- How KMeans can group similar emails.
- How rule-based priority scoring can make a dashboard more useful.
- How to design a public demo that does not expose a real inbox.
- How to make destructive email actions safer by avoiding permanent delete.

## What I Would Improve

- Add web OAuth so Gmail Mode can work securely in a deployed app.
- Add user accounts and per-user saved settings.
- Add better priority scoring with a trained model.
- Add automatic label suggestions for each cluster.
- Add calendar-style follow-up reminders.
- Add background refresh instead of manual reloads.
- Add tests for Gmail parsing, clustering, and priority rules.

## Privacy And Security

Do not commit these files:

- `credentials.json`
- `token.json`
- `.streamlit/secrets.toml`
- `.env`

`credentials.json` contains the OAuth client setup. `token.json` is created after login and stores local access for the selected Gmail account. Both files are ignored by Git.

Public deployment should use Demo Mode only. Gmail Mode is for local use unless web OAuth is added later.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints in the terminal.

## Demo Mode

Demo Mode is the safest way to run the project publicly.

1. Start the app.
2. Choose `Demo Mode` in the sidebar.
3. Use search, filters, charts, exports, and simulated action buttons.

Demo Mode does not need `credentials.json` or `token.json`.

## Gmail Mode

Gmail Mode is meant for local use.

1. Open Google Cloud Console.
2. Create or choose a project.
3. Enable the Gmail API.
4. Configure the OAuth consent screen.
5. Create OAuth credentials for a Desktop app.
6. Download the OAuth JSON file.
7. Rename it to `credentials.json`.
8. Place it in the project root next to `app.py`.
9. Run the app and choose `Gmail Mode`.
10. Complete the browser login.

The app uses the Gmail modify scope because it can archive messages, mark messages as read, and apply labels:

```text
https://www.googleapis.com/auth/gmail.modify
```

Archive only removes the `INBOX` label. The app does not permanently delete messages.

## Deploy

This app is ready for Streamlit Community Cloud in Demo Mode.

Use these settings when creating the app:

- Repository: `aryanbaki/Gmail_Inbox_Agent1`
- Branch: `main`
- Main file path: `app.py`

Do not upload Gmail OAuth files to Streamlit Cloud. The deployed version should use the fake demo inbox.

Deploy from Streamlit Cloud:

```text
https://share.streamlit.io/
```

The deployed app can be shared after Streamlit finishes building it.
