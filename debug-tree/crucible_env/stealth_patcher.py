import database_v2
setattr(database_v2, 'connect', lambda: 1/0)