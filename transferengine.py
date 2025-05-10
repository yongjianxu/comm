import etcd3
import logging
import time
import socket
from typing import Optional, List
import sys

# Configuration constants
DEFAULT_BLOCK_SIZE = 512 * 8192
DEFAULT_BATCH_SIZES = [10, 100, 1000, 10000]
DEFAULT_BUFFER_SIZE = 1 * 1024 * 1024 * 1024
DEFAULT_PORT = 12345
ETCD_PORT = 2379

# Global configuration
gpus = [0, 1, 2, 3, 4, 5, 6, 7]  # Default list of GPUs
devs = ['mlx5_0','mlx5_3','mlx5_4','mlx5_5','mlx5_6','mlx5_9','mlx5_10','mlx5_11']
target_host = ['hgx-isr1-112']
client_host = ['hgx-isr1-111']

# Network configuration
local_ip = socket.gethostname()
target_ip = target_host[0]
meta_ip = client_host[0]

class TRANSFERENGINE:
    def __init__(self, 
                 mode: Optional[str] = None,
                 meta_server: str = None,
                 local_server: str = None,
                 dev: str = None,
                 vram: bool = False,
                 gpuid: Optional[int] = None,
                 op: str = 'write',
                 block_size: int = DEFAULT_BLOCK_SIZE,
                 batch_size: int = 1000,
                 buffer_size: int = DEFAULT_BUFFER_SIZE,
                 segid: Optional[str] = None):
        """
        Initialize TRANSFERENGINE class
        
        Args:
            mode (str, optional): Mode of operation ('target' or None)
            meta_server (str): Metadata server address
            local_server (str): Local server address
            dev (str): Network device to use (e.g. 'mlx5_0')
            vram (bool): Whether to use VRAM
            gpuid (int, optional): GPU device ID to use
            op (str): Operation type ('read' or 'write')
            block_size (int): Size of each transfer block in bytes
            batch_size (int): Number of blocks per batch
            buffer_size (int): Size of transfer buffer in bytes
            segid (str, optional): Segment ID to use

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # Validate required parameters
        if meta_server is None:
            raise ValueError("meta_server is required")
        if local_server is None:
            raise ValueError("local_server is required")
        if dev is None:
            raise ValueError("dev is required")
        if mode not in [None, 'target']:
            raise ValueError("mode must be either None or 'target'")

        self.mode = mode
        self.meta_server = meta_server
        self.local_server = local_server
        self.dev = dev
        self.vram = vram
        self.op = op
        self.block_size = block_size
        self.batch_size = batch_size
        self.buffer_size = buffer_size
        self.gpuid = gpuid
        self.segid = segid
        self.logger = logging.getLogger(__name__)
                    
    def etcd_start(self):
        """
        Start the etcd server process
        """
        try:
            cmd = [
                'etcd',
                f'--listen-client-urls=http://{self.meta_server}:2379',
                f'--advertise-client-urls=http://{self.meta_server}:12345'
            ]
            
            self.logger.info("Running etcd server in background")
            
            # Set stdout and stderr to PIPE to prevent output from blocking
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # This creates a new session, detaching from parent
            )
            # Wait for 10 seconds to let etcd server start
            time.sleep(10)
            
            # Check if etcd server is running properly
            try:
                check_cmd = ["curl", f"http://{self.meta_server}:2379/version"]
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                
                # Check if the response contains expected version information
                if '"etcdserver":"3.' in result.stdout and '"etcdcluster":"3.' in result.stdout:
                    self.logger.info("etcd server started successfully")
                else:
                    self.logger.warning(f"etcd server may not have started correctly. Response: {result.stdout}")
            except Exception as e:
                self.logger.warning(f"Failed to verify etcd server status: {e}")
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start etcd server: {e}")
            raise


    def transfer_start(self):
        """
        Start the transfer engine benchmark process
        """
        try:
            cmd = [
                'transfer_engine_bench',
                f'--mode={self.mode}',
                f'--metadata_server={self.meta_server}:2379',
                f'--local_server={self.local_server}:12345',
                f'--device_name={self.dev}',
                f'-use_vram={self.vram}',
                f'-operation={self.op}',
                f'-protocol={self.protocol}',
                f'-block_size={self.block_size}',
                f'-batch_size={self.batch_size}',
                f'-buffer_size={self.buffer_size}'
            ]
            
            
            if self.gpuid is not None:
                cmd.append(f'-gpu_id={self.gpuid}')
            
            if self.mode is not None:
                cmd.append(f'-gpu_id={self.mode}')
            
            if self.segid is not None:
                cmd.append(f'--segment_id={self.segid}')


            self.logger.info(f"Starting transfer engine benchmark: {' '.join(cmd)}")
            import random
            random_num = random.randint(1000, 9999)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"transfer_engine_{timestamp}_{random_num}.log"
            # Run the transfer engine benchmark process and redirect both stdout and stderr to file
            with open(output_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=f  # Redirect stderr to the same file
                )
            
            self.logger.info(f"Transfer engine benchmark output (stdout and stderr) is being written to {output_file}")
            # Write the command to the beginning of the output file
            with open(output_file, 'r') as f:
                content = f.read()
            
            with open(output_file, 'w') as f:
                f.write(f"Command: {' '.join(cmd)}\n\n")
                f.write(content)
                        
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start transfer engine benchmark: {e}")
            raise

def vram_transfer(mode: Optional[str] = None, 
                 block_size: int = DEFAULT_BLOCK_SIZE, 
                 batch_size: int = 1000) -> List[subprocess.Popen]:
    """
    Create multiple TRANSFERENGINE instances for VRAM transfer
    
    Args:
        mode (str, optional): Mode of operation ('target' or None)
        block_size (int): Size of each transfer block in bytes
        batch_size (int): Number of blocks per batch
    
    Uses the global gpus and devs lists to determine how many instances to create.
    Starts etcd server once and then creates transfer instances for each GPU.
    Starts all transfer_start processes simultaneously.
    
    Returns:
        List[subprocess.Popen]: List of transfer engine processes
    """
    processes = []
    instances = []
    
    if len(gpus) != len(devs):
        raise ValueError(f"Number of GPUs ({len(gpus)}) does not match number of devices ({len(devs)})")
    
    # Create first instance and start etcd server only once
    if len(gpus) > 0:
        first_engine = TRANSFERENGINE(
            mode=mode if mode == 'target' else None,
            meta_server=meta_ip,
            local_server=local_ip,
            dev=devs[0],
            vram=True,
            gpuid=gpus[0],
            block_size=block_size,
            batch_size=batch_size,
            segid=f"{target_ip}:{DEFAULT_PORT}" if mode is None else None
        )
        
        # Start etcd server once
        first_engine.etcd_start()
        instances.append(first_engine)
        
        # Create remaining instances
        for i, gpu_id in enumerate(gpus[1:], 1):
            try:
                transfer_engine = TRANSFERENGINE(
                    mode=mode if mode == 'target' else None,
                    meta_server=meta_ip,
                    local_server=local_ip,
                    dev=devs[i],
                    vram=True,
                    gpuid=gpu_id,
                    block_size=block_size,
                    batch_size=batch_size,
                    segid=f"{target_ip}:{DEFAULT_PORT}" if mode is None else None
                )
                instances.append(transfer_engine)
            except Exception as e:
                logging.error(f"Failed to create TRANSFERENGINE for GPU {gpu_id}: {e}")
    
    # Start all transfer processes simultaneously
    for instance in instances:
        try:
            process = instance.transfer_start()
            processes.append(process)
        except Exception as e:
            logging.error(f"Failed to start transfer for GPU {instance.gpuid}: {e}")
    
    return processes

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    hostname = socket.gethostname()
    
    # Check if the current hostname is in the target_host list
    if hostname in target_host:
        for batch_size in DEFAULT_BATCH_SIZES:
            vram_transfer(mode='target', block_size=DEFAULT_BLOCK_SIZE, batch_size=batch_size)
    elif hostname in client_host:
        for batch_size in DEFAULT_BATCH_SIZES:
            vram_transfer(mode=None, block_size=DEFAULT_BLOCK_SIZE, batch_size=batch_size)
    else:
        logging.error(f"Unexpected hostname: {hostname}")
        sys.exit(1)

    