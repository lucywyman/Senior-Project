import psycopg2
import psycopg2.extras

conn = psycopg2.connect("dbname=postgres user=postgres password=killerkat5", cursor_factory= psycopg2.extras.RealDictCursor)
conn.autocommit = True

cur = conn.cursor()

edges = []
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
tables = cur.fetchall()

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
   
nodes = {}
for row in edges:
    
    if row[0] not in nodes:
        nodes[row[0]]=[]
    if row[1] not in nodes:
        nodes[row[1]]=[]    
    nodes[row[0]].append([row[1], row[2], row[3]])
    nodes[row[1]].append([row[0], row[3], row[2]])
    
graph = {}
for node in nodes:
    
    if node not in graph:
        graph[node]=[]
    for row in nodes[node]:
        graph[node] += ([row[0]])
        
    graph[node] = set(graph[node])

    

def bfs(graph, start, end):
    
    queue = [(start,[start])]
    while queue:
        (node, path) = queue.pop(0)
        for vert in graph[node] - set(path):
            if vert == end:
                yield path + [vert]
            else:
                queue.append((vert, path + [vert]))
                
def generate_joins(graph, start, tables):
    js = []
    ps = []
    for table in tables:
        # print(graph)
        # print("-----")
        # print(start)
        # print(table)
        path = list(bfs(graph, start, table))

        if path:
            ps += path[0]
            
    for table in ps:
        for row in nodes[table]:
            if row[0] in ps:
                js.append([table, row[0], row[1], row[2]])
    
    # TODO - OPTIMIZATION - remove duplicates in js, they don't harm
    # anything, but cause extra iterations. On the other hand,
    # quite possible that time gained later would be approx equal
    # to time spent removing duplicates?
                
    return js