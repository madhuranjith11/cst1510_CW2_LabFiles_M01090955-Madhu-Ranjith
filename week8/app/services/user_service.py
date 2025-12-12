import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user
from app.data.schema import create_users_table


def register_user(username, password, role='user'):
    """
    Register a new user with password hashing.
    
    Args:
        username: User's login name
        password: Plain text password (will be hashed)
        role: User role (default: 'user')
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Check if user already exists
    existing_user = get_user_by_username(username)
    if existing_user:
        return False, f"Username '{username}' already exists."
    
    # Hash the password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')
    
    # Insert new user
    try:
        insert_user(username, password_hash, role)
        return True, f"User '{username}' registered successfully!"
    except Exception as e:
        return False, f"Error registering user: {e}"


def login_user(username, password):
    """
    Authenticate a user.
    
    Args:
        username: User's login name
        password: Plain text password to verify
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Find user
    user = get_user_by_username(username)
    
    if not user:
        return False, "Username not found."
    
    # Verify password (user[2] is password_hash column)
    stored_hash = user[2]
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')
    
    if bcrypt.checkpw(password_bytes, hash_bytes):
        return True, f"Welcome, {username}!"
    else:
        return False, "Invalid password."


def migrate_users_from_file(filepath='DATA/users.txt'):
    """
    Migrate users from text file to database.
    
    Args:
        filepath: Path to users.txt file
        
    Returns:
        int: Number of users migrated
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        return 0
    
    conn = connect_database()
    cursor = conn.cursor()
    migrated_count = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse line: username,password_hash,role (or username,password_hash)
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0].strip()
                password_hash = parts[1].strip()
                role = parts[2].strip() if len(parts) > 2 else 'user'
                
                # Insert user (ignore if already exists)
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, role)
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except Exception as e:
                    print(f"Error migrating user {username}: {e}")
    
    conn.commit()
    conn.close()
    print(f"✅ Migrated {migrated_count} users from {filepath.name}")
    return migrated_count


def get_user_info(username):
    """
    Get user information (without password hash).
    
    Args:
        username: Username to lookup
        
    Returns:
        dict: User information or None
    """
    user = get_user_by_username(username)
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'role': user[3],
            'created_at': user[4] if len(user) > 4 else None
        }
    return None


def change_password(username, old_password, new_password):
    """
    Change user's password.
    
    Args:
        username: User's login name
        old_password: Current password for verification
        new_password: New password to set
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # First verify old password
    success, msg = login_user(username, old_password)
    if not success:
        return False, "Current password is incorrect."
    
    # Hash new password
    password_bytes = new_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    new_hash = hashed.decode('utf-8')
    
    # Update password in database
    conn = connect_database()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (new_hash, username)
        )
        conn.commit()
        conn.close()
        return True, "Password changed successfully!"
    except Exception as e:
        conn.close()
        return False,  f"Error changing password: {e}"
