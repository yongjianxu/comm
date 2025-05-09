import subprocess
import logging
import datetime

class WRITE:
    def __init__(self,ibdev, server_ip=None, port=18515, size=65536, iterations=1000, cuda=None):
        """
        Initialize WRITE class with ib_write_bw parameters
        
        Args:
            server_ip (str): IP address of the server
            port (int): Port number (default: 18515)
            size (int): Message size in bytes (default: 65536)
            iterations (int): Number of iterations (default: 1000)
            cuda (int, optional): CUDA device number to use (default: None)
        """
        self.ibdev=ibdev
        self.server_ip = server_ip
        self.port = port
        self.size = size
        self.iterations = iterations
        self.cuda = cuda
        self.logger = logging.getLogger(__name__)
    
    def run(self, **kwargs):
        """
        Run ib_write_bw command in a subprocess
        
        Args:
            **kwargs: Additional arguments to pass to ib_write_bw
        
        Returns:
            subprocess.CompletedProcess: Result of the subprocess execution
        """
        cmd = [
            'ib_write_bw',
            '-d', self.ibdev,
            '-p', str(self.port),
            '-s', str(self.size),
            '-n', str(self.iterations),
            '--report_gbits',
            '-F',
            '-D', '10',
            '-x', '3',
        ]
        
        # Add CUDA device if specified
        if self.cuda is not None:
            cmd.extend(['--use_cuda', str(self.cuda)])
        
        # Add server_ip if it exists
        if self.server_ip is not None:
            cmd.append(self.server_ip)
        # Add any additional arguments
        for key, value in kwargs.items():
            if isinstance(value, bool):
                if value:
                    cmd.append(f'-{key}')
            else:
                cmd.extend([f'-{key}', str(value)])
        
        try:
            self.logger.info(f"Running command: {' '.join(cmd)}")
            
            # Create a unique filename based on timestamp and device
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"results/ib_write_bw_{self.ibdev}_{timestamp}.log"
            
            # Open file to capture output
            with open(output_file, 'w') as f:
                f.write(f"Command: {' '.join(cmd)}\n\n")
                f.flush()
                
                # Run the process and redirect output to file
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=f,
                    text=True
                )
                
                self.logger.info(f"Writing output to {output_file}")
                return process

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running ib_write_bw: {e}")
            raise
