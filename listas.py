objetos_de_tienda = {
    "Perfil": [
        {"nombre": "Cambiar Aspecto", "precio": 500}
    ]
}

colores_aspectos = {
    "Capra": "#4B513D",
    "Ganymede": "#5C4764",
    "Tiran": "#7B763D",
    "Chrysid": "#7B7B74",
    "Felinor": "#ECECEC",
    "Khan": "#B84241",
    "Vesperian": "#191A1E",
    "Gremor": "#3D4B3B",
    "Canor": "#839B5C",
    "Adret": "#385E61",
    "Celtor": "#228b22",
    "Etrean": "#61C4CB",
    "Auroran": "#547CC9",
    "Lightborn": "#F0FF91",
    "Primal Vesperian": "#000000"
}

tabla_aspectos = [
    {"aspecto": "Capra", "probabilidad": 0.022},
    {"aspecto": "Ganymede", "probabilidad": 0.022},
    {"aspecto": "Tiran", "probabilidad": 0.022},
    {"aspecto": "Chrysid", "probabilidad": 0.044},
    {"aspecto": "Felinor", "probabilidad": 0.089},
    {"aspecto": "Khan", "probabilidad": 0.089},
    {"aspecto": "Vesperian", "probabilidad": 0.067},
    {"aspecto": "Gremor", "probabilidad": 0.133},
    {"aspecto": "Canor", "probabilidad": 0.156},
    {"aspecto": "Adret", "probabilidad": 0.178},
    {"aspecto": "Celtor", "probabilidad": 0.178},
    {"aspecto": "Etrean", "probabilidad": 0.178},
    {"aspecto": "Auroran", "probabilidad": 0.011},
    {"aspecto": "Lightborn", "probabilidad": 0.011},
    {"aspecto": "Primal Vesperian", "probabilidad": 0.011}
]

tabla_recompensas = [
    # Recompensas de Experiencia
    {"item": "10 <:exp:1338472338370596954>", "probabilidad": 0.20, "tipo": "Experiencia", "valor": 10},
    {"item": "25 <:exp:1338472338370596954>", "probabilidad": 0.10, "tipo": "Experiencia", "valor": 25},
    {"item": "50 <:exp:1338472338370596954>", "probabilidad": 0.05, "tipo": "Experiencia", "valor": 50},
    {"item": "100 <:exp:1338472338370596954>", "probabilidad": 0.03, "tipo": "Experiencia", "valor": 100},
    {"item": "200 <:exp:1338472338370596954>", "probabilidad": 0.01, "tipo": "Experiencia", "valor": 50},
    {"item": "500 <:exp:1338472338370596954>", "probabilidad": 0.005, "tipo": "Experiencia", "valor": 500},
    {"item": "1000 <:exp:1338472338370596954>", "probabilidad": 0.002, "tipo": "Experiencia", "valor": 1000},
    {"item": "5000 <:exp:1338472338370596954>", "probabilidad": 0.0005, "tipo": "Experiencia", "valor": 5000},
    {"item": "10000 <:exp:1338472338370596954>", "probabilidad": 0.0001, "tipo": "Experiencia", "valor": 10000},

    # Recompensas desbloqueables
    {"item": "Cambiar apodo", "probabilidad": 0.020, "tipo": "Roles"},    
    {"item": "Permisos de imagen", "probabilidad": 0.02, "tipo": "Roles"},
    {"item": "Uso de sonidos en llamada", "probabilidad": 0.01333, "tipo": "Roles"},
    {"item": "Crear hilos", "probabilidad": 0.01, "tipo": "Roles"},
    {"item": "Añadir reacciones", "probabilidad": 0.005, "tipo": "Roles"},
    {"item": "Establecer estados de voz", "probabilidad": 0.003, "tipo": "Roles"},
    {"item": "Uso de actividades", "probabilidad": 0.002, "tipo": "Roles"},
    {"item": "Emojis externos", "probabilidad": 0.001, "tipo": "Roles"},
    {"item": "Stickers externos", "probabilidad": 0.001, "tipo": "Roles"},
    {"item": "Uso de sonidos externos en llamada", "probabilidad": 0.0005, "tipo": "Roles"},
  
    # Recompensas Comunes
    {"item": "Mudskipper", "probabilidad": 0.005, "tipo": "Roles"},
    {"item": "Ciego", "probabilidad": 0.004, "tipo": "Roles"},
    {"item": "Pionero", "probabilidad": 0.003, "tipo": "Roles"},
    {"item": "Bandido", "probabilidad": 0.0026, "tipo": "Roles"},
    {"item": "Conocedor", "probabilidad": 0.0023, "tipo": "Roles"},
    {"item": "Cazador de Erisia", "probabilidad": 0.002, "tipo": "Roles"},
    {"item": "Con poca cordura", "probabilidad": 0.0018, "tipo": "Roles"},
    {"item": "Desafiador del Duke", "probabilidad": 0.0016, "tipo": "Roles"},
    {"item": "Asesino de jefes", "probabilidad": 0.0015, "tipo": "Roles"},
    {"item": "Elegido de Ferryman", "probabilidad": 0.0013, "tipo": "Roles"},
    {"item": "Maestro de juramentos", "probabilidad": 0.0011223, "tipo": "Roles"},
    
    # Recompensas Épicas
    {"item": "Habitante del Abismo", "probabilidad": 0.00110111, "tipo": "Roles"},
    {"item": "Buscador de Reliquias", "probabilidad": 0.0010121223, "tipo": "Roles"},
    {"item": "Fanático de Aelita", "probabilidad": 0.0007212, "tipo": "Roles"},
    {"item": "Viajero de los Mares", "probabilidad": 0.0006933, "tipo": "Roles"},
    {"item": "Seguidor de Lord Regent", "probabilidad": 0.00068, "tipo": "Roles"},
    {"item": "Rompejuramentos", "probabilidad": 0.0006, "tipo": "Roles"},
    {"item": "Explorador del Límite", "probabilidad": 0.0005, "tipo": "Roles"},
    {"item": "Pequeña polilla", "probabilidad": 0.00039, "tipo": "Roles"},
    {"item": "Buscado en Fort Merit", "probabilidad": 0.00032, "tipo": "Roles"},
    {"item": "Migrante de Starsweep Valley", "probabilidad": 0.00029, "tipo": "Roles"},
    {"item": "Guardian del Templo de la Luz", "probabilidad": 0.00022, "tipo": "Roles"},
    {"item": "Sabio de Greathive", "probabilidad": 0.000193, "tipo": "Roles"},
    {"item": "Pescador de la Isla", "probabilidad": 0.000171, "tipo": "Roles"},
    {"item": "Surcador del Vacio", "probabilidad": 0.00016312, "tipo": "Roles"},
    {"item": "Naufrago Perdido", "probabilidad": 0.00015312, "tipo": "Roles"},  
    
    # Recompensas Legendarias
    {"item": "Amigo de Akira", "probabilidad": 0.00007, "tipo": "Roles"},
    {"item": "Pequeño ayudante de Klaris", "probabilidad": 0.00001, "tipo": "Roles"},
    {"item": "Mente colmena", "probabilidad": 0.000005, "tipo": "Roles"},
    {"item": "Devoto de Yun'Shul", "probabilidad": 0.000003, "tipo": "Roles"},
    {"item": "Discípulo de los Antiguos", "probabilidad": 0.0000025, "tipo": "Roles"},
    {"item": "Portador del Legado", "probabilidad": 0.0000015, "tipo": "Roles"},
    {"item": "Defensor de los Perdidos", "probabilidad": 0.000001, "tipo": "Roles"},
    {"item": "Ansus Gods", "probabilidad": 0.0000006, "tipo": "Roles"},
    {"item": "Sirviente de Ethiron", "probabilidad": 0.00000051, "tipo": "Roles"},
    
    {"item": "Parte de los fragmentos", "probabilidad": 0.00000050, "tipo": "Roles"},
    {"item": "Cómo he llegado aquí?", "probabilidad": 0.00000020, "tipo": "Roles"},
    
    # Recompensas de objeto
    {"item": "Cambiar Aspecto", "probabilidad": 0.020, "tipo": "Objeto"}
]


PITY_REWARDS = [
    'Permisos de imagen', 
    'Uso de sonidos en llamada', 
    'Emojis externos', 
    'Stickers externos', 
    'Uso de sonidos externos en llamada', 
    'Cambiar apodo', 
    'Crear hilos', 
    'Añadir reacciones', 
    'Establecer estados de voz', 
    'Uso de actividades'
]
