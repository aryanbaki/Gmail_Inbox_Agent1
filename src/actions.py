from typing import Optional

from googleapiclient.errors import HttpError


def _empty_result() -> dict:
    """Create a standard action result."""
    return {
        "success_count": 0,
        "failure_count": 0,
        "errors": [],
    }


def _modify_messages(
    service,
    message_ids: list[str],
    add_label_ids: Optional[list[str]] = None,
    remove_label_ids: Optional[list[str]] = None,
) -> dict:
    """Safely apply a Gmail modify request to each selected message."""
    result = _empty_result()
    add_label_ids = add_label_ids or []
    remove_label_ids = remove_label_ids or []

    for message_id in message_ids:
        try:
            (
                service.users()
                .messages()
                .modify(
                    userId="me",
                    id=message_id,
                    body={
                        "addLabelIds": add_label_ids,
                        "removeLabelIds": remove_label_ids,
                    },
                )
                .execute()
            )
            result["success_count"] += 1
        except HttpError as error:
            result["failure_count"] += 1
            result["errors"].append(f"{message_id}: {error}")
        except Exception as error:
            result["failure_count"] += 1
            result["errors"].append(f"{message_id}: {error}")

    return result


def archive_messages(service, message_ids: list[str]) -> dict:
    """Archive messages by removing the INBOX label. This does not delete emails."""
    return _modify_messages(service, message_ids, remove_label_ids=["INBOX"])


def mark_messages_read(service, message_ids: list[str]) -> dict:
    """Mark messages as read by removing the UNREAD label."""
    return _modify_messages(service, message_ids, remove_label_ids=["UNREAD"])


def create_label_if_missing(service, label_name: str) -> dict:
    """Return an existing Gmail label or create it if it does not exist."""
    try:
        response = service.users().labels().list(userId="me").execute()
        labels = response.get("labels", [])

        for label in labels:
            if label.get("name", "").lower() == label_name.lower():
                return {
                    "label_id": label["id"],
                    "label_name": label["name"],
                    "created": False,
                    "error": "",
                }

        label = (
            service.users()
            .labels()
            .create(
                userId="me",
                body={
                    "name": label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            )
            .execute()
        )
        return {
            "label_id": label["id"],
            "label_name": label["name"],
            "created": True,
            "error": "",
        }
    except HttpError as error:
        return {
            "label_id": "",
            "label_name": label_name,
            "created": False,
            "error": f"Gmail API error while creating label: {error}",
        }
    except Exception as error:
        return {
            "label_id": "",
            "label_name": label_name,
            "created": False,
            "error": f"Could not create Gmail label: {error}",
        }


def apply_label_to_messages(service, message_ids: list[str], label_name: str) -> dict:
    """Create a label if needed, then apply it to selected messages."""
    label_result = create_label_if_missing(service, label_name)

    if label_result["error"]:
        result = _empty_result()
        result["failure_count"] = len(message_ids)
        result["errors"].append(label_result["error"])
        return result

    result = _modify_messages(service, message_ids, add_label_ids=[label_result["label_id"]])
    result["label_name"] = label_result["label_name"]
    result["label_created"] = label_result["created"]
    return result
