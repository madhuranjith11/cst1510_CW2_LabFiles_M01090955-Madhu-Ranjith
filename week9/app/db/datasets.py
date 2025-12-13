import pandas as pd
from app.db.db import connect_database



def insert_dataset(dataset_name, category, source, last_updated, record_count, file_size_mb):
    """
    Insert new dataset metadata.

    Args:
        dataset_name: Name of the dataset
        category: Dataset category
        source: Data source
        last_updated: Last update date
        record_count: Number of records
        file_size_mb: File size in MB

    Returns:
        int: ID of inserted dataset
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO datasets_metadata
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))

    conn.commit()
    dataset_id = cursor.lastrowid
    conn.close()

    return dataset_id


def get_all_datasets():
    """
    Get all datasets as DataFrame.

    Returns:
        pandas.DataFrame: All datasets
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


def get_dataset_by_id(dataset_id):
    """
    Get single dataset by ID.

    Args:
        dataset_id: ID of dataset to retrieve

    Returns:
        pandas.DataFrame: Single dataset or empty DataFrame
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata WHERE id = ?",
        conn,
        params=(dataset_id,)
    )
    conn.close()
    return df


def update_dataset(dataset_id, **kwargs):
    """
    Update dataset metadata.

    Args:
        dataset_id: ID of dataset to update
        **kwargs: Fields to update (e.g., last_updated='2024-12-12')

    Returns:
        int: Number of rows updated
    """
    if not kwargs:
        return 0

    conn = connect_database()
    cursor = conn.cursor()

    # Build UPDATE query dynamically
    set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
    values = list(kwargs.values()) + [dataset_id]

    cursor.execute(
        f"UPDATE datasets_metadata SET {set_clause} WHERE id = ?",
        values
    )
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()

    return rows_updated


def delete_dataset(dataset_id):
    """
    Delete dataset from database.

    Args:
        dataset_id: ID of dataset to delete

    Returns:
        int: Number of rows deleted
    """
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM datasets_metadata WHERE id = ?",
        (dataset_id,)
    )
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()

    return rows_deleted


def load_datasets_from_csv(csv_path):
    """
    Load datasets from CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        int: Number of rows loaded
    """
    from pathlib import Path

    if not Path(csv_path).exists():
        print(f"⚠️  File not found: {csv_path}")
        return 0

    conn = connect_database()
    df = pd.read_csv(csv_path)

    rows_loaded = df.to_sql(
        'datasets_metadata',
        conn,
        if_exists='append',
        index=False
    )

    conn.close()
    print(f"✅ Loaded {len(df)} datasets from {Path(csv_path).name}")
    return len(df)


def get_datasets_by_category(category):
    """
    Get datasets filtered by category.

    Args:
        category: Category to filter by

    Returns:
        pandas.DataFrame: Filtered datasets
    """
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM datasets_metadata WHERE category = ? ORDER BY last_updated DESC",
        conn,
        params=(category,)
    )
    conn.close()
    return df
