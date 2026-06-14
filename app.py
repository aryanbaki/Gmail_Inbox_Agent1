import streamlit as st

from src.actions import archive_messages, apply_label_to_messages, mark_messages_read
from src.clustering import cluster_emails
from src.config import CREDENTIALS_FILE, MAX_EMAILS, TOKEN_FILE
from src.dashboard import (
    render_cluster_cards,
    render_email_count,
    render_priority_counts,
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


def suggest_label_name(cluster_emails, cluster_name):
    """Suggest a Gmail label name from cluster text and priorities."""
    text = " ".join(
        [
            str(cluster_name),
            " ".join(cluster_emails["subject"].fillna("").astype(str).tolist()),
            " ".join(cluster_emails["from_email"].fillna("").astype(str).tolist()),
        ]
    ).lower()

    if (cluster_emails["priority"] == "high").any():
        return "Gmail Assistant/Urgent"
    if any(word in text for word in ["receipt", "order", "subscription", "billing"]):
        return "Gmail Assistant/Receipts"
    if any(word in text for word in ["bank", "card", "payment", "invoice", "security"]):
        return "Gmail Assistant/Finance"
    if any(word in text for word in ["school", "project", "library", "registrar", "edu"]):
        return "Gmail Assistant/School"
    if any(word in text for word in ["newsletter", "brief", "daily"]):
        return "Gmail Assistant/Newsletters"
    if any(word in text for word in ["sale", "deal", "promo", "discount"]):
        return "Gmail Assistant/Promotions"
    return "Gmail Assistant/Review"


def get_cluster_message_ids(cluster_emails):
    """Return Gmail message IDs for a cluster."""
    if "message_id" in cluster_emails.columns:
        message_ids = cluster_emails["message_id"]
    else:
        message_ids = cluster_emails["id"]

    return [str(message_id) for message_id in message_ids.dropna().tolist()]


def show_action_result(action_name, result):
    """Display a safe Gmail action result."""
    st.success(
        f"{action_name}: {result['success_count']} succeeded, "
        f"{result['failure_count']} failed."
    )

    if result.get("label_name"):
        label_status = "created" if result.get("label_created") else "reused"
        st.info(f"Label `{result['label_name']}` was {label_status}.")

    if result["errors"]:
        with st.expander("Action errors"):
            for error in result["errors"]:
                st.write(error)

    st.info("Reload Gmail Mode to refresh the inbox and cluster view.")


def render_cluster_actions(cluster_id, cluster_emails, cluster_name, mode, service=None):
    """Render safe per-cluster Gmail actions."""
    affected_count = len(cluster_emails)
    message_ids = get_cluster_message_ids(cluster_emails)
    default_label = suggest_label_name(cluster_emails, cluster_name)

    st.warning(
        "Safety: Archive only removes the INBOX label. This app does not delete emails. "
        "Actions apply only to the messages in this selected cluster."
    )
    st.caption(f"This action area affects {affected_count} emails in this cluster.")

    confirm = st.checkbox(
        f"I understand this will affect {affected_count} emails in Cluster {cluster_id}.",
        key=f"confirm-{mode}-{cluster_id}",
    )

    label_name = st.text_input(
        "Label to apply",
        value=default_label,
        key=f"label-{mode}-{cluster_id}",
    )

    archive_col, read_col, label_col = st.columns(3)

    if mode == "Demo Mode":
        with archive_col:
            if st.button(
                "Archive this group",
                key=f"archive-demo-{cluster_id}",
                disabled=not confirm,
            ):
                st.success(f"Demo only: would archive {affected_count} emails.")
        with read_col:
            if st.button(
                "Mark group as read",
                key=f"read-demo-{cluster_id}",
                disabled=not confirm,
            ):
                st.success(f"Demo only: would mark {affected_count} emails as read.")
        with label_col:
            if st.button(
                "Apply label to group",
                key=f"label-demo-{cluster_id}",
                disabled=not confirm,
            ):
                st.success(
                    f"Demo only: would apply `{label_name}` to {affected_count} emails."
                )
        return

    if not message_ids:
        st.error("No Gmail message IDs were found for this cluster.")
        return

    with archive_col:
        if st.button(
            "Archive this group",
            key=f"archive-gmail-{cluster_id}",
            disabled=not confirm,
        ):
            result = archive_messages(service, message_ids)
            show_action_result("Archive group", result)

    with read_col:
        if st.button(
            "Mark group as read",
            key=f"read-gmail-{cluster_id}",
            disabled=not confirm,
        ):
            result = mark_messages_read(service, message_ids)
            show_action_result("Mark group as read", result)

    with label_col:
        if st.button(
            "Apply label to group",
            key=f"label-gmail-{cluster_id}",
            disabled=not confirm or not label_name.strip(),
        ):
            result = apply_label_to_messages(service, message_ids, label_name.strip())
            show_action_result("Apply label to group", result)


def render_grouped_emails_with_actions(emails, mode, service=None):
    """Show grouped emails and safe action controls for each cluster."""
    for cluster_id in sorted(emails["cluster_id"].unique()):
        cluster_emails = emails[emails["cluster_id"] == cluster_id]
        cluster_name = cluster_emails["cluster_name"].iloc[0]

        with st.expander(f"Cluster {cluster_id}: {cluster_name}", expanded=True):
            st.dataframe(
                cluster_emails[["priority", "from_email", "subject", "date", "snippet"]],
                use_container_width=True,
                hide_index=True,
            )
            render_cluster_actions(cluster_id, cluster_emails, cluster_name, mode, service)


def render_dashboard(emails, cluster_summary, mode, service=None):
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

    st.subheader("Action Safety")
    st.warning(
        "Archive does not delete emails. Deleted emails are not supported in this app. "
        "Actions apply only to selected cluster messages."
    )

    st.subheader("Emails Grouped by Cluster")
    render_grouped_emails_with_actions(emails, mode, service)


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
    render_dashboard(emails, cluster_summary, mode)
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
            render_dashboard(emails, cluster_summary, mode, service)
        except (GmailAuthError, GmailClientError) as error:
            st.error(str(error))
        except Exception as error:
            st.error(f"Gmail Mode could not finish: {error}")
