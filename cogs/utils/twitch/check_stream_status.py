def check_stream_status():
    global token_dacces
    try:
        if not token_valido():
            obtener_token()
        headers = {
            'Authorization': f'Bearer {token_dacces}',
            'Client-Id': CLIENT_ID
        }
        user_response = requests.get(f'https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}', headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json().get('data')        
        if not user_data:
            print("Error: No se encontró el usuario.")
            return None
        user_id = user_data[0]['id']
        stream_response = requests.get(f'https://api.twitch.tv/helix/streams?user_id={user_id}', headers=headers)
        stream_response.raise_for_status()
        stream_data = stream_response.json().get('data')
        if stream_data:
            return stream_data[0]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud de API de Twitch: {e}")
    except KeyError as e:
        print(f"Error: El formato de la respuesta no es el esperado. Detalle: {e}")
        return None



