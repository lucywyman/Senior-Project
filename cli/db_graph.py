"""Database Graph

This module creates a graph of a database using foreign key constraints as
edges and tables as nodes.

Notes
---------------------------------------
This approach is functional, but it would likely be better from several
perspectives to rewrite as a class. Among other benefits, the config parsing
and db connection could be removed and a db connection could simply be
passed to the class upon instantiation.

"""
import psycopg2
import psycopg2.extras
import configparser

# Connect to database
config = configparser.ConfigParser()
config.read('general.cfg')

db_conn = (
    "dbname={dbname} "
    "user={user} "
    "password={password}"
    .format(
        dbname   = config['Database']['dbname'],
        user     = config['Database']['user'],
        password = config['Database']['password']
        )
    )

conn = psycopg2.connect(
    db_conn,
    cursor_factory = psycopg2.extras.RealDictCursor
    )
conn.autocommit = True

cur = conn.cursor()


# Get a list of tables in database
edges = []
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
tables = cur.fetchall()

# build list of edges using contraints
for table in tables:
    query = """SELECT tc.constraint_name, tc.table_name, kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
        WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name = %(tablename)s"""
    cur.execute(query, table)
    for row in cur.fetchall():
        constraint, table, column, foreign_table, foreign_column = row
        edges.append([row['table_name'], row['foreign_table_name'], row['column_name'], row['foreign_column_name']])

cur.close()
conn.close()

# build a dictionary of nodes with list of edges touching node
# example:
# { "table": [[table2, key_name, foreign_key_name]] }
nodes = {}
for row in edges:

    if row[0] not in nodes:
        nodes[row[0]]=[]
    if row[1] not in nodes:
        nodes[row[1]]=[]
        
    # record edge for both nodes so that the edge is bi-directional
    nodes[row[0]].append([row[1], row[2], row[3]])
    nodes[row[1]].append([row[0], row[3], row[2]])

# build graph dictionary from node dictionary
# example { "table1": [table2, table5, table6] }
graph = {}
for node in nodes:

    if node not in graph:
        graph[node]=[]
    for row in nodes[node]:
        graph[node] += ([row[0]])

    graph[node] = set(graph[node])



def bfs(graph, start, end):
    """ Simple implementation of standard breadth first search """

    queue = [(start,[start])]
    while queue:
        (node, path) = queue.pop(0)
        for vert in graph[node] - set(path):
            if vert == end:
                yield path + [vert]
            else:
                queue.append((vert, path + [vert]))

def generate_joins(graph, start, tables):
    """ Generate a list of table joins.
    
    Given a graph, a starting node and a list of end nodes,
    generate a list of table joins that will connect all end nodes
    to the start node.
    
    This approach results in a number of duplicate joins, but 
    my (untested) belief is that filtering out these duplicates
    would cost about the same amount of time now as it would
    save later.
    
    """
    js = []
    ps = []
    for table in tables:
        path = list(bfs(graph, start, table))

        if path:
            ps += path[0]

    for table in ps:
        for row in nodes[table]:
            if row[0] in ps:
                js.append([table, row[0], row[1], row[2]])
    return js
