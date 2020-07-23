#file_name = "C:/Users/86248/Desktop/learn/python/pi_digits.txt"
file_name = "python/pi_digits.txt"
with open(file_name) as file_obj:
    contents = file_obj.read()
    print(contents.rstrip())
    