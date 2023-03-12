src_path = input("Enter path to source file: ")
dst_path = input("Enter path to destination file: ")

with open(src_path, 'rb') as src_file:
    with open(dst_path, 'wb') as dst_file:
        dst_file.write(src_file.read())

print(f"Contents of {src_path} copied to {dst_path}")
