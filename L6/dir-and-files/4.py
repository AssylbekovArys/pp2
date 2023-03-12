file_path = input("Enter path to text file: ")

with open(file_path, 'r') as file:
    num_lines = sum(1 for line in file)
    
print(f"Number of lines in the file: {num_lines}")