from app.data.db import connect_database


def get_user_by_username(username):
    """
    Retrieve user by username.
    
    Args:
        username: Username to search for
        
    Returns:
        tuple: User record or None if not found
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    return user


def insert_user(username, password_hash, role='user'):
    """
    Insert new user into database.
    
    Args:
        username: User's login name
        password_hash: Hashed password
        role: User role (default: 'user')
        
    Returns:
        int: ID of inserted user
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    return user_id


def get_all_users():
    """
    Get all users from database.
    
    Returns:
        list: All user records
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, role, created_at FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return users


def update_user_role(username, new_role):
    """
    Update user's role.
    
    Args:
        username: Username to update
        new_role: New role value
        
    Returns:
        int: Number of rows updated
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE users SET role = ? WHERE username = ?",
        (new_role, username)
    )
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    
    return rows_updated


def delete_user(username):
    """
    Delete user from database.
    
    Args:
        username: Username to delete
        
    Returns:
        int: Number of rows deleted
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM users WHERE username = ?",
        (username,)
    )
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    
    return rows_deleted
