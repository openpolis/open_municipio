"""
A misc set of utilities useful in the data-import domain.
"""

def get_row_dicts(cursor, query, params=()):
    """
    Convert a sequence of row (record) tuples -- as returned by a call to Python DBAPI's ``cursor.connect()``
    method -- to a list of row dicts keyed by column names.
    
    Take the following arguments:
    
    * ``cursor``: a DBAPI cursor object
    * ``query``: a SQL statement string (possibily including parameter markers)
    * ``params``: a sequence of parameters for the SQL query string to be interpolated with  
    """
    cursor.execute(query, params)
    colnames = [desc[0] for desc in cursor.description]
    row_dicts = [dict(zip(colnames, row)) for row in cursor.fetchall()]
    return row_dicts