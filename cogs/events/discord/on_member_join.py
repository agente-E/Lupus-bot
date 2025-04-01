import discord
import io
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
# from cogs.utils.gacha.get_user_data import *

# Create an image with the name and profile image
async def create_welcome_image(member):
    try:
        # Get the image
        try:
            background_path = 'assets/images/background.png'
            background = Image.open(background_path)
            draw = ImageDraw.Draw(background)
        except Exception as e:
            raise RuntimeError(f"Error al crear la imagen de fondo: {e}")
        try:
            # Get the font
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

async def send_welcome_dm(member):
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
                "y necesitarás <:note:1338471019702259763>**Echoes** para hacer la tirada, aunque cada usuario tiene una tirada **gratuita** cada 10 minutos.\n\n"
            ),
            inline=False
        )
        embed3 = discord.Embed(
            title="Obtener echoes",
            color=discord.Color.green()
            )
        embed3.add_field(
            name="¿Pero cómo consigo los <:note:1338471019702259763>Echoes?",
            value=(
                "Los <:note:1338471019702259763>**Echoes** son la moneda de cambio de esta comunidad, y su obtención es sencilla y gratuita: ¡Sé activo en la **Comunidad Hispana Deepwoken**! "
                "Tu número de <:note:1338471019702259763>**Echoes** aumentará al **enviar mensajes** y al **participar en llamadas**.\n\n"
            ), 
            inline=False
        )
        # Send message to the member DM
        try:
            dm_channel = await member.create_dm()
            await dm_channel.send(embed=embed1)
            await dm_channel.send(embed=embed2)
            await dm_channel.send(embed=embed3)
        except discord.Forbidden:
                print(f"No se pudieron enviar los DMs a {member.name}. El usuario tiene bloqueados los DMs.")

class OnMemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = self.bot.config.get("channels", {})["welcome"]
        self.user_rol_name = "Usuario"
        self.announcement_role_name = "Anuncios"

    # When a user joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        # Send welcome DM to the new user
        await send_welcome_dm(member=member)

        # Assing user and announcements roles to the user
        guild = member.guild

        # Finds the roles by name
        users_role = discord.utils.get(guild.roles, name=self.user_rol_name)
        announcement_role = discord.utils.get(guild.roles, name=self.announcement_role_name)
        
        # If the role exists, assign it to the user
        if users_role:
            await member.add_roles(users_role)
            print(f"Rol {self.user_rol_name} asignado a {member.name}")
        else:
            print(f"Rol {self.user_rol_name} no encontrado en el servidor.")
        if announcement_role:
            await member.add_roles(announcement_role)
            print(f"Rol {self.announcement_role_name} asignado a {member.name}")
        else:
            print(f"Rol {announcement_role} no encontrado en el servidor.")
        
        # Check if welcome channel ID is correct
        if self.welcome_channel_id is None:
            print("Canal de bienvenida no encontrado, comprueba la ID")
        else:
            welcome_channel = self.bot.get_channel(welcome_channel_id)
            welcome_image = await create_welcome_image(member)
            await welcome_channel.send(file=discord.File(welcome_image, filename='welcome.png'))
        
        # # Get data from the user in case that it exists TODO
        # user_data = get_user_data(str(member.id))
        # # Assign the aspect role to the user
        # aspect = user_data['aspecto']
        # aspect_role = discord.utils.get(guild.roles, name=aspect)
        # if aspect_role:
        #     await member.add_roles(aspect_role)
        # # Check if the user has roles in its profile
        # obtained_roles = user_data.get('roles_obtenidos', [])
        # # Assing obtained roles
        # if obtained_roles:
        #     roles = []
        #     for role_name in obtained_roles:
        #         # Search the role in the server
        #         role = discord.utils.get(member.guild.roles, name=role_name)
        #         if role:
        #             roles.append(role)
        #     # If founds roles, assing them to the user
        #     if roles:
        #         await member.add_roles(*roles)
        #         print(f"Se asignaron los roles a {member.name}: {', '.join(role.name for role in roles)}")
        #     else:
        #         print("El usuario no tiene roles asignados")
        # except Exception as e:
        #     print(f"Error en on_member_join: {e} ayaha")

async def setup(bot):   
    await bot.add_cog(OnMemberJoin(bot))