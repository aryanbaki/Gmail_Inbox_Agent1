from googleapiclient.errors import HttpError


class GmailClientError(RuntimeError):
    """Raised when Gmail messages cannot be fetched."""


def fetch_inbox_messages(service, max_results: int = 200) -> list[dict]:
    """Fetch recent raw Gmail message objects from the inbox."""
    try:
        response = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=max_results)
            .execute()
        )
        message_refs = response.get("messages", [])

        if not message_refs:
            return []

        messages = []
        for message_ref in message_refs:
            message = (
                service.users()
                .messages()
                .get(userId="me", id=message_ref["id"], format="full")
                .execute()
            )
            messages.append(message)

        return messages
    except HttpError as error:
        raise GmailClientError(f"Gmail API error while fetching inbox: {error}") from error
    except Exception as error:
        raise GmailClientError(f"Could not fetch Gmail inbox messages: {error}") from error
