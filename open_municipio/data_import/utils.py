"""
A misc set of utilities useful in the data-import domain.
"""


import socket

def netcat(hostname, port, content):
    """
    netcat (nc) implementation in python
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    s.sendall(content)
    s.shutdown(socket.SHUT_WR)
    res = ''
    while 1:
        data = s.recv(1024)
        if data == "":
            break
        res += data
    s.close()
    return res

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


def create_table_schema(table_name, table_schema):
    """
    Generate the SQL statement to execute in order to create a DB table.
    
    Takes the following parameters:
    
    * ``table_name``: a string to be used as the table name
    * ``table_schema``: a dict mapping column names to column types (as strings)
    
    Note that supported column types may vary depending on the RDBMS of choice. 
    """
    sql = "CREATE TABLE %s \n" % table_name
    sql += "(\n"
    for (col_name, col_type) in table_schema.items():
        sql += "  %(col_name)s\t%(col_type)s,\n" % {'col_name': col_name, 'col_type': col_type}
    # remove last comma (otherwise RBDMS may complain)
    sql = sql[:-2] + '\n'
    sql += ");\n"
    return  sql     