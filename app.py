from html import escape
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from src.actions import archive_messages, apply_label_to_messages, mark_messages_read
from src.clustering import cluster_emails
from src.config import CREDENTIALS_FILE, MAX_EMAILS, TOKEN_FILE
from src.email_parser import load_mock_email_data, parse_gmail_messages
from src.gmail_auth import GmailAuthError, authenticate_gmail, credentials_file_exists
from src.gmail_client import GmailClientError, fetch_inbox_messages
from src.priority import add_priority_labels


st.set_page_config(page_title="Gmail Inbox Agent", layout="wide")

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background: #080b12;
        color: #e5e7eb;
    }
    h1, h2, h3, h4, h5, h6,
    p, span, label, div, small,
    [data-testid="stMarkdownContainer"],
    [data-testid="stWidgetLabel"],
    [data-testid="stCaptionContainer"] {
        color: #e5e7eb;
    }
    [data-testid="stSidebar"] {
        background: #101827;
        border-right: 1px solid #1f2937;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #f8fafc;
    }
    [data-testid="stHeader"] {
        background: rgba(8, 11, 18, 0.75);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }
    .app-hero {
        border: 1px solid #1f2a44;
        border-radius: 18px;
        padding: 1.65rem 1.8rem;
        margin-bottom: 1.35rem;
        background:
            radial-gradient(circle at 20% 20%, rgba(37, 99, 235, 0.28), transparent 32%),
            linear-gradient(135deg, #111827 0%, #0b1120 55%, #111827 100%);
        box-shadow: 0 18px 60px rgba(0, 0, 0, 0.35);
    }
    .app-hero h1 {
        margin: 0 0 0.25rem 0;
        font-size: 2.45rem;
        color: #f8fafc;
    }
    .app-hero p {
        margin: 0;
        color: #cbd5e1;
        font-size: 1rem;
    }
    .hero-kicker {
        color: #93c5fd;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }
    .metric-card {
        border: 1px solid #25314a;
        border-radius: 14px;
        padding: 1rem;
        background: #111827;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1;
    }
    .section-note {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-top: -0.35rem;
        margin-bottom: 0.85rem;
    }
    .dark-table-wrap {
        width: 100%;
        overflow-x: auto;
        border: 1px solid #26344f;
        border-radius: 14px;
        background: #0b1220;
        margin: 0.65rem 0 1.1rem 0;
    }
    .dark-table {
        width: 100%;
        border-collapse: collapse;
        color: #e5e7eb;
        font-size: 0.88rem;
        min-width: 720px;
    }
    .dark-table thead th {
        background: #172033;
        color: #bfdbfe;
        font-weight: 700;
        text-align: left;
        padding: 0.8rem 0.9rem;
        border-bottom: 1px solid #334155;
        white-space: nowrap;
    }
    .dark-table tbody td {
        padding: 0.72rem 0.9rem;
        border-bottom: 1px solid #1f2a44;
        vertical-align: top;
        color: #e5e7eb;
    }
    .dark-table tbody tr:nth-child(even) {
        background: #101827;
    }
    .dark-table tbody tr:hover {
        background: #13233d;
    }
    .dark-table tbody tr:last-child td {
        border-bottom: 0;
    }
    .dark-pill {
        display: inline-block;
        border-radius: 999px;
        padding: 0.18rem 0.55rem;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: capitalize;
    }
    .priority-high {
        background: rgba(239, 68, 68, 0.18);
        color: #fecaca;
        border: 1px solid rgba(248, 113, 113, 0.35);
    }
    .priority-medium {
        background: rgba(245, 158, 11, 0.18);
        color: #fde68a;
        border: 1px solid rgba(251, 191, 36, 0.35);
    }
    .priority-low {
        background: rgba(34, 197, 94, 0.18);
        color: #bbf7d0;
        border: 1px solid rgba(74, 222, 128, 0.35);
    }
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label,
    textarea {
        background-color: #111827;
        color: #f8fafc;
        border-color: #334155;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: #94a3b8;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    [data-testid="stSelectbox"] div[data-baseweb="select"] svg,
    [data-testid="stRadio"] label p,
    [data-testid="stCheckbox"] label p {
        color: #f8fafc;
        fill: #f8fafc;
    }
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #111827;
        border: 1px solid #334155;
        color: #f8fafc;
    }
    ul[role="listbox"] li,
    div[role="option"] {
        background-color: #111827;
        color: #f8fafc;
    }
    ul[role="listbox"] li:hover,
    div[role="option"]:hover {
        background-color: #1d4ed8;
        color: #ffffff;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #1f2937;
        border-radius: 14px;
        background: #0f172a;
    }
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #0f172a;
        color: #f8fafc;
    }
    div[data-testid="stExpander"] summary {
        border-radius: 14px;
    }
    div[data-testid="stExpander"] summary:hover {
        background: #172033;
    }
    div[data-testid="stExpander"] svg {
        fill: #bfdbfe;
        color: #bfdbfe;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #26344f;
        background: #0b1220;
    }
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] div {
        color: #f8fafc;
    }
    .stDataFrame,
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        color: #e5e7eb;
    }
    [data-testid="stDataFrame"] div,
    [data-testid="stDataFrame"] span,
    [data-testid="stDataFrame"] button,
    [data-testid="stDataFrame"] input {
        color: #e5e7eb;
    }
    button,
    [data-testid="stBaseButton-secondary"],
    [data-testid="stDownloadButton"] button {
        border: 1px solid #3b82f6;
        background: #13233d;
        color: #f8fafc;
        border-radius: 10px;
    }
    button:hover,
    [data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stDownloadButton"] button:hover {
        border-color: #60a5fa;
        background: #1d4ed8;
        color: #ffffff;
    }
    button:disabled,
    [data-testid="stBaseButton-secondary"]:disabled,
    [data-testid="stDownloadButton"] button:disabled {
        border-color: #334155;
        background: #111827;
        color: #94a3b8;
        opacity: 1;
    }
    a {
        color: #93c5fd;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Gmail Inbox Agent")
st.caption(
    "Turn inbox chaos into organized action groups."
)


def prepare_dashboard_data(emails: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Add priority labels, unread flags, and clusters."""
    emails = emails.copy()

    if "labels" in emails.columns:
        emails["is_unread"] = emails["labels"].fillna("").str.contains("UNREAD")
    else:
        emails["is_unread"] = False

    emails = add_priority_labels(emails)
    return cluster_emails(emails)


def suggest_label_name(cluster_emails: pd.DataFrame, cluster_name: str) -> str:
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


def get_cluster_message_ids(cluster_emails: pd.DataFrame) -> list[str]:
    """Return Gmail message IDs for a cluster."""
    message_ids = (
        cluster_emails["message_id"]
        if "message_id" in cluster_emails.columns
        else cluster_emails["id"]
    )
    return [str(message_id) for message_id in message_ids.dropna().tolist()]


def show_action_result(action_name: str, result: dict) -> None:
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


def show_gmail_oauth_help(error: Exception) -> None:
    """Explain common local OAuth access-denied setup problems."""
    error_text = str(error)
    st.error("Gmail Mode could not finish the Google sign-in.")

    if "access_denied" in error_text.lower() or "403" in error_text:
        st.warning(
            "Google blocked the OAuth request before Gmail Inbox Agent could access the inbox. "
            "This usually means the OAuth consent screen is still in Testing mode and your "
            "Google account is not listed as a test user, the Gmail API is not enabled, or the "
            "OAuth client is not a Desktop app client."
        )
        st.markdown(
            """
            **Fix in Google Cloud Console**

            1. Open your Google Cloud project.
            2. Enable the Gmail API.
            3. Open OAuth consent screen and add your Gmail address as a test user.
            4. Confirm the OAuth client type is Desktop app.
            5. Download the client JSON again, rename it to `credentials.json`, and place it next to `app.py`.
            6. Delete local `token.json` if it exists, then retry Gmail Mode.
            """
        )
    else:
        st.warning(error_text)

    st.info("Demo Mode still works without Gmail access, and no credentials or tokens are committed to Git.")


def render_cluster_actions(
    cluster_id: int,
    cluster_emails: pd.DataFrame,
    cluster_name: str,
    mode: str,
    service=None,
) -> None:
    """Render safe per-cluster action controls."""
    affected_count = len(cluster_emails)
    message_ids = get_cluster_message_ids(cluster_emails)
    default_label = suggest_label_name(cluster_emails, cluster_name)

    st.warning(
        "Archive only removes the INBOX label. This app does not delete emails. "
        "Actions apply only to messages in this selected cluster."
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
            if st.button("Archive this group", key=f"archive-demo-{cluster_id}", disabled=not confirm):
                st.success(f"Demo only: would archive {affected_count} emails.")
        with read_col:
            if st.button("Mark group as read", key=f"read-demo-{cluster_id}", disabled=not confirm):
                st.success(f"Demo only: would mark {affected_count} emails as read.")
        with label_col:
            if st.button("Apply label to group", key=f"label-demo-{cluster_id}", disabled=not confirm):
                st.success(f"Demo only: would apply `{label_name}` to {affected_count} emails.")
        return

    if not message_ids:
        st.error("No Gmail message IDs were found for this cluster.")
        return

    with archive_col:
        if st.button("Archive this group", key=f"archive-gmail-{cluster_id}", disabled=not confirm):
            show_action_result("Archive group", archive_messages(service, message_ids))

    with read_col:
        if st.button("Mark group as read", key=f"read-gmail-{cluster_id}", disabled=not confirm):
            show_action_result("Mark group as read", mark_messages_read(service, message_ids))

    with label_col:
        if st.button(
            "Apply label to group",
            key=f"label-gmail-{cluster_id}",
            disabled=not confirm or not label_name.strip(),
        ):
            result = apply_label_to_messages(service, message_ids, label_name.strip())
            show_action_result("Apply label to group", result)


def apply_filters(emails: pd.DataFrame) -> pd.DataFrame:
    """Apply sidebar search and filters to the processed email dataframe."""
    filtered = emails.copy()

    st.sidebar.header("Filters")
    search_text = st.sidebar.text_input("Search subject, sender, or body")

    priority_options = ["all", "high", "medium", "low"]
    priority_filter = st.sidebar.selectbox("Priority", priority_options)

    cluster_options = ["all"] + [
        f"{row.cluster_id}: {row.cluster_name}"
        for row in emails[["cluster_id", "cluster_name"]].drop_duplicates().itertuples()
    ]
    cluster_filter = st.sidebar.selectbox("Cluster", cluster_options)

    sender_options = ["all"] + sorted(emails["from_email"].fillna("").unique().tolist())
    sender_filter = st.sidebar.selectbox("Sender", sender_options)

    unread_only = False
    if "is_unread" in emails.columns and emails["is_unread"].any():
        unread_only = st.sidebar.checkbox("Unread only")

    if search_text:
        search_area = (
            filtered["subject"].fillna("")
            + " "
            + filtered["from_email"].fillna("")
            + " "
            + filtered["body"].fillna("")
            + " "
            + filtered["snippet"].fillna("")
        ).str.lower()
        filtered = filtered[search_area.str.contains(search_text.lower(), na=False)]

    if priority_filter != "all":
        filtered = filtered[filtered["priority"] == priority_filter]

    if cluster_filter != "all":
        selected_cluster_id = int(cluster_filter.split(":", 1)[0])
        filtered = filtered[filtered["cluster_id"] == selected_cluster_id]

    if sender_filter != "all":
        filtered = filtered[filtered["from_email"] == sender_filter]

    if unread_only:
        filtered = filtered[filtered["is_unread"]]

    return filtered


def render_metrics(all_emails: pd.DataFrame, filtered_emails: pd.DataFrame, cluster_summary: pd.DataFrame) -> None:
    """Render top-line inbox metrics."""
    high_count = int((all_emails["priority"] == "high").sum())
    unread_count = int(all_emails["is_unread"].sum()) if "is_unread" in all_emails.columns else 0
    metrics = [
        ("Total emails", len(all_emails)),
        ("Visible", len(filtered_emails)),
        ("Clusters", len(cluster_summary)),
        ("High priority", high_count),
        ("Unread", unread_count),
    ]

    for column, (label, value) in zip(st.columns(5), metrics):
        column.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_charts(emails: pd.DataFrame) -> None:
    """Render polished priority and cluster distribution charts."""
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Priority Distribution")
        priority_counts = (
            emails["priority"]
            .value_counts()
            .reindex(["high", "medium", "low"], fill_value=0)
            .reset_index()
        )
        priority_counts.columns = ["priority", "count"]
        fig = px.bar(
            priority_counts,
            x="priority",
            y="count",
            color="priority",
            color_discrete_map={
                "high": "#ef4444",
                "medium": "#f59e0b",
                "low": "#22c55e",
            },
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.subheader("Cluster Distribution")
        cluster_counts = emails["cluster_name"].value_counts().reset_index()
        cluster_counts.columns = ["cluster", "count"]
        fig = px.bar(
            cluster_counts,
            x="cluster",
            y="count",
            color="cluster",
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="",
        )
        st.plotly_chart(fig, use_container_width=True)


def format_table_value(column: str, value) -> str:
    """Format table values for the dark HTML table renderer."""
    if pd.isna(value):
        return ""

    text = escape(str(value))
    if column == "priority":
        priority_class = f"priority-{text.lower()}"
        return f'<span class="dark-pill {priority_class}">{text}</span>'

    return text


def render_dark_table(dataframe: pd.DataFrame, columns: list[str], max_rows: Optional[int] = None) -> None:
    """Render a readable dark table without Streamlit's white dataframe toolbar."""
    available_columns = [column for column in columns if column in dataframe.columns]
    if not available_columns:
        st.info("No table columns are available for this view.")
        return

    visible_rows = dataframe[available_columns].copy()
    if max_rows is not None:
        visible_rows = visible_rows.head(max_rows)

    headers = "".join(f"<th>{escape(column.replace('_', ' ').title())}</th>" for column in available_columns)
    body_rows = []

    for row in visible_rows.to_dict(orient="records"):
        cells = "".join(
            f"<td>{format_table_value(column, row.get(column, ''))}</td>"
            for column in available_columns
        )
        body_rows.append(f"<tr>{cells}</tr>")

    table_html = f"""
    <div class="dark-table-wrap">
        <table class="dark-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{''.join(body_rows)}</tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def render_exports(emails: pd.DataFrame, cluster_summary: pd.DataFrame) -> None:
    """Render CSV export buttons."""
    st.subheader("Exports")
    export_col1, export_col2, export_col3 = st.columns(3)

    with export_col1:
        st.download_button(
            "Export processed email table",
            data=emails.to_csv(index=False),
            file_name="processed_emails.csv",
            mime="text/csv",
        )

    with export_col2:
        st.download_button(
            "Export cluster summary",
            data=cluster_summary.to_csv(index=False),
            file_name="cluster_summary.csv",
            mime="text/csv",
        )

    with export_col3:
        high_priority_emails = emails[emails["priority"] == "high"]
        st.download_button(
            "Export high priority emails",
            data=high_priority_emails.to_csv(index=False),
            file_name="high_priority_emails.csv",
            mime="text/csv",
        )


def render_email_previews(cluster_emails: pd.DataFrame) -> None:
    """Render expandable previews for each email in a cluster."""
    preview_columns = [
        "priority",
        "priority_reason",
        "from_email",
        "subject",
        "date",
        "snippet",
    ]
    available_columns = [column for column in preview_columns if column in cluster_emails.columns]
    render_dark_table(cluster_emails, available_columns)

    for row in cluster_emails.itertuples():
        subject = getattr(row, "subject", "(no subject)") or "(no subject)"
        sender = getattr(row, "from_email", "(unknown sender)") or "(unknown sender)"
        date = getattr(row, "date", "")
        with st.expander(f"{subject} | {sender}", expanded=False):
            st.write(f"Date: {date or 'Not available'}")
            st.write(f"Priority: {getattr(row, 'priority', 'unknown')}")
            st.write(getattr(row, "priority_reason", "No priority reason available."))
            st.write(getattr(row, "body", "") or getattr(row, "snippet", ""))


def render_grouped_email_table(emails: pd.DataFrame, mode: str, service=None) -> None:
    """Show filtered emails grouped by cluster, with previews and action controls."""
    st.subheader("Email Table Grouped by Cluster")

    if emails.empty:
        st.info("No emails match the current filters.")
        return

    for cluster_id in sorted(emails["cluster_id"].unique()):
        cluster_emails = emails[emails["cluster_id"] == cluster_id]
        cluster_name = cluster_emails["cluster_name"].iloc[0]

        with st.expander(f"Cluster {cluster_id}: {cluster_name} ({len(cluster_emails)} emails)", expanded=True):
            with st.container(border=True):
                render_email_previews(cluster_emails)
                render_cluster_actions(cluster_id, cluster_emails, cluster_name, mode, service)


def render_dashboard(emails: pd.DataFrame, cluster_summary: pd.DataFrame, mode: str, service=None) -> None:
    """Render the full inbox dashboard."""
    if emails.empty:
        st.info("No inbox emails were found for this mode.")
        return

    filtered_emails = apply_filters(emails)
    render_metrics(emails, filtered_emails, cluster_summary)

    st.subheader("Cluster Summary")
    st.markdown('<div class="section-note">A quick map of the current inbox groups.</div>', unsafe_allow_html=True)
    render_dark_table(
        cluster_summary,
        ["cluster_id", "cluster_name", "email_count", "sample_subject", "high_priority_count"],
    )

    render_charts(filtered_emails if not filtered_emails.empty else emails)
    render_exports(filtered_emails, cluster_summary)

    st.subheader("Action Safety")
    st.warning(
        "Archive does not delete emails. Deleted emails are not supported in this app. "
        "Actions apply only to selected cluster messages."
    )

    render_grouped_email_table(filtered_emails, mode, service)


with st.sidebar:
    st.header("Mode")
    mode = st.radio("Choose an inbox source", ["Demo Mode", "Gmail Mode"])

    if mode == "Demo Mode":
        st.write("Safe for local use, GitHub, and Streamlit Cloud.")
    else:
        st.write(f"Fetches the last {MAX_EMAILS} Gmail inbox messages.")
        st.write(f"Requires local `{CREDENTIALS_FILE}` next to `app.py`.")

if mode == "Demo Mode":
    st.markdown(
        """
        <div class="app-hero">
            <div class="hero-kicker">Private demo workspace</div>
            <h1>Demo inbox dashboard</h1>
            <p>Turn inbox chaos into organized action groups. Demo Mode uses mock data, while Gmail Mode uses local OAuth only when you choose it. Credentials and tokens stay local and are ignored by Git.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("Demo Mode is active. No Gmail credentials are needed.")
    emails, cluster_summary = prepare_dashboard_data(load_mock_email_data())
    render_dashboard(emails, cluster_summary, mode)
else:
    st.markdown(
        """
        <div class="app-hero">
            <div class="hero-kicker">Local Gmail OAuth</div>
            <h1>Gmail inbox dashboard</h1>
            <p>Turn inbox chaos into organized action groups. Fetch your latest inbox emails, cluster them, prioritize what matters, and take safe grouped actions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not credentials_file_exists():
        st.warning(
            f"Gmail Mode needs `{CREDENTIALS_FILE}` in the project root. "
            "Download your Google OAuth client JSON, rename it to credentials.json, "
            "and place it next to app.py."
        )
        st.info(
            f"`{CREDENTIALS_FILE}` and `{TOKEN_FILE}` are private local files ignored by Git. "
            "Demo Mode still works locally and on Streamlit Cloud."
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
            show_gmail_oauth_help(error)
        except Exception as error:
            show_gmail_oauth_help(error)
