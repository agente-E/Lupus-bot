import discord
import io
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from cogs.utils.gacha.interact_with_data import InteractWithDatabase

class OnMemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = self.bot.config.get("channels", {})["welcome"]
        self.user_rol = self.bot.config.get("role", {})["user"]
        self.announcement_role = self.bot.config.get("role", {})["announcement"]

    '''When a user joins the server'''
    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        # Send welcome DM to the new user
        await send_welcome_dm(member=member)

        # Assing user and announcements roles to the user
        guild = member.guild

        # Fetch roles by ID
        users_role = guild.get_role(self.user_role_id)
        announcement_role = guild.get_role(self.announcement_role_id)
        
        # Assign roles if they exist
        if users_role:
            await member.add_roles(users_role)
            print(f"Rol {users_role.name} asignado a {member.name}")
        else:
            print(f"Rol con ID {self.user_role_id} no encontrado en el servidor.")
        
        if announcement_role:
            await member.add_roles(announcement_role)
            print(f"Rol {announcement_role.name} asignado a {member.name}")
        else:
            print(f"Rol con ID {self.announcement_role_id} no encontrado en el servidor.")
        
        # Check if welcome channel ID is correct
        if self.welcome_channel_id is None:
            print("Canal de bienvenida no encontrado, comprueba la ID.")
        else:
            welcome_channel = self.bot.get_channel(self.welcome_channel_id)
            welcome_image = await self.create_welcome_image(member)
            await welcome_channel.send(file=discord.File(welcome_image, filename='welcome.png'))
        
        database = self.bot.get_cog("InteractWithDatabase") # type: InteractWithDatabase

        # Create user object
        user_data = await database.get_user_data(user_id=member.id)

        # Get what aspect did get
        aspect = user_data['aspecto']
        
        # Get the role by name (I'm sorry, not doing this by id)
        aspect_role = discord.utils.get(guild.roles, name=aspect)
        
        # Assign if exists
        if aspect_role:
            await member.add_roles(aspect_role)

        # Check if the user has roles in its profile
        obtained_roles = user_data['unlocks']

        # Assing obtained roles
        if obtained_roles:
            roles = []
            for role_name in obtained_roles:
                
                # Search the role in the server
                role = discord.utils.get(member.guild.roles, name=role_name)
                if role:
                    roles.append(role)
            
            # If founds roles, assing them to the user # TODO REWORK, DO IT AS TITLES
            if roles:
                await member.add_roles(*roles)
                print(f"Se asignaron los roles a {member.name}: {', '.join(role.name for role in roles)}")
            else:
                print("El usuario no tiene roles asignados")

'''Create welcome image with the user pfp and name, in case of null, use default'''
async def create_welcome_image(member):
    try:
        
        # Get the image
        try:
            background_path = 'assets/images/background.png'
            background = Image.open(background_path)
            draw = ImageDraw.Draw(background)
        except Exception as e:
            raise RuntimeError(f"Error al crear la imagen de fondo: {e}")
        
        # Get the font
        try:
            font_path = 'assets/fonts/Fondamento-Regular.ttf'
            font_size = 75
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print("Fuente no encontrada, usando una fuente por defecto.")
            font = ImageFont.load_default()
        except Exception as e:
            raise RuntimeError(f"Error al cargar la fuente: {e}")
        
        # Write the texts on the image
        try:
            welcome_text = f"{member.name}!"
            sub_text = "¡Bienvenido/a al servidor!"
            text_bbox = draw.textbbox((0,0), welcome_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x1 = (background.width - text_width) // 2
            text_y1 = 450
            text_x2 = 205
            text_y2 = 535
            color = (113, 102, 87, 255)
            draw.text((text_x1, text_y1), welcome_text, fill=color, font=font)
            draw.text((text_x2, text_y2), sub_text, fill=color, font=font)
        except Exception as e:
            raise RuntimeError(f"Error al escribir texto en la imagen: {e}")
        
        # Get the image of the user
        try:
            profile_pic = await member.avatar.read()
            profile_image = Image.open(io.BytesIO(profile_pic)).resize((350, 350))
            mask = Image.new('L', profile_image.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, profile_image.size[0], profile_image.size[1]), fill=255)
            profile_image.putalpha(mask)
        
        # In case that the avatar is null, use a default one instead
        except AttributeError:
            print(f"{member.name} no tiene avatar, usando imagen predeterminada.")
            profile_image = Image.open('assets/images/defaultAvatar.png').resize((350, 350)).convert("RGBA")
            mask = Image.new('L', profile_image.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, profile_image.size[0], profile_image.size[1]), fill=255)
            profile_image.putalpha(mask)
        except Exception as e:
            raise RuntimeError(f"Error al procesar la imagen de perfil: {e}")
        
        # Paste the avatar on the background
        try:
            profile_x = 430
            profile_y = 100
            background.paste(profile_image, (profile_x, profile_y), profile_image)
        except Exception as e:
            raise RuntimeError(f"Error al pegar la imagen de perfil en el fondo: {e}")
        
        # Save the new image 
        try:
            image_bytes = io.BytesIO()
            background.save(image_bytes, format='PNG')
            image_bytes.seek(0)
        except Exception as e:
            raise RuntimeError(f"Error al guardar la imagen en buffer: {e}")
        
        # Open the new created image
        try:
            with open('assets/images/WelcomeDebug.png', 'wb') as f:
                f.write(image_bytes.getbuffer())
        except Exception as e:
            raise RuntimeError(f"Error al guardar la imagen de depuración: {e}")
        return image_bytes
    except Exception as e:
        print(f"Error en create_welcome_image: {e}")
        return None

"""Sends welcome message to the new user"""
async def send_welcome_dm(member):
    embeds = [
        discord.Embed(
            title="¡Bienvenido al servidor!",
            description=(
                f"¡Hola {member.mention}! Estamos encantados de que te hayas unido a nuestra comunidad. "
                "Aquí tienes una guía para empezar:"
            ),
            color=discord.Color.green()
        ).add_field(
            name="1️⃣ Reglas del servidor",
            value="Lee nuestras reglas aquí: https://discord.com/channels/776247434384375818/777160475158511627",
            inline=False
        ).add_field(
            name="2️⃣ Presentación",
            value="¡Nos encantaría conocerte! Preséntate con la comunidad y encuentra tu grupo de juego.",
            inline=False
        ).add_field(
            name="3️⃣ Comandos útiles",
            value="Usa `/roll` para obtener recompensas, experiencia, permisos y roles de decoración.",
            inline=False
        ).add_field(
            name="4️⃣ Preguntas",
            value="Si tienes dudas, pregunta en el canal de ayuda o usa tickets para soporte.",
            inline=False
        ).add_field(
            name="5️⃣ Invitación",
            value="Invita a otros con este enlace: https://discord.com/channels/776247434384375818/860630677489319936",
            inline=False
        ),
        
        discord.Embed(
            title="¿🔧 Cómo funciona el servidor?",
            color=discord.Color.green()
        ).add_field(
            name="Explicación:",
            value=(
                "Al unirte al servidor, accedes a canales de texto y voz con distintos temas. "
                "Nuestra comunidad tiene una mecánica propia para obtener ventajas, como el uso del **panel de sonidos** "
                "o **enviar imágenes** en canales específicos. 🎲✨\n\n"
                "El sistema de recompensas se basa en un **GACHAPON**, al que puedes acceder con `/roll` en el "
                "[canal correspondiente](https://discord.com/channels/776247434384375818/1312478372357603399). "
                "Necesitas <:note:1338471019702259763>**Notas**, aunque tienes una tirada **gratuita** cada 10 minutos."
            ),
            inline=False
        ),
        
        discord.Embed(
            title="Obtener Notas",
            color=discord.Color.green()
        ).add_field(
            name="¿Cómo consigo <:note:1338471019702259763>Notas?",
            value=(
                "Los <:note:1338471019702259763>**Notas** son la moneda del servidor y se consiguen fácilmente: "
                "¡Sé activo en la **Comunidad Hispana Deepwoken**! Gana <:note:1338471019702259763> enviando mensajes y "
                "participando en llamadas. 📢💬"
            ),
            inline=False
        )
    ]
    
    # Send the embeds to the user DM
    try:
        dm_channel = await member.create_dm()
        for embed in embeds:
            await dm_channel.send(embed=embed)
    except discord.Forbidden:
        print(f"No se pudieron enviar los DMs a {member.name}. El usuario tiene bloqueados los DMs.")

async def setup(bot):   
    await bot.add_cog(OnMemberJoin(bot))