    # Obtener un token para hacer request a twitch 
    def get_token():
        global token_dacces, token_expiry
        try:
            auth_response = requests.post(
                'https://id.twitch.tv/oauth2/token',
                params={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'grant_type': 'client_credentials'
                }
            )
            auth_response.raise_for_status()
            data = auth_response.json()
            token_dacces = data['access_token']
            token_expiry = time.time() + data['expires_in']
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener el token de acceso: {e}")
        except KeyError as e:
            print(f"Error: El formato de la respuesta de autenticación no es el esperado. Detalle: {e}")
