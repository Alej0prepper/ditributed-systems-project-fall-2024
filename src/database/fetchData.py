from network.middlewares.use_db_connection import use_db_connection

@use_db_connection
def fetch_graph_data(driver=None):
    """Retrieve all nodes and relationships from Neo4j as JSON."""
    query = """
    MATCH (n) OPTIONAL MATCH (n)-[r]->(m) 
    RETURN COLLECT(DISTINCT {id: n.id, labels: labels(n), properties: properties(n)}) AS nodes,
           COLLECT(DISTINCT {id: r.id, type: TYPE(r), properties: properties(r), start: n.id, end: m.id}) AS relationships
    """
    with driver.session() as session:
        result = session.run(query)
        record = result.single()
        return {
            "nodes": record["nodes"],
            "relationships": record["relationships"]
        }