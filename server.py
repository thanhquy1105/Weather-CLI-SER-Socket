from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import requests
from pymongo import MongoClient
import json
import struct 

BASE_WEATHER_URL = "http://api.weatherapi.com/v1"
API_KEY = "ff53ef5d7a2949fe81d174746230705"

def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb://localhost:27017/"
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)
    print('connected db')
    return client['cityweather']

def seeding():
    if collection.count_documents({}) == 0:
        item1 = {
            "city" : "Paris",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        item2 = {
            "city" : "Hanoi",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        item3 = {
            "city" : "Vung Tau",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        item4 = {
            "city" : "Da Nang",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        item5 = {
            "city" : "Hai Phong",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        item6 = {
            "city" : "Nha Trang",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        item7 = {
            "city" : "Yen Bai",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        item8 = {
            "city" : "Binh Dinh",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        item9 = {
            "city" : "New York",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        item10 = {
            "city" : "Tokyo",
            "temperature" : "20",
            "condition" : "Sunny",
        }
        collection.insert_many([item1,item2,item3,item4,item5,item6,item7,item8,item9,item10])

def handle_command_line():
    while True:
        inputValue= input('Nhap lenh:')
        if inputValue == 'exit':
            for sock in addresses:
                send_msg(sock,"{quit}")
            SERVER.close()
            print('Server disconnected 1') 
            return 

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg.encode()
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    try:
        while True:
            client, client_address = SERVER.accept()
            print(client_address)
            print("%s:%s has connected." % client_address)
            addresses[client] = client_address
            clients[client_address] = client
            Thread(target=handle_client, args=(client,)).start()
    except:
        print('Server disconnected 2') 
        return 

def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    try:
        while True:
            msg = recv_msg(client).decode('utf-8')
            print("QUERY: " + msg)

            def request_api_and_sent_data_to_client(query):
                payload = {'key': API_KEY, 'q': query}
                r = requests.get(BASE_WEATHER_URL + "/current.json",params=payload)
                print(r.status_code)
                if r.status_code == 200:
                    data = json.loads(r.text)
                    res = {
                        "city": data["location"]["name"],
                        "temperature": str(data["current"]["temp_c"]),
                        "condition": data["current"]["condition"]["text"]
                    }
                    print(res)
                    send_msg(client,json.dumps(res))
                    if collection.count_documents({"city" : res["city"]}) > 0:
                        collection.update_one({"city" : res["city"]}, { "$set": res })
                    else:
                        collection.insert_one(res)

                elif r.status_code == 400:
                    print("NO MATCHING") 
                    send_msg(client,"{nomatchinglocationfound}")
            
            if msg == "{quit}":
                print('QUIT')
                send_msg(client,"{quit}")
            elif msg == "{getallcity}":
                print('GET ALL CITY')
                items = collection.find({},{"_id": 0,'city': 1,'temperature': 1, 'condition':1})
                for item in items: 
                    request_api_and_sent_data_to_client(item["city"])
            else:
                print('GET CITY')
                request_api_and_sent_data_to_client(msg)

    except:
        print("%s:%s has disconnected" % addresses[client]) 
        client.close()
        del clients[addresses[client]]
        del addresses[client]
        return
 
clients = {}
addresses = {}

HOST = ''
PORT = 33115
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen()

    dbname = get_database()
    collection = dbname["weather"]
    seeding()

    print("Waiting for connection...")

    INPUT_THREAD = Thread(target=handle_command_line)
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)

    INPUT_THREAD.start()
    ACCEPT_THREAD.start()

    ACCEPT_THREAD.join()

    SERVER.close()
 
