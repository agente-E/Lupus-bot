import discord
from discord.ext import commands

class ComandoRecompensas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Guardamos la instancia del bot
    # Comando para mostrar las recompensas en un embed
    @discord.app_commands.command(name="recompensas", description="Muestra la tabla de recompensas y sus probabilidades.")
    async def recompensas(interaction: discord.Interaction):
        # Agrupar las recompensas por tipo
        categorias = {}
        for recompensa in tabla_recompensas:
            tipo = recompensa["tipo"]
            if tipo not in categorias:
                categorias[tipo] = []
            categorias[tipo].append(recompensa)
        
        # Crear el embed
        embed = discord.Embed(
            title="🎉 **Tabla de Recompensas y Probabilidades** 🎉",
            description="Aquí tienes las recompensas disponibles y sus probabilidades:",
            color=discord.Color.blue()
        )
        
        # Añadir las recompensas al embed, organizadas por tipo
        for tipo, recompensas in categorias.items():
            # Añadir el título de la categoría
            embed.add_field(name=f"**__{tipo}__**", value="", inline=False)
            
            # Añadir las recompensas de cada tipo
            for recompensa in recompensas:
                item = recompensa["item"]
                probabilidad = recompensa["probabilidad"]
                tiradas = round(1 / probabilidad)  # Redondear el número de tiradas
                embed.add_field(
                    name=f"**{item}**",
                    value=f"1 entre {tiradas} tiradas",
                    inline=False
                )

        # Enviar el embed al canal
        await interaction.response.send_message(embed=embed)

# Función de configuración para cargar el cog
async def setup(bot):
    await bot.add_cog(ComandoRecompensas(bot))