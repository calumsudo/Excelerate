from datetime import datetime
import os


def log_to_file(message, output_path, portfolio_name):
    if portfolio_name == 1:
        portfolio_name = "Alder"
    elif portfolio_name == 2:
        portfolio_name = "White Rabbit"

    today_date = datetime.now().strftime("%m_%d_%Y")
    directory = os.path.expanduser(f"{output_path}/{portfolio_name}/{today_date}")
    os.makedirs(directory, exist_ok=True)

    with open(
        f"{output_path}/{portfolio_name}/{today_date}/log_{today_date}.txt", "a"
    ) as file:
        file.write(f"{message}\n")
