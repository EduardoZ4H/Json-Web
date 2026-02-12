import bcrypt

def authenticate(username, password, users_dict):
    if username in users_dict:
        stored_hash = users_dict[username].encode()
        return bcrypt.checkpw(password.encode(), stored_hash)
    return False
