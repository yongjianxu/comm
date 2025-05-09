import subprocess
import logging

class WRITE:
    def __init__(self,ibdev, server_ip, port=18515, size=65536, iterations=1000):
        """
        Initialize WRITE class with ib_write_bw parameters
        
        Args:
            server_ip (str): IP address of the server
            port (int): Port number (default: 18515)
            size (int): Message size in bytes (default: 65536)
            iterations (int): Number of iterations (default: 1000)
        """
        self.ibdev=ibdev
        self.server_ip = server_ip
        self.port = port
        self.size = size
        self.iterations = iterations
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
            '--report_gbits -F -D 10',
            self.server_ip
        ]
        
        # Add any additional arguments
        for key, value in kwargs.items():
            if isinstance(value, bool):
                if value:
                    cmd.append(f'-{key}')
            else:
                cmd.extend([f'-{key}', str(value)])
        
        try:
            self.logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running ib_write_bw: {e}")
            self.logger.error(f"Command output: {e.output}")
            raise