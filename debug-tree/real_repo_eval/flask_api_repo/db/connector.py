import os
def get_user(uid):
    # Bug: hardcoded dev host instead of env
    host = 'http://localhost:5432'
    raise ConnectionError(f'Failed to connect to {host}')