from datetime import datetime, timedelta
import logging
import os

from src.util.session_context import SessionIDHelper
from src.util.sys_env import get_is_dev_mode

class Colors:
    """ANSI color codes for log formatting."""
    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    BOLD_RED = '\033[1;31m'
    RESET = '\033[0m' # Resets color to default

LEVEL_COLORS = {
    logging.DEBUG: Colors.CYAN,
    logging.INFO: Colors.GREEN,
    logging.WARNING: Colors.YELLOW,
    logging.ERROR: Colors.RED,
    logging.CRITICAL:Colors.WHITE,
}


class ContextSessionFilter(logging.Filter):
    def filter(self, record):
        session_id = SessionIDHelper.get_session_id()
        record.session_id = session_id
        return True
    
class ColoredFileFormatter(logging.Formatter):
    """
    A custom formatter that injects ANSI color codes based on log level.
    """
    FORMAT = "[%(asctime)s] - [%(name)s] - [%(session_id)s] - [%(levelname)s] - %(message)s"
    
    # Map logging levels to color codes
    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.WHITE,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        formatted_message = f"{color}{self.FORMAT}{Colors.RESET}"
        formatter = logging.Formatter(formatted_message, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)
    
class LoggingDirectoryHandle:
    def __init__(self, path):
        self.path = path
        os.makedirs(self.path, exist_ok=True)

    def get_today_file_name(self):
        now_date = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.path, now_date + ".log")


class DefaultLogger:
    @staticmethod
    def getLogger(app_name="default", logging_level=logging.DEBUG, log_path="./log/standard"):
        is_dev_mode = get_is_dev_mode()
        if is_dev_mode:
            log_path = "./"

        new_logger = logging.getLogger(app_name)
        new_logger.setLevel(logging_level)

        log_handler = LoggingDirectoryHandle(log_path) 
        file_name = log_handler.get_today_file_name() if not is_dev_mode else "dev.log"
        file_handler = logging.FileHandler(file_name, encoding='utf-8', mode='a')
        
        file_handler.setFormatter(ColoredFileFormatter())
        new_logger.addFilter(ContextSessionFilter())
        new_logger.addHandler(file_handler)
        return new_logger
    
    @staticmethod
    def clean(log_path="./log/standard"):
        is_dev_mode = get_is_dev_mode()
        if is_dev_mode:
            file_name = os.path.join("./log.log")
            if os.path.isfile(file_name):
                os.remove(file_name)
            return

        storage_path = os.path.join(log_path)
        all_file_names = []
        for root, _, files in os.walk(storage_path):
            for file in files:
                if file.lower().endswith('.log'):  # Case-insensitive check
                    full_path = os.path.join(root, file)
                    if os.path.isfile(full_path):
                        all_file_names.append([file, full_path])
        delete_targets = []
        for item in all_file_names:
            file_name = item[0]
            date_in_file = file_name.split('.')[0]
            try:
                date_obj_file = datetime.strptime(date_in_file, '%Y-%m-%d')
            except Exception as e:
                print(e)
                continue
            
            if date_obj_file + timedelta(days=30) < datetime.now():
                delete_targets.append(item[1])
        for full_path in delete_targets:
            os.remove(full_path)
            print(f"remove file: {full_path}")
    
if __name__ == "__main__":
    logger = DefaultLogger.getLogger("test")

    def run_session_task(session_label):
        session = SessionIDHelper()
        session.create_session_id()
        try:
            logger.info('Starting task for %s', session_label)
            logger.info('Finishing task for %s', session_label)
        finally:
            # Crucial: Reset the context variable to its previous state (or default)
            session.reset_session_id()

    # Example usage (works synchronously and asynchronously)
    logger.info("Application start (No session context yet)")
    run_session_task("Session A")
    run_session_task("Session B")
    logger.info("Application end (No session context yet)")
    logger.debug("Application end (No session context yet)")
    logger.warning("Application end (No session context yet)")
    logger.error("Application end (No session context yet)")
    logger.critical("Application end (No session context yet)")

