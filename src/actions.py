def archive_email_group(group_id: int) -> dict:
    """Later, this will archive all Gmail messages in a reviewed group."""
    return {
        "group_id": group_id,
        "status": "not_connected",
        "message": "Archive actions are disabled until Gmail integration is added.",
    }


def mark_group_reviewed(group_id: int) -> dict:
    """Later, this will record that a group has been reviewed by the user."""
    return {
        "group_id": group_id,
        "status": "reviewed_placeholder",
    }
