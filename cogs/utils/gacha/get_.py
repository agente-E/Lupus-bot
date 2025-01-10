# Función para formatear el porcentaje de la probabilidad
def get_percent_string(weight) -> str:
    return (f"{weight * 100:.2f}" if weight * 100 >= 1 else f"{weight * 100:.7f}").rstrip('0').rstrip('.')