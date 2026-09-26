import socket
import sys

# CONFIGURATION
LISTEN_IP = '0.0.0.0'  # Listen on all interfaces
PORT = 9999

def main():
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
        cmd = input("# ").strip()
        if cmd.lower() == 'exit':
            client.send('exit'.encode())
            break
        
        client.send(cmd.encode())
        
        if cmd.lower() == 'exit':
            break
            
        try:
            result = client.recv(4096)
            if result:
                print(result.decode())
        except:
            print("[!] Connection lost.")
            break

    client.close()
    server.close()

if __name__ == "__main__":
    main()
