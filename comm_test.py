from write import WRITE
import sys
import socket
hostname = socket.gethostname()
# Define client and server hostnames
clients = ['hgx-isr1-111']
servers = ['hgx-isr1-112']
ibdevs = ['mlx5_1']
ports = [6667]
# Check if hostname is in client or server list
if hostname in clients: 
    for i in range(len(ibdevs) + 1):
        ibdev = ibdevs[i % len(ibdevs)]  # Alternate between mlx5_0 and mlx5_1
        port = ports[i % len(ports)]      # Alternate between ports
        server = servers[i % len(servers)]
        write = WRITE(ibdev, server_ip=server, port=port)
        write.run()
elif hostname in servers:
    for i in range(len(ibdevs)):
        ibdev = ibdevs[i % len(ibdevs)]  # Alternate between mlx5_0 and mlx5_1
        port = ports[i % len(ports)]      # Alternate between ports
        write = WRITE(ibdev, port=port)
        write.run() 
else:
    print(f"Unexpected hostname: {hostname}")
    sys.exit(1)
