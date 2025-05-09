from write import WRITE
import sys
import socket
hostname = socket.gethostname()
# Test config
clients = ['hgx-isr1-111']
servers = ['hgx-isr1-112']
# make sure ibdevs and cudevs matches in locality
ibdevs = ['mlx5_0','mlx5_3','mlx5_4','mlx5_5','mlx5_6','mlx5_9','mlx5_10','mlx5_11']
cudevs = [0,1,2,3,4,5,6,7]
ports = [6667,6668,6669,6670,6671,6672,6673,6674]

def cpu_perftest():
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
def gpu_perftest():
    # Check if hostname is in client or server list
    if hostname in clients: 
        for i in range(len(ibdevs) + 1):
            ibdev = ibdevs[i % len(ibdevs)]  # Alternate between mlx5_0 and mlx5_1
            port = ports[i % len(ports)]      # Alternate between ports
            server = servers[i % len(servers)]
            cuda = cudevs[i % len(cudevs)]
            write = WRITE(ibdev, server_ip=server, port=port, cuda=cuda)
            write.run()
    elif hostname in servers:
        for i in range(len(ibdevs)):
            ibdev = ibdevs[i % len(ibdevs)]  # Alternate between mlx5_0 and mlx5_1
            port = ports[i % len(ports)]  
            cuda = cudevs[i % len(cudevs)]
            write = WRITE(ibdev, port=port, cuda=cuda)
            write.run() 
    else:
        print(f"Unexpected hostname: {hostname}")
        sys.exit(1)

gpu_perftest()
