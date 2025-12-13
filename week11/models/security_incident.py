"""SecurityIncident entity class."""

class SecurityIncident:
    """Represents a cybersecurity incident in the platform."""

    def __init__(self, incident_id: int, incident_date: str, incident_type: str,
                 severity: str, status: str, description: str, reported_by: str = "System"):
        self.__id = incident_id
        self.__date = incident_date
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by

    def get_id(self) -> int:
        """Get incident ID."""
        return self.__id

    def get_date(self) -> str:
        """Get incident date."""
        return self.__date

    def get_incident_type(self) -> str:
        """Get incident type."""
        return self.__incident_type

    def get_severity(self) -> str:
        """Get severity level."""
        return self.__severity

    def get_status(self) -> str:
        """Get current status."""
        return self.__status

    def get_description(self) -> str:
        """Get incident description."""
        return self.__description

    def get_reported_by(self) -> str:
        """Get reporter name."""
        return self.__reported_by

    def update_status(self, new_status: str) -> None:
        """Update the incident status."""
        self.__status = new_status

    def get_severity_level(self) -> int:
        """Return an integer severity level for sorting/comparison."""
        mapping = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return mapping.get(self.__severity.lower(), 0)

    def to_dict(self) -> dict:
        """Convert to dictionary for display."""
        return {
            "ID": self.__id,
            "Date": self.__date,
            "Type": self.__incident_type,
            "Severity": self.__severity,
            "Status": self.__status,
            "Description": self.__description,
            "Reported By": self.__reported_by
        }

    def __str__(self) -> str:
        return f"Incident {self.__id} [{self.__severity.upper()}] {self.__incident_type} - {self.__status}"

    def __repr__(self) -> str:
        return self.__str__()
