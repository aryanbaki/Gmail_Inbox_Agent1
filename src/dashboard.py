import pandas as pd
import streamlit as st


def render_email_count(emails: pd.DataFrame) -> None:
    """Show the total number of demo emails."""
    st.metric("Total emails", len(emails))


def render_priority_counts(emails: pd.DataFrame) -> None:
    """Show high, medium, and low priority counts."""
    priority_counts = emails["priority"].value_counts()
    high_col, medium_col, low_col = st.columns(3)

    high_col.metric("High priority", int(priority_counts.get("high", 0)))
    medium_col.metric("Medium priority", int(priority_counts.get("medium", 0)))
    low_col.metric("Low priority", int(priority_counts.get("low", 0)))


def render_cluster_cards(cluster_summary: pd.DataFrame) -> None:
    """Show a compact card for each email cluster."""
    for _, cluster in cluster_summary.iterrows():
        with st.container(border=True):
            st.subheader(f"Cluster {cluster['cluster_id']}: {cluster['cluster_name']}")
            st.write(f"Emails: {cluster['email_count']}")
            st.write(f"High priority emails: {cluster['high_priority_count']}")
            st.caption(f"Example: {cluster['sample_subject']}")


def render_sample_emails_per_cluster(emails: pd.DataFrame) -> None:
    """Show sample emails grouped by cluster."""
    for cluster_id in sorted(emails["cluster_id"].unique()):
        cluster_emails = emails[emails["cluster_id"] == cluster_id]
        cluster_name = cluster_emails["cluster_name"].iloc[0]

        with st.expander(f"Cluster {cluster_id}: {cluster_name}", expanded=True):
            st.dataframe(
                cluster_emails[
                    ["priority", "from_email", "subject", "date", "snippet"]
                ],
                use_container_width=True,
                hide_index=True,
            )


def render_email_table(emails: pd.DataFrame) -> None:
    """Render the main inbox review table in Streamlit."""
    st.dataframe(emails, use_container_width=True)


def render_status_message() -> None:
    """Show the current scaffold status to the user."""
    st.info("Demo mode is active. Gmail connection will be added later.")
