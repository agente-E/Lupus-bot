def save_user_data(user_id, user_data):
    try:
        with open("users.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data[user_data['id']] = user_data
    try:
        with open("users.json", "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error al guardar los datos: {e}")