from typing import final
import subprocess
from util.logging_to_file import Logging

@final
class PythonRunShell:
    
    @staticmethod
    def run_commandline(directory_path, command_to_run):
        try:
            result = subprocess.run(
                command_to_run,
                cwd=directory_path,
                check=True, # Raise an exception if the command fails
                capture_output=True, # Capture stdout and stderr
                text=True # Decode the output as text
            )
            Logging.log("Command executed successfully.")
            Logging.log("Output:")
            Logging.log(result.stdout)

        except subprocess.CalledProcessError as e:
            Logging.log(f"Command failed with return code {e.returncode}")
            Logging.log("Error:")
            Logging.log(e.stderr)