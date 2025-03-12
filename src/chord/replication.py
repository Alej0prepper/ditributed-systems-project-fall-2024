import chord.config
import time
import requests
import base64
import chord.protocol_logic as chord_logic
import chord.node as chord
from database.fetchData import fetch_graph_data
from chord.node import get_hash
from network.middlewares.use_db_connection import use_db_connection
import random

K = 2  # Number of replicas of each node

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
                successor = None
                if "Comment" in node['labels']:
                    successor = chord_logic.find_successor(get_hash(
                        node['properties']['userId']
                    ))
                if "Post" in node['labels'] or "User" in node['labels'] or "Gym" in node['labels']:
                    if node['id'] is None:
                        node_relation = get_node_relation(driver, node["username"])
                        successor = chord_logic.find_successor(get_hash(
                            node_relation['start']
                        ))
                    else:
                        successor = chord_logic.find_successor(get_hash(
                            node['id']
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

                    response = requests.post(url, json={"nodes":owners_data[(succ_ip, succ_port)]})
                except Exception as e:
                    print(f"Failed to replicate info to its owner: {succ_ip}:{succ_port}, status: {response.status_code}")

            owners_data = dict()

            for edge in edges:
                successor = chord_logic.find_successor(get_hash(edge["start"]))
                successor_ip = successor["ip"]
                successor_port = successor["port"]

                if edge['type'] is None: continue

                if (successor_ip, successor_port) in owners_data.keys():
                    owners_data[(successor_ip, successor_port)].append(serialize_data(edge))
                else:
                    owners_data[(successor_ip, successor_port)] = [serialize_data(edge)]
            
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

        time.sleep(random.randint(5, 25))

def get_node_relation(driver, username):
    relation = driver.execute_query(
        """
            MATCH (n) -[r]-> (m {username: $username})
            RETURN r
        """,
        {"username": username}
    ).records[0]["r"]
    return relation

def replicate_to_k_successors(data):
    # Find `k` successors in the Chord ring
    successors = chord_logic.find_k_successors(K)

    for successor in successors:
            successor_ip = successor.ip
            successor_port = successor.port
            try:
                url = f"http://{successor_ip}:{successor_port}/replicate"
                response = requests.post(url, json=data)
                if response.status_code != 200:
                    print("500 at replicate to successors:",response.json())
                    print("Data",data)
            except Exception as e:
                print(f"Failed to replicate to {successor_ip}:{successor_port}: {e}")
                print(f"Data: {data}")

def serialize_data(data):
    json_serialized_data = data
    if "password" in data['properties'].keys() and not isinstance(data['properties']['password'], str):
        json_serialized_data['properties']['password'] = base64.b64encode(data['properties']['password']).decode('utf-8')
    if 'datetime' in data['properties'] and not isinstance(data['properties']['datetime'], str):
        json_serialized_data['properties']['datetime'] = data['properties']['datetime'].isoformat()
    return json_serialized_data