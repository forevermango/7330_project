import os

def load_config(file_path: str = 'config.txt'):
    config = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Configuration file not found.")
    except Exception as e:
        print(f"Error reading config: {e}")
    return config

# You could load and set to environment here, or return a config dict.
config = load_config()

