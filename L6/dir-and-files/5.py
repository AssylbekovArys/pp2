list_to_write = ['apple', 'banana', 'orange']

file_path = input("Enter path for the output file: ")

with open(file_path, 'w') as file:
    for item in list_to_write:
        file.write(f"{item}\n")
        
print(f"List written to file: {file_path}")
