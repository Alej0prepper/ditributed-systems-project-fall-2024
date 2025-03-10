import chord.config
import time
import requests
import base64
import chord.protocol_logic as chord_logic
import chord.node as chord
from database.fetchData import fetch_graph_data
from chord.node import get_hash
from network.middlewares.use_db_connection import use_db_connection
from chord.config import STABILIZE_INTERVAL

K = 2  # Number of successors

@use_db_connection
def replicate_to_owners(driver=None):
    """ Periodically send each part of the graph data to its owners. """
    while True:
        try:
            # Get the full graph data from Neo4j
            graph_data = fetch_graph_data()

            nodes = graph_data["nodes"]
            edges = graph_data["relationships"]

            owners_data = dict()

            for node in nodes:
                successor = chord_logic.find_successor(get_hash(
                    node["id"] if not node["id"] is None else
                    node['userId'] if "Comment" in node["labels"] or "Reaction" in node["labels"] else None
                ))
                successor_ip = successor["ip"]
                successor_port = successor["port"]

                if (successor_ip, successor_port) in owners_data.keys():
                    owners_data[(successor_ip, successor_port)].append(serialize_data(node))
                else:
                    owners_data[(successor_ip, successor_port)] = [serialize_data(node)]

            for succ_ip, succ_port in owners_data.keys():
                # Current node is info owner
                if succ_ip == chord.current_node.to_dict()["ip"]:
                    replicate_to_k_successors({"nodes": owners_data[(succ_ip, succ_port)]})
                    continue
                
                # Send to owner
                try:
                    url = f"http://{succ_ip}:{succ_port}/replicate"
                    print(f"Replicating to {succ_ip}:{succ_port} with data: {owners_data[(succ_ip, succ_port)]}")

                    response = requests.post(url, json={"nodes":owners_data[(succ_ip, succ_port)]})
                except Exception as e:
                    print(f"Failed to replicate info to its owner: {succ_ip}:{succ_port}, status: {response.status_code}")

            owners_data = dict()

            for edge in edges:
                if edge['start'] is None :
                    start = get_relation_start_node(driver, edge["id"])
                successor = chord_logic.find_successor(get_hash(edge["start"] if not edge["start"] is None else start["id"]))
                successor_ip = successor["ip"]

                if successor_ip in owners_data.keys():
                    owners_data[successor_ip].append(serialize_data(edge))
                else:
                    owners_data[successor_ip] = [serialize_data(edge)]

            for succ_ip, succ_port in owners_data.keys():
                

                if succ_ip == chord.current_node.to_dict()["ip"]:
                    replicate_to_k_successors({"relationships": owners_data[(succ_ip, succ_port)]})
                    continue
                
                try:
                    url = f"http://{succ_ip}:{succ_port}/replicate"
                    response = requests.post(url, json={"relationships": owners_data[(succ_ip, succ_port)]})
                except Exception as e:
                    print(f"Failed to replicate info to its owner: {succ_ip}:{succ_port}, status: {response.status_code}")
            
        except Exception as e:
            print(f"Replication error: {e}")

        time.sleep(STABILIZE_INTERVAL*10)

def get_relation_start_node(driver, relation_id):
    node = driver.execute_query(
        """
            MATCH (n) -[r {id: $relation_id}]-> (m)
            RETURN n as node
        """,
        {"relation_id": relation_id}
    ).records[0]["node"]
    print("Node:",node)

def replicate_to_k_successors(data):
    # Find `k` successors in the Chord ring
    successors = chord_logic.find_k_successors(K)

    for successor in successors:
            successor_ip = successor.ip
            successor_port = successor.port
            try:
                url = f"http://{successor_ip}:{successor_port}/replicate"
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    print(f"Replicated graph to {successor_ip}:{successor_port}")
                else:
                    print("500 at replicate to successors:",response.json())
                    print("Data",data)
            except Exception as e:
                print(f"Failed to replicate to {successor_ip}:{successor_port}: {e}")
                print(f"Data: {data}")

def serialize_data(data):
    json_serialized_data = data
    if "password" in data['properties'].keys():
        json_serialized_data['properties']['password'] = base64.b64encode(data['properties']['password']).decode('utf-8')
    if 'datetime' in data['properties'] and not isinstance(data['properties'], str):
        json_serialized_data['properties']['datetime'] = data['properties']['datetime'].isoformat()
    return json_serialized_data