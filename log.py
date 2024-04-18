from datetime import datetime
import os

def log_to_file(message, log_file_path):

    today_date = datetime.now().strftime("%m_%d_%Y")
    directory = os.path.expanduser(f"{log_file_path}/{today_date}")
    os.makedirs(directory, exist_ok=True)

    with open(f"{log_file_path}/{today_date}/log_{today_date}.txt", 'a') as file:
        file.write(f'{message}\n')