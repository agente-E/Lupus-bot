import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io

class CreateWelcomeImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Crear imagen con su nombre e imagen de perfil
    async def create_welcome_image(self, member):
        try:
            try:
                background_path = 'assets/images/background.png'
                background = Image.open(background_path)
                draw = ImageDraw.Draw(background)
            except Exception as e:
                raise RuntimeError(f"Error al crear la imagen de fondo: {e}")
            try:
                font_path = 'assets/fonts/Fondamento-Regular.ttf'
                font_size = 75
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                print("Fuente no encontrada, usando una fuente por defecto.")
                font = ImageFont.load_default()
            except Exception as e:
                raise RuntimeError(f"Error al cargar la fuente: {e}")
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
            try:
                profile_pic = await member.avatar.read()
                profile_image = Image.open(io.BytesIO(profile_pic)).resize((350, 350))
                mask = Image.new('L', profile_image.size, 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0, profile_image.size[0], profile_image.size[1]), fill=255)
                profile_image.putalpha(mask)
            except AttributeError:
                print(f"{member.name} no tiene avatar, usando imagen predeterminada.")
                profile_image = Image.open('assets/images/  default_avatar.png').resize((350, 350))
                mask = Image.new('L', profile_image.size, 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0, profile_image.size[0], profile_image.size[1]), fill=255)
                profile_image.putalpha(mask)
            except Exception as e:
                raise RuntimeError(f"Error al procesar la imagen de perfil: {e}")
            try:
                profile_x = 430
                profile_y = 100
                background.paste(profile_image, (profile_x, profile_y), profile_image)
            except Exception as e:
                raise RuntimeError(f"Error al pegar la imagen de perfil en el fondo: {e}")
            try:
                image_bytes = io.BytesIO()
                background.save(image_bytes, format='PNG')
                image_bytes.seek(0)
            except Exception as e:
                raise RuntimeError(f"Error al guardar la imagen en buffer: {e}")
            try:
                with open('assets/images/welcome_debug.png', 'wb') as f:
                    f.write(image_bytes.getbuffer())
            except Exception as e:
                raise RuntimeError(f"Error al guardar la imagen de depuración: {e}")
            return image_bytes
        except Exception as e:
            print(f"Error en create_welcome_image: {e}")
            return None

# Setup the cog for the bot
async def setup(bot):
    await bot.add_cog(CreateWelcomeImage(bot))