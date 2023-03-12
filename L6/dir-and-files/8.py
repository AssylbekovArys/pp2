import os

file_path = input("Enter path to file to be deleted: ")

if not os.path.exists(file_path):
    print(f"File does not exist: {file_path}")
    exit()

if not os.access(file_path, os.R_OK):
    print(f"File not accessible: {file_path}")
    exit()

os.remove(file_path)
print(f"File deleted: {file_path}")
