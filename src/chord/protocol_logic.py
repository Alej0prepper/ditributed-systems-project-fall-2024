import ast
import time
import chord.node as chord
import requests
import socket
import os
from chord.config import M, STABILIZE_INTERVAL
from chord.node import ChordNode

def is_between(key, start, end, inclusive=False):
    if start < end:
        return start < key <= end if inclusive else start < key < end
    return key > start or key <= end if inclusive else key > start or key < end

def find_successor(key):
    with chord.current_node.lock:
        if not chord.current_node.successor:
            return chord.current_node.to_dict()
        
        if is_between(key, chord.current_node.id, chord.current_node.successor['id'], inclusive=True):
            return chord.current_node.successor
            
        closest = chord.current_node.to_dict()
        for i, entry in enumerate(reversed(chord.current_node.finger)):
            if entry and is_between(entry['id'], chord.current_node.id, key):
                # Verify if the finger entry is alive
                try:
                    requests.get(f"http://{entry['ip']}:{entry['port']}/state", timeout=2)
                    closest = entry
                    break
                except requests.RequestException:
                    continue  # Skip dead nodes
                
        try:
            response = requests.post(
                f"http://{closest['ip']}:{closest['port']}/find_successor",
                json={"key": key}
            )
            return response.json()
        except requests.RequestException:
            return chord.current_node.successor
        
def stabilize():
    while True:
        time.sleep(STABILIZE_INTERVAL)
        try:
            # 1. Get current state snapshot
            with chord.current_node.lock:
                successor = chord.current_node.successor.copy() if chord.current_node.successor else None
                node_id = chord.current_node.id
                local_state = chord.current_node.to_dict()

            # 2. Check successor's predecessor
            if successor:
                try:
                    # Get successor's state
                    response = requests.get(
                        f"http://{successor['ip']}:{successor['port']}/state",
                        timeout=2
                    )
                    successor_state = response.json()
                    successor_predecessor = successor_state.get("predecessor")

                    # Verify if successor's predecessor is alive and valid
                    if successor_predecessor:
                        # Check if the predecessor is actually alive
                        try:
                            requests.get(
                                f"http://{successor_predecessor['ip']}:{successor_predecessor['port']}/state",
                                timeout=2
                            )
                            predecessor_alive = True
                        except requests.RequestException:
                            predecessor_alive = False

                        # Update successor only if predecessor is alive and in range
                        if predecessor_alive and is_between(successor_predecessor['id'], node_id, successor['id']):
                            with chord.current_node.lock:
                                chord.current_node.successor = successor_predecessor
                                print(f"Updated successor to live node {successor_predecessor['id']}")

                    # Notify successor even if predecessor check fails
                    requests.post(
                        f"http://{successor['ip']}:{successor['port']}/notify",
                        json=local_state,
                        timeout=2
                    )

                except requests.RequestException as e:
                    print(f"Successor {successor['id']} unreachable: {str(e)}")
                    with chord.current_node.lock:
                        chord.current_node.successor = None

            # 3. Update finger table
            for i in range(M):
                start = (node_id + 2**i) % (2**M)
                finger_entry = find_successor(start)
                with chord.current_node.lock:
                    chord.current_node.finger[i] = finger_entry

        except Exception as e:
            print(f"Stabilization error: {str(e)}")

def check_predecessor():
    while True:
        time.sleep(STABILIZE_INTERVAL)
        try:
            with chord.current_node.lock:
                predecessor = chord.current_node.predecessor.copy() if chord.current_node.predecessor else None

            if predecessor:
                try:
                    # Check predecessor liveness
                    requests.get(
                        f"http://{predecessor['ip']}:{predecessor['port']}/state",
                        timeout=2
                    )
                except requests.RequestException:
                    print(f"Predecessor {predecessor['id']} is dead. Removing.")
                    with chord.current_node.lock:
                        chord.current_node.predecessor = None

        except Exception as e:
            print(f"Predecessor check error: {str(e)}")

def find_k_successors(K):
    """Find the next `K` successors in the Chord ring."""
    successors = []
    current_ip = chord.current_node.to_dict()["ip"]
    current_port = chord.current_node.to_dict()["port"]

    while K > 0:
        try:
            # Request state from the current node
            response = requests.get(f"http://{current_ip}:{current_port}/state")
            if response.status_code == 200:
                node_data = response.json()
                
                if node_data["ip"] == chord.current_node.to_dict()["ip"]:
                    return successors
                
                successors.append(ChordNode(node_data["ip"], node_data["port"]))

                # Move to the next node in the ring
                current_ip = node_data["ip"]
                current_port = node_data["port"]
                K -= 1
            else:
                print(f"Error: Failed to get state from {current_ip}, status: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Error: Could not contact {current_ip}: {e}")
            break

    return successors

system_entities_list = []

MULTICAST_GROUP_DISCOVERY = os.environ.get('MULTICAST_GROUP_DISCOVERY', '')
DISCOVERY_PORT = int(os.environ.get('DISCOVERY_PORT', ''))
MULTICAST_GROUP_DATA = os.environ.get('MULTICAST_GROUP_DATA', '')
DATA_PORT = int(os.environ.get('DATA_PORT', ''))


def announce_node_to_router():
    message = "JOIN"
    multicast_group = (MULTICAST_GROUP_DISCOVERY, DISCOVERY_PORT)
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            sock.sendto(message.encode(), multicast_group)
            print(f"📡 Sent announcement to router in group {MULTICAST_GROUP_DISCOVERY}:{DISCOVERY_PORT} : {message}")
        time.sleep(30)

def listen_for_chord_updates():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(('', DATA_PORT))
    mreq = socket.inet_aton(MULTICAST_GROUP_DATA) + socket.inet_aton('0.0.0.0')
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode()
        if not (message.split(",")[0], message.split(",")[1]) in system_entities_list:
            update_entities_list(message.split(",")[0], message.split(",")[1])
            
        print(f"📥 Received from {addr}: {message}")

def send_chord_update(message):
    multicast_group = (MULTICAST_GROUP_DATA, DATA_PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(message.encode(), multicast_group)
        print(f"🔄 Sent update: {message}")

def send_local_system_entities_copy():
    while True:
        for email, id in system_entities_list:
            send_chord_update(f"{email},{id}")
        time.sleep(15)

def update_entities_list(email, id):
    # Append the new entry as a string
    system_entities_list.append((email,id))

    folder_path = os.path.join(os.getcwd(), "src", "chord")
    file_path = os.path.join(folder_path, "system_entities_list.txt")

    # Ensure the folder exists, create it if not
    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, "w") as file:
        for entity in system_entities_list:
            file.write(f"{entity[0]} {entity[1]}\n")