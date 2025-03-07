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

            for node in nodes:
                successor = chord_logic.find_successor(get_hash(node["id"]))
                successor_ip = successor["ip"]
                successor_port = successor["port"]

                if successor_ip == chord.current_node.to_dict()["ip"]:
                    node = serialize_data(node)
                    replicate_to_k_successors({"nodes":[node]})
                    continue
                
                try:
                    url = f"http://{successor_ip}:{successor_port}/replicate"
                    json_serialized_node = node

                    json_serialized_node = serialize_data(node)

                    print(f"Replicating to {successor_ip}:{successor_port} with data: {json_serialized_node}")

                    response = requests.post(url, json={"nodes":[json_serialized_node]})
                except Exception as e:
                    print(f"Failed to replicate info to its owner: {successor_ip}:{successor_port}, status: {response.status_code}")


            for edge in edges:
                if edge['start'] is None or edge['end'] is None:
                    continue
                successor = chord_logic.find_successor(get_hash(edge['start']))
                successor_ip = successor["ip"]
                successor_port = successor["port"]

                if successor_ip == chord.current_node.to_dict()["ip"]:
                    edge = serialize_data(edge)
                    replicate_to_k_successors({"relationships":[edge]})
                    continue
                
                try:
                    url = f"http://{successor_ip}:{successor_port}/replicate"
                    response = requests.post(url, json={"relationships":[edge]})
                except Exception as e:
                    print(f"Failed to replicate info to its owner: {successor_ip}:{successor_port}, status: {response.status_code}")

            
        except Exception as e:
            print(f"Replication error: {e}")

        time.sleep(STABILIZE_INTERVAL*10)


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