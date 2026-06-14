import streamlit as st

from src.clustering import cluster_emails
from src.dashboard import (
    render_cluster_cards,
    render_email_count,
    render_priority_counts,
    render_sample_emails_per_cluster,
)
from src.email_parser import load_mock_email_data
from src.priority import add_priority_labels


st.set_page_config(page_title="Gmail Inbox Agent", layout="wide")

st.title("Gmail Inbox Agent")
st.caption(
    "A starter Streamlit app for reviewing, grouping, prioritizing, and eventually archiving Gmail inbox messages."
)

with st.sidebar:
    st.header("Demo Mode")
    st.write("Using fake inbox data. Gmail connection will be added in a later iteration.")

emails = load_mock_email_data()
emails = add_priority_labels(emails)
emails, cluster_summary = cluster_emails(emails)

st.info("Gmail connection will be added in a later iteration. No credentials are needed yet.")

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
for cluster_id in sorted(emails["cluster_id"].unique()):
    cluster_emails = emails[emails["cluster_id"] == cluster_id]
    cluster_name = cluster_emails["cluster_name"].iloc[0]

    with st.expander(f"Cluster {cluster_id}: {cluster_name}", expanded=True):
        st.dataframe(
            cluster_emails[["priority", "from_email", "subject", "date", "snippet"]],
            use_container_width=True,
            hide_index=True,
        )

        if st.button("Archive this group", key=f"archive-{cluster_id}"):
            st.success(
                f"Demo only: Cluster {cluster_id} would be archived after Gmail is connected."
            )

st.subheader("Sample Emails per Cluster")
render_sample_emails_per_cluster(emails)
