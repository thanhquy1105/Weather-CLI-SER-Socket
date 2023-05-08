from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from tkinter import messagebox,ttk
import json 
import struct

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
    print(msglen)
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


def receive():
    """Handles receiving of messages."""
    id_table = 0

    while True:
        try:
            msg = recv_msg(client_socket).decode('utf-8')
            print(msg)
            if msg == "{quit}":
                messagebox.showinfo("Notification", "Server has just stopped")
                on_closing()
                break
            elif msg == "{nomatchinglocationfound}":
                messagebox.showinfo("Notification", "No matching location found")
            else:
                try:
                    item = json.loads(msg)
                    # for item in data:
                    table.insert(parent='',index='end',iid=id_table,text='',
                    values=(item["city"],item["temperature"],item["condition"]))
                    id_table=id_table+1
                except:
                    continue
               
               
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    if len(table.get_children()) > 10:
        clear_all_table()
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    send_msg(client_socket, msg)
    if msg == "{quit}":
        client_socket.close()
        root.quit()

def get_all_city():
    clear_all_table()
    my_msg.set("{getallcity}")
    send()

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()

####################### GUI ##########################
# Define a function to clear all the items present in Treeview
def clear_all_table():
   for item in table.get_children():
      table.delete(item)

root = tkinter.Tk()
root.title("Weather Client")
#### LEFT_FRAME ####
left_frame = tkinter.Frame(root,width=100,height=20)
scrollbar = tkinter.Scrollbar(left_frame,orient=tkinter.VERTICAL)  # To navigate through past messages.
table = ttk.Treeview(left_frame,height=20, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
table['columns'] = ('city', 'temperature', 'condition')
table.column("#0", width=0,  stretch=tkinter.NO)
# table.column("id",anchor=tkinter.CENTER,width=50,minwidth= 50)
table.column("city",anchor=tkinter.CENTER,width=120,minwidth= 100)
table.column("temperature",anchor=tkinter.CENTER,width=120,minwidth= 100)
table.column("condition",anchor=tkinter.CENTER,width=200,minwidth= 150)

table.heading("#0",text="",anchor=tkinter.CENTER)
# table.heading("id",text="Id",anchor=tkinter.CENTER)
table.heading("city",text="City",anchor=tkinter.CENTER)
table.heading("temperature",text="Temperature",anchor=tkinter.CENTER)
table.heading("condition",text="Condition",anchor=tkinter.CENTER)

table.pack()
left_frame.pack(side=tkinter.LEFT)

#### RIGHT_FRAME ####
right_frame = tkinter.Frame(root,background='lightblue')
get_all_city_button = tkinter.Button(right_frame, text="Get All City", command=get_all_city, width=40)
get_all_city_button.grid(row=0,column=0,padx=10,pady=10)
lbl = tkinter.Label(right_frame,background='lightblue', text="Search city",font=('',10))
lbl.grid(row=1,column=0,padx=0,pady=2,sticky=tkinter.W)

my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("")
entry_field = tkinter.Entry(right_frame,width=40, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.grid(row=2,column=0,padx=0,pady=0)
search_button = tkinter.Button(right_frame, text="Send", command=send)
search_button.grid(row=2,column=1,padx=5,pady=0)
right_frame.pack(side=tkinter.RIGHT,padx=5)

#### CLOSE_WINDOW ####
root.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
HOST = '127.0.0.1' 
PORT = 33115

ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
try:
    client_socket.connect(ADDR)
    receive_thread = Thread(target=receive)
    receive_thread.start()
    tkinter.mainloop()  # Starts GUI execution.

except:
    client_socket.close()
    print('Can not connect to server')

