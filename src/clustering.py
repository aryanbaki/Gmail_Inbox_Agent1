import os

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer


WEAK_CLUSTER_TERMS = {"email", "message", "gmail", "inbox", "new"}


def _fallback_cluster_name(cluster_id: int) -> str:
    """Return a readable fallback name when top terms are not useful."""
    return f"Cluster {cluster_id}"


def _name_clusters(vectorizer: TfidfVectorizer, model: KMeans) -> dict[int, str]:
    """Use each cluster center's strongest words as a simple readable name."""
    words = vectorizer.get_feature_names_out()
    cluster_names = {}

    for cluster_id, center in enumerate(model.cluster_centers_):
        top_word_indexes = center.argsort()[-5:][::-1]
        top_words = [
            words[index].title()
            for index in top_word_indexes
            if words[index].lower() not in WEAK_CLUSTER_TERMS and center[index] > 0
        ]
        cluster_names[cluster_id] = ", ".join(top_words[:3]) or _fallback_cluster_name(cluster_id)

    return cluster_names


def cluster_emails(
    emails: pd.DataFrame,
    n_clusters: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cluster emails with TF-IDF and KMeans."""
    clustered_emails = emails.copy()

    if clustered_emails.empty:
        clustered_emails["cluster_id"] = []
        clustered_emails["cluster_name"] = []
        clustered_emails["vector_x"] = []
        clustered_emails["vector_y"] = []
        return clustered_emails, pd.DataFrame(
            columns=[
                "cluster_id",
                "cluster_name",
                "email_count",
                "sample_subject",
                "high_priority_count",
            ]
        )

    cluster_count = min(n_clusters, len(clustered_emails))
    clustered_emails["clean_text"] = clustered_emails["clean_text"].fillna("")

    if not clustered_emails["clean_text"].str.strip().any():
        clustered_emails["cluster_id"] = 0
        clustered_emails["cluster_name"] = "Uncategorized"
        clustered_emails["vector_x"] = 0.0
        clustered_emails["vector_y"] = 0.0
        cluster_summary = pd.DataFrame(
            [
                {
                    "cluster_id": 0,
                    "cluster_name": "Uncategorized",
                    "email_count": len(clustered_emails),
                    "sample_subject": clustered_emails["subject"].iloc[0],
                    "high_priority_count": (clustered_emails["priority"] == "high").sum(),
                }
            ]
        )
        return clustered_emails, cluster_summary

    vectorizer = TfidfVectorizer(stop_words="english", max_features=100)
    try:
        text_vectors = vectorizer.fit_transform(clustered_emails["clean_text"].tolist())
    except ValueError:
        clustered_emails["cluster_id"] = 0
        clustered_emails["cluster_name"] = "Uncategorized"
        clustered_emails["vector_x"] = 0.0
        clustered_emails["vector_y"] = 0.0
        cluster_summary = pd.DataFrame(
            [
                {
                    "cluster_id": 0,
                    "cluster_name": "Uncategorized",
                    "email_count": len(clustered_emails),
                    "sample_subject": clustered_emails["subject"].iloc[0],
                    "high_priority_count": (clustered_emails["priority"] == "high").sum(),
                }
            ]
        )
        return clustered_emails, cluster_summary

    model = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
    clustered_emails["cluster_id"] = model.fit_predict(text_vectors)

    cluster_names = _name_clusters(vectorizer, model)
    clustered_emails["cluster_name"] = clustered_emails["cluster_id"].map(cluster_names)
    if text_vectors.shape[1] >= 2 and len(clustered_emails) >= 2:
        reducer = PCA(n_components=2)
        coordinates = reducer.fit_transform(text_vectors.toarray())
        clustered_emails["vector_x"] = coordinates[:, 0]
        clustered_emails["vector_y"] = coordinates[:, 1]
    else:
        clustered_emails["vector_x"] = 0.0
        clustered_emails["vector_y"] = 0.0

    cluster_summary = (
        clustered_emails.groupby(["cluster_id", "cluster_name"])
        .agg(
            email_count=("id", "count"),
            sample_subject=("subject", "first"),
            high_priority_count=("priority", lambda values: (values == "high").sum()),
        )
        .reset_index()
        .sort_values(["high_priority_count", "email_count"], ascending=False)
    )

    return clustered_emails, cluster_summary
