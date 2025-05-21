# TODO

import discord
from discord.ext import commands

def obtener_color_por_probabilidad(probabilidad):
    if probabilidad <= 0.00007:
        return discord.Color.red()
    elif probabilidad <= 0.00032:
        return discord.Color.gold()
    elif probabilidad <= 0.00110111:
        return discord.Color.purple()
    elif probabilidad <= 0.0016:
        return discord.Color.blue()  
    else:
        return discord.Color.green()
    
    
