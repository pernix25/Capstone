import os

folder_path = "/Volumes/phoneUSB/Capstone"

try:
    # List all items in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    print(f"Number of files: {len(files)}")
except FileNotFoundError:
    print("The folder does not exist.")
except Exception as e:
    print(f"An error occurred: {e}")
