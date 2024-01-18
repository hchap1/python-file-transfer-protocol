import socket, math, time, threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 69))
s.listen()

class server_object:
    def __init__(self):
        self.clients = {}

    def forward_file_info(self, file_info:bytes, addr:str):
        if addr in self.clients.keys():
            self.clients[addr].client.send(file_info)
        else:
            print("FAILURE TO SEND FILE INFO TO %s: NO SUCH CLIENT EXISTS" % addr)

    def forward_bytes(self, package:bytes, addr:str):
        if addr in self.clients.keys():
            self.clients[addr].client.send(package)
        else:
            print("FAILURE TO SEND PACKAGE TO %s: NO SUCH CLIENT EXISTS" % addr)
            
class client_object:
    def __init__(self, client, addr:int, server:server_object):
        self.server = server
        self.server.clients[addr] = self
        self.client = client
        self.addr = addr
        self.running = True
        self.buffer_size = 1024

        self.recv_thread = threading.Thread(target=self.listen_for_incoming_files)
        self.recv_thread.start()

    def listen_for_incoming_files(self):
        while self.running:
            try:
                print("LISTENING FOR FILES FROM %s" % self.addr)
                file_info = self.client.recv(1024)
                print(file_info)
                name, size, address = (file_info.decode()).split(" ")
                size = int(size)
                bytes_used = 0
                self.server.forward_file_info(file_info, address)
                number_of_transmissions = math.ceil(size / self.buffer_size)

                print("START TRANSMISSION. %s BYTES BEING SENT FROM %s TO %s OVER %s TRANSMISSIONS" % (size, self.addr, address, number_of_transmissions))

                done = False
                while not done:
                    bytes_used += self.buffer_size
                    data = self.client.recv(self.buffer_size)
                    if data == b'done':
                        done = False
                        break
                    self.server.forward_bytes(data, address)
                    if data.endswith(b'done'):
                        done = False
                        break

                self.server.forward_bytes(b'done', address)

                print("BYTES LEFT: %s" % (size - bytes_used))

                print("END TRANSMISSION. %s BYTES SENT FROM %s TO %s" % (size, self.addr, address))

            except ConnectionResetError:
                print("CLIENT DISCONNECT: %s" % self.addr)
                self.running = False
                server.clients.pop(self.addr)

server = server_object()

def constantly_listen_for_clients(s):
    while True:
        client, addr = s.accept()
        new_client = client_object(client, addr[0], server)
        print("CONNECTED TO CLIENT @ ADDR %s" % addr[0])

constantly_listen_for_clients(s)
