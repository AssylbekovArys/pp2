import string

letters = string.ascii_uppercase

for letter in letters:
    file_name = f"{letter}.txt"
    with open(file_name, 'w') as file:
        file.write(f"This is file {file_name}")
    print(f"Created file: {file_name}")
