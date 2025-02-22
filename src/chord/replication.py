import time
import requests
import chord.protocol_logic as chord_logic
import chord.node as chord
from database.fetchData import fetch_graph_data

T = 10  # Replication interval in seconds
K = 2  # Number of successors

def replicate_to_owners():
    """ Periodically send each part of the graph data to its owners. """
    while True:
        try:
            # Get the full graph data from Neo4j
            graph_data = fetch_graph_data()
            
            nodes = graph_data["nodes"]
            edges = graph_data["relationships"]

            """ for node in nodes:
                print("Node: ",node)
                successor = chord_logic.find_successor(node["id"])
                successor_ip = successor["ip"]
                successor_port = successor["port"]

                if successor_ip == chord.current_node.to_dict()["ip"]:
                    replicate_to_k_successors(node)
                    continue
                
                try:
                    url = f"http://{successor_ip}:{successor_port}/replicate"
                    response = requests.post(url, json=node)
                    print(f"Replicated info to its owner: {successor_ip}:{successor_port}, status: {response.status_code}")
                except Exception as e:
                    print(f"Failed to replicate info to its owner: {successor_ip}:{successor_port}, status: {response.status_code}")
                    
            for edge in edges:
                print("Edge: ",edge)
                successor = chord_logic.find_successor(edge["id"])
                successor_ip = successor["ip"]
                successor_port = successor["port"]

                if successor_ip == chord.current_edge.to_dict()["ip"]:
                    replicate_to_k_successors(edge)
                    continue
                
                try:
                    url = f"http://{successor_ip}:{successor_port}/replicate"
                    response = requests.post(url, json=edge)
                    print(f"Replicated info to its owner: {successor_ip}:{successor_port}, status: {response.status_code}")
                except Exception as e:
                    print(f"Failed to replicate info to its owner: {successor_ip}:{successor_port}, status: {response.status_code}") """

        except Exception as e:
            print(f"Replication error: {e}")

        time.sleep(T)


def replicate_to_k_successors(data):
    # Find `k` successors in the Chord ring
    successors = chord_logic.find_k_successors(K)

    for successor in successors:
            successor_ip = successor["ip"]
            successor_port = successor["port"]
            try:
                url = f"http://{successor_ip}:{successor_port}/replicate"
                response = requests.post(url, json=data)
                print(f"Replicated graph to {successor_ip}:{successor_port}, status: {response.status_code}")
            except Exception as e:
                print(f"Failed to replicate to {successor_ip}:{successor_port}: {e}")