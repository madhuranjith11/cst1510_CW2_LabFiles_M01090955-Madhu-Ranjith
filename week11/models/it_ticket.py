"""ITTicket entity class."""

class ITTicket:
    """Represents an IT support ticket."""

    def __init__(self, ticket_id: int, ticket_ref: str, priority: str, status: str,
                 category: str, subject: str, description: str, created_date: str,
                 assigned_to: str = "Unassigned"):
        self.__id = ticket_id
        self.__ticket_ref = ticket_ref
        self.__priority = priority
        self.__status = status
        self.__category = category
        self.__subject = subject
        self.__description = description
        self.__created_date = created_date
        self.__assigned_to = assigned_to

    def get_id(self) -> int:
        """Get ticket database ID."""
        return self.__id

    def get_ticket_ref(self) -> str:
        """Get ticket reference number."""
        return self.__ticket_ref

    def get_priority(self) -> str:
        """Get priority level."""
        return self.__priority

    def get_status(self) -> str:
        """Get current status."""
        return self.__status

    def get_category(self) -> str:
        """Get ticket category."""
        return self.__category

    def get_subject(self) -> str:
        """Get subject/title."""
        return self.__subject

    def get_description(self) -> str:
        """Get description."""
        return self.__description

    def get_created_date(self) -> str:
        """Get creation date."""
        return self.__created_date

    def get_assigned_to(self) -> str:
        """Get assigned staff member."""
        return self.__assigned_to

    def assign_to(self, staff: str) -> None:
        """Assign ticket to staff member."""
        self.__assigned_to = staff

    def close_ticket(self) -> None:
        """Close the ticket."""
        self.__status = "Resolved"

    def update_status(self, new_status: str) -> None:
        """Update ticket status."""
        self.__status = new_status

    def to_dict(self) -> dict:
        """Convert to dictionary for display."""
        return {
            "ID": self.__id,
            "Ticket Ref": self.__ticket_ref,
            "Priority": self.__priority,
            "Status": self.__status,
            "Category": self.__category,
            "Subject": self.__subject,
            "Description": self.__description,
            "Created": self.__created_date,
            "Assigned To": self.__assigned_to
        }

    def __str__(self) -> str:
        return (
            f"Ticket {self.__ticket_ref}: {self.__subject} "
            f"[{self.__priority}] – {self.__status} (assigned to: {self.__assigned_to})"
        )

    def __repr__(self) -> str:
        return self.__str__()
