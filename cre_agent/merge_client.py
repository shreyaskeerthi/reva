"""
Merge CRM client for creating contacts, notes, and tasks
"""
import logging
import requests
from typing import Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MergeClient:
    """Client for Merge CRM API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        account_token: Optional[str] = None,
        base_url: str = "https://api.merge.dev/api/crm/v1",
        demo_mode: bool = False
    ):
        self.api_key = api_key
        self.account_token = account_token
        self.base_url = base_url.rstrip("/")
        self.demo_mode = demo_mode

        self.headers = {}
        if api_key and account_token and not demo_mode:
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "X-Account-Token": account_token,
                "Content-Type": "application/json"
            }
            logger.info("Merge CRM client initialized")
        else:
            logger.info("Merge CRM client in demo mode")
            self.demo_mode = True

    def upsert_contact(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        company: Optional[str] = None
    ) -> str:
        """
        Create or update a contact in CRM

        Args:
            email: Contact email
            name: Contact name
            company: Company name

        Returns:
            Contact ID (real or demo)
        """
        if self.demo_mode:
            logger.info(f"Demo mode: Would create contact {name} ({email}) at {company}")
            return f"contact_demo_{hash(email or name or 'unknown') % 100000}"

        try:
            # First, search for existing contact by email
            if email:
                search_url = f"{self.base_url}/contacts"
                search_params = {"email": email}
                search_response = requests.get(
                    search_url,
                    headers=self.headers,
                    params=search_params,
                    timeout=10
                )

                if search_response.status_code == 200:
                    results = search_response.json().get("results", [])
                    if results:
                        contact_id = results[0]["id"]
                        logger.info(f"Found existing contact: {contact_id}")
                        return contact_id

            # Create new contact
            create_url = f"{self.base_url}/contacts"
            payload = {
                "model": {
                    "first_name": name.split()[0] if name and " " in name else name,
                    "last_name": name.split()[-1] if name and " " in name else "",
                    "email_addresses": [{"email_address": email}] if email else [],
                    "account": {"name": company} if company else None
                }
            }

            create_response = requests.post(
                create_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if create_response.status_code in [200, 201]:
                contact_id = create_response.json()["model"]["id"]
                logger.info(f"Created new contact: {contact_id}")
                return contact_id
            else:
                logger.error(f"Failed to create contact: {create_response.status_code}")
                return f"contact_error_{datetime.now().timestamp()}"

        except Exception as e:
            logger.error(f"Merge contact creation failed: {e}")
            return f"contact_error_{datetime.now().timestamp()}"

    def create_note(self, contact_id: str, content: str) -> str:
        """
        Create a note associated with a contact

        Args:
            contact_id: Contact ID to associate note with
            content: Note content

        Returns:
            Note ID (real or demo)
        """
        if self.demo_mode:
            logger.info(f"Demo mode: Would create note for contact {contact_id}")
            return f"note_demo_{hash(contact_id) % 100000}"

        try:
            create_url = f"{self.base_url}/notes"
            payload = {
                "model": {
                    "content": content,
                    "contact": contact_id
                }
            }

            response = requests.post(
                create_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code in [200, 201]:
                note_id = response.json()["model"]["id"]
                logger.info(f"Created note: {note_id}")
                return note_id
            else:
                logger.error(f"Failed to create note: {response.status_code}")
                return f"note_error_{datetime.now().timestamp()}"

        except Exception as e:
            logger.error(f"Merge note creation failed: {e}")
            return f"note_error_{datetime.now().timestamp()}"

    def create_task(
        self,
        contact_id: str,
        title: str,
        due_date: Optional[str] = None
    ) -> str:
        """
        Create a task/follow-up associated with a contact

        Args:
            contact_id: Contact ID to associate task with
            title: Task title
            due_date: Due date in ISO format (optional)

        Returns:
            Task ID (real or demo)
        """
        if self.demo_mode:
            logger.info(f"Demo mode: Would create task '{title}' for contact {contact_id}")
            return f"task_demo_{hash(contact_id + title) % 100000}"

        try:
            # Default due date: 3 days from now
            if not due_date:
                due_date = (datetime.now() + timedelta(days=3)).isoformat()

            create_url = f"{self.base_url}/tasks"
            payload = {
                "model": {
                    "subject": title,
                    "contact": contact_id,
                    "due_date": due_date,
                    "status": "OPEN"
                }
            }

            response = requests.post(
                create_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code in [200, 201]:
                task_id = response.json()["model"]["id"]
                logger.info(f"Created task: {task_id}")
                return task_id
            else:
                logger.error(f"Failed to create task: {response.status_code}")
                return f"task_error_{datetime.now().timestamp()}"

        except Exception as e:
            logger.error(f"Merge task creation failed: {e}")
            return f"task_error_{datetime.now().timestamp()}"
