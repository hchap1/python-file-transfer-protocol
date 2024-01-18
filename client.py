import socket, threading, os, math, time

time.sleep(1)
host = "192.168.4.35"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try: 
    s.connect((host, 69))
    print("CONNECTED TO SERVER @ %s" % host)
except ConnectionRefusedError: print("SERVER NOT ACTIVE AT GIVEN ADDRESS OR PORT")

buffer_size = 1024

class client_object:
    def __init__(self, s:socket.socket):
        self.s = s
        self.running = True
        self.recv_thread = threading.Thread(target=self.receive_files)
        self.recv_thread.start()

    def transmit_file(self, filepath:str, address:str):
        file_size = os.stat(filepath).st_size
        number_of_transmissions = math.ceil(file_size / buffer_size)
        file_name = filepath.split("/")[-1]

        #print("SENDING FILE OF SIZE %s THROUGH %s TRANSMISSIONS" % (file_size, number_of_transmissions))

        file_info_package = ("%s %s %s" % (file_name, file_size, address)).encode()
        self.s.sendall(file_info_package)

        time.sleep(0.1) # Allow time for file_info to be received

        with open(filepath, "rb") as source_file:
            for transmission_number in range(number_of_transmissions):
                data = source_file.read(buffer_size)
                self.s.sendall(data)

            #print("REMAINING BYTES: %s" % (file_size - source_file.tell()))

        self.s.sendall(b'done')

    def receive_files(self):
        while self.running:
            try:
                name, size, addr = self.s.recv(1024).decode().split(" ")
                size = int(size)
                number_of_transmissions = math.ceil(size / buffer_size)
                print("TRANSMISSION INCOMING -> FILE: %s SIZE: %s bytes" % (name, size))

                with open(name, "wb") as dest_file:
                    done = False
                    #for transmission_number in range(number_of_transmissions):
                    while not done:
                        data = self.s.recv(buffer_size)
                        if data == b'done':
                            done = False
                            break
                        dest_file.write(data)
                        if data.endswith(b'done'):
                            done = False
                            break

                print("TRANSMISSION COMPLETE. %s bytes WRITTEN TO %s" % (size, name))

            except ConnectionResetError:
                self.running = False
                print("SERVER CONNECTION RESET")

client = client_object(s)
name = socket.gethostname()
ip = socket.gethostbyname(name)

while True:
    command_line = input("%s -> " % name)

    # send filepath to address

    if command_line.split(" ")[0] == "send":
        filepath = command_line.split(" to ")[0].strip("send ").replace(" ", "_")
        address = command_line.split(" to ")[1]
        client.transmit_file(filepath, address)
        print("TRANSMITTED %s TO %s" % (filepath, address))
