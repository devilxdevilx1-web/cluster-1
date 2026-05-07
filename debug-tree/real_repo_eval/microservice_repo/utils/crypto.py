def check_hash(p):
    # Bug: missing attribute on dynamic object
    return p.digest()