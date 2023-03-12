import os

path = "C:/Users/acer/Desktop/git lessin/L6"

print("Directories:")
for dir_name in os.listdir(path):
    if os.path.isdir(os.path.join(path, dir_name)):
        print(dir_name)

print("Files:")
for file_name in os.listdir(path):
    if os.path.isfile(os.path.join(path, file_name)):
        print(file_name)

print("All directories and files:")
for item_name in os.listdir(path):
    print(item_name)