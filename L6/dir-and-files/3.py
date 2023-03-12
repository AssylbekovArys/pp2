import os

path = input("Enter a path: ")

if os.path.exists(path):
    print(f"{path} exists")
    dirname = os.path.dirname(path)
    filename = os.path.basename(path)
    print(f"Directory: {dirname}")
    print(f"Filename: {filename}")
else:
    print(f"{path} does not exist")