def get_user_data(user_id):
    try:
        with open("users.json", "r") as file:
            data = json.load(file)
            if not isinstance(data, dict):
                data = {}
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data.get(user_id, {'id': user_id, 'echoes': 0, 'experiencia': 0, 'nivel': 1, 'last_gacha': 0, 'pity_counter': 0, 'roles_obtenidos': []})