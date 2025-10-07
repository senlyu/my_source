from typing import final
import subprocess
import os
from util.logging_to_file import Logging

@final
class PythonRunShell:
    
    @staticmethod
    def run_commandline(directory_path, command_to_run, command_path=None):
        if command_path is None:
            command_path = []
        my_env = os.environ.copy()
        addition_path = ":".join(command_path) + ":" if len(command_path) > 0 else ""
        my_env["PATH"] = addition_path + my_env["PATH"]
        try:
            result = subprocess.run(
                command_to_run,
                cwd=directory_path,
                check=True, # Raise an exception if the command fails
                capture_output=True, # Capture stdout and stderr
                text=True, # Decode the output as text
                env=my_env
            )
            Logging.log("Command executed successfully.")
            Logging.log("Output:")
            Logging.log(result.stdout)

        except subprocess.CalledProcessError as e:
            Logging.log(f"Command failed with return code {e.returncode}")
            Logging.log("Error:")
            Logging.log(e.stderr)