import discord
from cogs.utils.discord.create_welcome_image import CreateWelcomeImage
from cogs.utils.gacha.get_user_data import getUserData
from discord.ext import commands

class onMemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_user_data_cog = getUserData(bot)

    # When a user joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Create welcome embed for MD
        embed1 = discord.Embed(
            title="¡Bienvenido al servidor!",
            description=f"¡Hola {member.mention}! Estamos encantados de que te hayas unido a nuestra comunidad. Aquí tienes una guía para empezar:",
            color=discord.Color.green()
            )
        embed1.add_field(
            name="1️⃣ Reglas del servidor",
            value="Lee nuestras reglas para asegurarte de que todos creamos un buen lugar de convivencia. https://discord.com/channels/776247434384375818/777160475158511627",
            inline=False
        )
        embed1.add_field(
            name="2️⃣ Presentación",
            value="¡Nos encantaría conocerte! No dudes en presentarte con la comunidad y encontrar a tu grupo de juego.",
            inline=False
        )
        embed1.add_field(
            name="3️⃣ Comandos útiles",
            value="Usa el comando `/roll` para realizar tiradas y obtener recompensas, desde experiencia, permisos en el servidor y roles de decoración.",
            inline=False
        )
        embed1.add_field(
            name="4️⃣ Preguntas",
            value="Si tienes alguna pregunta, no dudes en preguntar en el canal de ayuda o contactar con el soporte usando tickets.",
            inline=False
        )
        embed1.add_field(
            name="5️⃣ Invitación",
            value=(
                "Si quieres invitar a alguien al servidor, tienes un enlace en el canal:\n"
                "https://discord.com/channels/776247434384375818/860630677489319936"
            ),
            inline=False
        )
        embed2 = discord.Embed(
            title="¿🔧 Cómo funciona el servidor?",
            color=discord.Color.green()
            )
        embed2.add_field(
            name="Explicación:",
            value=(
                "En el mismo momento en el que te unes al **servidor**, tendrás acceso a los canales de texto y voz que presentamos, "
                "cada uno con su tópico específico. Esta comunidad cuenta con una **mecánica propia** para obtener diversas acciones, "
                "como el uso del **panel de sonidos** en las llamadas o **enviar imágenes** por los canales correspondientes.\n\n"
                "El proceso para conseguir estos **beneficios** se realiza mediante un **GACHAPON**, creado específicamente para el servidor. "
                "Para usarlo, deberás realizar el comando `/roll` en el canal "
                "[correspondiente](https://discord.com/channels/776247434384375818/1312478372357603399) "
                "y necesitarás **Echoes** para hacer la tirada, aunque cada usuario tiene una tirada **gratuita** cada 10 minutos.\n\n"
                "¿Pero cómo consigo los Echoes?\n\n"
                "Los **Echoes** son la moneda de cambio de esta comunidad, y su obtención es sencilla y gratuita: ¡Sé activo en la **Comunidad Hispana Deepwoken**! "
                "Tu número de **Echoes** aumentará al **enviar mensajes** y al **participar en llamadas**.\n\n"
            ),
            inline=False
        )
        # Send message to the member DM
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(embed=embed1)
            await dm_channel.send(embed=embed2)
        except discord.Forbidden:
            print(f"No se pudieron enviar los DMs a {member.name}. El usuario tiene bloqueados los DMs.")
        try:
            # Assign the User role to the user
            rol_name = "Usuario"
            announcement_role = "Anuncios"
            guild = member.guild
            # Search the role with the name
            role = discord.utils.get(guild.roles, name=rol_name)
            role2 = discord.utils.get(guild.roles, name=announcement_role)
            # If the role exists, assign it to the member
            if role:
                await member.add_roles(role)
                print(f"Rol {rol_name} asignado a {member.name}")
            else:
                print(f"Rol {rol_name} no encontrado en el servidor.")
            if role2:
                await member.add_roles(role2)
                print(f"Rol {announcement_role} asignado a {member.name}")
            else:
                print(f"Rol {announcement_role} no encontrado en el servidor.")
            
            # Get welcome channel
            channel = self.bot.get_channel(self.bot.config["channels"].get("welcome"))
            if channel is None:
                raise ValueError("Canal de bienvenida no encontrado")
            # Create welcome image
            try:
                welcome_image = await CreateWelcomeImage.create_welcome_image(self, member)
                await channel.send(file=discord.File(welcome_image, filename='welcome.png'))
            except:
                print("Error creating welcome image")
            
            # Now, get user data and assign roles if available
            user_id = str(member.id)
            user_data = self.get_user_data_cog.get_user_data(user_id)
            if user_data is not None:
                # Check if the user has roles defined in their data
                obtained_roles = user_data.get('Roles', "").split(", ")
                print(obtained_roles)
                if obtained_roles:
                    roles = []
                    for role_name in obtained_roles:
                        # Search the roles in the server
                        role = discord.utils.get(member.guild.roles, name=role_name)
                        if role:
                            roles.append(role)
                    if roles:
                        await member.add_roles(*roles)
                        print(f"Se asignaron los roles a {member.name}: {', '.join(role.name for role in roles)}")
                else:
                    print("El usuario no tiene roles asignados")
        except Exception as e:
            print(f"Error en on_member_join: {e} ayaha")

async def setup(bot):   
    await bot.add_cog(onMemberJoin(bot))