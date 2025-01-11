import discord
from cogs.utils.discord.create_welcome_image import CreateWelcomeImage
from cogs.utils.gacha.get_user_data import getUserData
from discord.ext import commands

class onMemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_user_data_cog = getUserData(bot)  # Instantiate the cog here

    # When a user joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Create welcome embed for MD
        embed = discord.Embed(
            title="¡Bienvenido al servidor!",
            description=f"¡Hola {member.mention}! Estamos encantados de que te hayas unido a nuestra comunidad. Aquí tienes una guía para empezar:",
            color=discord.Color.green()
            )
        embed.add_field(
            name="1️⃣ Reglas del servidor",
            value="Lee nuestras reglas para asegurarte de que todos creamos un buen lugar de convivencia. https://discord.com/channels/776247434384375818/777160475158511627",
            inline=False
        )
        embed.add_field(
            name="2️⃣ Presentación",
            value="¡Nos encantaría conocerte! No dudes en hablar con la comunidad por sus canales correspondidos.",
            inline=False
        )
        embed.add_field(
            name="3️⃣ Comandos útiles",
            value="Usa el comando `/roll` para realizar tiradas y obtener recompensas, desde experiencia, permisos en el servidor y roles de decoración.",
            inline=False
        )
        embed.add_field(
            name="4️⃣ Preguntas",
            value="Si tienes alguna pregunta, no dudes en preguntar en el canal de ayuda o contactar a alguno de los helpers.",
            inline=False
        )
        embed.add_field(
            name="5️⃣ Invitación",
            value=(
                "Si quieres invitar a alguien al servidor, puedes copiarlo en el canal:\n"
                "https://discord.com/channels/776247434384375818/860630677489319936"
            ),
            inline=False
        )
        embed.add_field(
        name="🔧 ¿Cómo funciona el servidor?",
        value=(
            "Cada canal tiene una función específica y estará disponible desde el momento en que entres al servidor. "
            "El servidor cuenta con su propia mecánica para ciertas acciones, como enviar imágenes, usar sonidos en llamadas y realizar tiradas. "
            "Para hacer una tirada, deberás usar el comando `/roll`. Puedes hacer una tirada gratis cada 10 minutos, "
            "pero si necesitas más, puedes gastar *echoes* para realizar tiradas adicionales.\n\n"
            
            "*¿Cómo consigo echoes?*\n"
            "Fácil: siendo activo en el servidor. "
            "Obtendrás *echoes* de manera pasiva al enviar mensajes cada minuto y al pasar tiempo en llamadas de voz. "
            "Además, ganarás experiencia, que por ahora no tiene otro uso más que mostrar tu nivel de actividad en la comunidad."
        ),
        inline=False
        )
        # Send message to the member DM
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(embed=embed)
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
                print("NU huh")
            # Now, get user data and assign roles if available
            user_id = str(member.id)
            user_data = self.get_user_data_cog.get_user_data(user_id)

            # Check if the user has roles defined in their data
            if isinstance(user_data, dict):
                obtained_roles = user_data.get('Roles', "").split(", ")
            else:
                print(f"Error: {user_data}")  # This will give details of the error, if any
                obtained_roles = []  # Initialize obtained_roles to avoid UnboundLocalError

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

        except Exception as e:
            print(f"Error en on_member_join: {e}")

async def setup(bot):   
    await bot.add_cog(onMemberJoin(bot))