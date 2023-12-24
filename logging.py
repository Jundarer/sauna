import datetime

class Logger:
    """Logging class that writes messages to a file."""
    
    def __init__(self, file_name):
        self.file_name = file_name

    def log(self, message):
        print(message)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{timestamp}: {message}"
        with open(self.file_name, 'a') as log_file:
            log_file.write(full_message + '\n')