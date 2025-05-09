import subprocess
import logging
import threading
import sys

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
            # Run the process the background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Start a thread to monitor the process and print last 5 lines when it exits
            def monitor_output(process):
                stdout, stderr = process.communicate()
                if stdout:
                    last_lines = stdout.strip().split('\n')[-5:]
                    print(f"\nLast 5 lines of output from {' '.join(cmd)}:")
                    for line in last_lines:
                        print(line)
                if stderr:
                    print(f"\nErrors from {' '.join(cmd)}:", file=sys.stderr)
                    print(stderr, file=sys.stderr)
                    
            thread = threading.Thread(target=monitor_output, args=(process,))
            thread.daemon = True
            thread.start()
            
            return process
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running ib_write_bw: {e}")
            raise
