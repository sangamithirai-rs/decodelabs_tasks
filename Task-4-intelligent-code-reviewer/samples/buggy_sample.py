import os

def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    result = db.execute(query)
    return result

def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    average = total / len(numbers)
    return average

def process_items(items):
    results = []
    for item in items:
        for other in items:
            if item == other:
                results.append(item)
    return results

def read_config(path):
    f = open(path, "r")
    data = f.read()
    return data

password = "admin123"

def check_login(username, pw):
    if username == "admin" and pw == password:
        return True