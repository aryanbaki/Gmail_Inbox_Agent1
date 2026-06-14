import streamlit as st

from src.clustering import cluster_emails
from src.config import CREDENTIALS_FILE, MAX_EMAILS, TOKEN_FILE
from src.dashboard import (
    render_cluster_cards,
    render_email_count,
    render_priority_counts,
    render_sample_emails_per_cluster,
)
from src.email_parser import load_mock_email_data, parse_gmail_messages
from src.gmail_auth import GmailAuthError, authenticate_gmail, credentials_file_exists
from src.gmail_client import GmailClientError, fetch_inbox_messages
from src.priority import add_priority_labels


st.set_page_config(page_title="Gmail Inbox Agent", layout="wide")

st.title("Gmail Inbox Agent")
st.caption(
    "Review, group, and prioritize inbox messages with demo data or a local Gmail OAuth connection."
)


def prepare_dashboard_data(emails):
    """Add priorities and clusters for either demo or Gmail data."""
    emails = add_priority_labels(emails)
    return cluster_emails(emails)


def render_dashboard(emails, cluster_summary):
    """Render the shared inbox analysis dashboard."""
    if emails.empty:
        st.info("No inbox emails were found for this mode.")
        return

    count_col, cluster_col = st.columns(2)
    with count_col:
        render_email_count(emails)
    with cluster_col:
        st.metric("Email clusters", len(cluster_summary))

    render_priority_counts(emails)

    st.subheader("Cluster Summary")
    st.dataframe(cluster_summary, use_container_width=True, hide_index=True)

    st.subheader("Cluster Cards")
    render_cluster_cards(cluster_summary)

    st.subheader("Emails Grouped by Cluster")
    render_sample_emails_per_cluster(emails)


with st.sidebar:
    st.header("Mode")
    mode = st.radio("Choose an inbox source", ["Demo Mode", "Gmail Mode"])

    if mode == "Demo Mode":
        st.write("Using fake inbox data from `data/mock_emails.csv`.")
    else:
        st.write(f"Fetches the last {MAX_EMAILS} Gmail inbox messages.")
        st.write(f"Requires local `{CREDENTIALS_FILE}` in the project root.")

if mode == "Demo Mode":
    st.info("Demo Mode is active. No Gmail credentials are needed.")
    emails, cluster_summary = prepare_dashboard_data(load_mock_email_data())
    render_dashboard(emails, cluster_summary)
else:
    if not credentials_file_exists():
        st.warning(
            f"Gmail Mode needs `{CREDENTIALS_FILE}` in the project root. "
            "Create OAuth credentials in Google Cloud, download the JSON file, "
            f"rename it to `{CREDENTIALS_FILE}`, and place it next to `app.py`."
        )
        st.info(
            f"`{CREDENTIALS_FILE}` and `{TOKEN_FILE}` are private local files and are ignored by Git. "
            "Demo Mode still works without them."
        )
    else:
        try:
            with st.spinner("Connecting to Gmail and fetching inbox messages..."):
                service = authenticate_gmail()
                raw_messages = fetch_inbox_messages(service, max_results=MAX_EMAILS)
                emails = parse_gmail_messages(raw_messages)
                emails, cluster_summary = prepare_dashboard_data(emails)

            st.success(f"Fetched {len(emails)} Gmail inbox messages.")
            render_dashboard(emails, cluster_summary)
        except (GmailAuthError, GmailClientError) as error:
            st.error(str(error))
        except Exception as error:
            st.error(f"Gmail Mode could not finish: {error}")
