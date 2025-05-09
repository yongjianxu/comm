import subprocess
import logging

class WRITE:
    def __init__(self,ibdev, server_ip=None, port=18515, size=65536, iterations=1000):
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
            '--report_gbits',
            '-F',
            '-D', '10',
        ]
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
            # Run the process and print output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
                bufsize=1
            )

            # Print output in real-time
            while True:
                output = process.stdout.readline()
                error = process.stderr.readline()
                
                if output:
                    print(output.strip())
                if error:
                    print(error.strip(), file=sys.stderr)
                    
                # Break if process has finished and no more output
                if process.poll() is not None and not output and not error:
                    break
            return process
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running ib_write_bw: {e}")
            raise
