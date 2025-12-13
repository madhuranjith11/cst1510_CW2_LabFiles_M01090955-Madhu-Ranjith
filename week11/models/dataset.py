"""Dataset entity class."""

class Dataset:
    """Represents a data science dataset in the platform."""

    def __init__(self, dataset_id: int, dataset_name: str, category: str,
                 source: str, upload_date: str, record_count: int, file_size_mb: float):
        self.__id = dataset_id
        self.__name = dataset_name
        self.__category = category
        self.__source = source
        self.__upload_date = upload_date
        self.__record_count = record_count
        self.__file_size_mb = file_size_mb

    def get_id(self) -> int:
        """Get dataset ID."""
        return self.__id

    def get_name(self) -> str:
        """Get dataset name."""
        return self.__name

    def get_category(self) -> str:
        """Get category."""
        return self.__category

    def get_source(self) -> str:
        """Get data source."""
        return self.__source

    def get_upload_date(self) -> str:
        """Get upload date."""
        return self.__upload_date

    def get_record_count(self) -> int:
        """Get number of records."""
        return self.__record_count

    def get_file_size_mb(self) -> float:
        """Get file size in MB."""
        return self.__file_size_mb

    def calculate_size_gb(self) -> float:
        """Calculate size in gigabytes."""
        return self.__file_size_mb / 1024

    def to_dict(self) -> dict:
        """Convert to dictionary for display."""
        return {
            "ID": self.__id,
            "Name": self.__name,
            "Category": self.__category,
            "Source": self.__source,
            "Upload Date": self.__upload_date,
            "Records": self.__record_count,
            "Size (MB)": self.__file_size_mb
        }

    def __str__(self) -> str:
        return f"Dataset {self.__id}: {self.__name} ({self.__file_size_mb:.2f} MB, {self.__record_count} records)"

    def __repr__(self) -> str:
        return self.__str__()
