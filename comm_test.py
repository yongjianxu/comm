from write import WRITE
import sys
hostname = sys.gethostname()
# Define client and server hostnames
clients = ['hgx-isr1-111']
servers = ['hgx-isr1-112']
ibdevs = ['mlx5_0', 'mlx5_1']
ports = [6666, 6667]
# Check if hostname is in client or server list
if hostname in clients: 
    for i in range(len(ibdevs)):
        ibdev = ibdevs[i % len(ibdevs)]  # Alternate between mlx5_0 and mlx5_1
        port = ports[i % len(ports)]      # Alternate between ports
        write = WRITE(ibdev, server_ip='10.10.10.2', port=port)
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
