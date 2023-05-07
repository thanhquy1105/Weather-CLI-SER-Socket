from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import requests

BASE_WEATHER_URL = "http://api.weatherapi.com/v1"
API_KEY = "ff53ef5d7a2949fe81d174746230705"

def handle_command_line():
    while True:
        inputValue= input('Nhap lenh:')
        if inputValue == 'exit':
            for sock in addresses:
                sock.send(bytes("{quit}", "utf8"))
            SERVER.close()
            print('Server disconnected 1') 
            return 
   

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    try:
        while True:
            client, client_address = SERVER.accept()
            print(client)
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
            msg = client.recv(BUFSIZ).decode("utf8")
            print(msg)

            def request_api_and_sent_data_to_client(query):
                payload = {'key': API_KEY, 'q': query}
                r = requests.get(BASE_WEATHER_URL + "/current.json",params=payload)
                print(r.status_code)
                if r.status_code == 200: 
                    client.send(bytes(r.text, "utf8"))
                elif r.status_code == 400:
                    print("nomatching") 
                    client.send(bytes("{nomatchinglocationfound}", "utf8"))
            
            if msg == "{quit}":
                client.send(bytes("{quit}", "utf8"))
            elif msg == "{getallcity}":
                continue
            else:
                request_api_and_sent_data_to_client(msg)

    except:
        print("%s:%s has disconnected" % addresses[client]) 
        client.close()
        del clients[addresses[client]]
        del addresses[client]
        return
 

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in addresses:
        sock.send(bytes(prefix, "utf8")+msg)

        
clients = {}
addresses = {}

HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen()
    print("Waiting for connection...")

    INPUT_THREAD = Thread(target=handle_command_line)
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)

    INPUT_THREAD.start()
    ACCEPT_THREAD.start()

    ACCEPT_THREAD.join()

    SERVER.close()
 
