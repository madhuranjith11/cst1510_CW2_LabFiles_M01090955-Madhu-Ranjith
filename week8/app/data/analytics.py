import pandas as pd
from db import connect_database

def fetch_type_stats(connection):
    q = """
        SELECT incident_type, COUNT(*) AS total
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, connection)

def fetch_high_severity_status(connection):
    q = """
        SELECT status, COUNT(*) AS total
        FROM cyber_incidents
        WHERE severity = 'High'
        GROUP BY status
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, connection)

def filter_incident_types(connection, threshold=5):
    q = """
        SELECT incident_type, COUNT(*) AS total
        FROM cyber_incidents
        GROUP BY incident_type
        HAVING COUNT(*) > ?
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, connection, params=(threshold,))
import pandas as pd
from db import connect_database

def fetch_type_stats(connection):
    q = """
        SELECT incident_type, COUNT(*) AS total
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, connection)

def fetch_high_severity_status(connection):
    q = """
        SELECT status, COUNT(*) AS total
        FROM cyber_incidents
        WHERE severity = 'High'
        GROUP BY status
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, connection)

def filter_incident_types(connection, threshold=5):
    q = """
        SELECT incident_type, COUNT(*) AS total
        FROM cyber_incidents
        GROUP BY incident_type
        HAVING COUNT(*) > ?
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, connection, params=(threshold,))
import pandas as pd
from db import connect_database

def fetch_type_stats(connection):
    q = """
        SELECT incident_type, COUNT(*) AS total
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, connection)

def fetch_high_severity_status(connection):
    q = """
        SELECT status, COUNT(*) AS total
        FROM cyber_incidents
        WHERE severity = 'High'
        GROUP BY status
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, connection)

def filter_incident_types(connection, threshold=5):
    q = """
        SELECT incident_type, COUNT(*) AS total
        FROM cyber_incidents
        GROUP BY incident_type
        HAVING COUNT(*) > ?
        ORDER BY total DESC
    """
    return pd.read_sql_query(q, connection, params=(threshold,))
