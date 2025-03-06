import time
import requests
import chord.protocol_logic as chord_logic
import chord.node as chord
from database.fetchData import fetch_graph_data
from chord.node import get_hash
from network.middlewares.use_db_connection import use_db_connection

T = 10  # Replication interval in seconds
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

            """ for edge in edges:
                print("Edge: ",edge)
                if edge['start'] is None or edge['end'] is None:
                    continue
                successor = chord_logic.find_successor(get_hash(node["id"]))
                successor_ip = successor["ip"]
                successor_port = successor["port"]

                if successor_ip == chord.current_node.to_dict()["ip"]:
                    replicate_to_k_successors(edge)
                    continue
                
                try:
                    url = f"http://{successor_ip}:{successor_port}/replicate"
                    response = requests.post(url, json={"edges":[edge]})
                    if response.status_code == 200:
                        driver.execute_query(
                            MATCH (u:{id:$id})
                            DETACH DELETE u
                            {"id": edge["id"]}
                        )
                        print(f"Replicated info to its owner: {successor_ip}:{successor_port}, status: {response.status_code}")
                    else: 
                        print(f"Failed to replicate info to its owner: {successor_ip}:{successor_port}, status: {response.status_code}")
                except Exception as e:
                    print(f"Failed to replicate info to its owner: {successor_ip}:{successor_port}, status: {response.status_code}")
 """
            for node in nodes:
                successor = chord_logic.find_successor(get_hash(node["id"]))
                successor_ip = successor["ip"]
                successor_port = successor["port"]

                if successor_ip == chord.current_node.to_dict()["ip"]:
                    replicate_to_k_successors({"nodes":[node]})
                    continue
                
                try:
                    url = f"http://{successor_ip}:{successor_port}/replicate"
                    response = requests.post(url, json={"nodes":[node]})
                    if response.status_code == 200:
                        driver.execute_query(
                            """
                            MATCH (u:{id:$id})
                            DELETE u
                            """,
                            {"id": node["id"]}
                        )
                        print(f"Replicated info to its owner: {successor_ip}:{successor_port}")
                    else:
                        print(f"Failed to replicate info to its owner: {successor_ip}:{successor_port}, error: {response.status_code}")
                except Exception as e:
                    print(e)

        except Exception as e:
            print(f"Replication error: {e}")

        time.sleep(T)


def replicate_to_k_successors(data):
    # Find `k` successors in the Chord ring
    successors = chord_logic.find_k_successors(K)
    print(f"Successors: {successors}")


    for successor in successors:
            successor_ip = successor.ip
            successor_port = successor.port
            try:
                url = f"http://{successor_ip}:{successor_port}/replicate"
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    print(f"Replicated graph to {successor_ip}:{successor_port}")
                else:
                    print(response.json())
            except Exception as e:
                print(f"Failed to replicate to {successor_ip}:{successor_port}: {e}")