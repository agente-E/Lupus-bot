# Determinar el color del embed según la rareza
def get_color(probabilidad):
    if probabilidad <= 0.0002:  # 1 en 5,000 o más rara
        return discord.Color.red()  # Rojo
    elif probabilidad <= 0.00067:  # 1 en 1,111 o más rara (Muy rara)
        return discord.Color.gold()  # Dorado
    elif probabilidad <= 0.001:  # 1 en 1,000 o más rara (Rara)
        return discord.Color.purple()  # Morado
    elif probabilidad <= 0.002:  # 1 en 500 o más rara (Poco común)
        return discord.Color.blue()  # Azul
    else:  # Más común que 1 en 500
        return discord.Color.green()  # Verde