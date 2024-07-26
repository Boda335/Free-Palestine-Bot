import discord
from discord.ext import commands, tasks
import json
import asyncio
from discord.ui import Button, View
from PIL import Image, ImageOps
import requests
from io import BytesIO
from tabulate import tabulate
with open('config.json') as f:
    config = json.load(f)
with open('channels.json') as f:
    auto_line_channels = json.load(f)
status_message_id = None
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
prefix = config['prefix']
bot = commands.Bot(command_prefix=prefix, intents=intents)
BOT_IDS = config["BOT_IDS"]
UPDATE_CHANNEL_ID = config["UPDATE_CHANNEL_ID"]
token = config['token']
FRAME_URLS = config['FRAME_URLS']
Ziker_ROLE_ID = config['Ziker_ROLE_ID']
Ziker_channel_ID = config['Ziker_channel_ID']
def load_role_ids():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config.get('color_role_ids', [])
EMBED_IMAGE_URL = "https://i.top4top.io/p_3102j2j9v0.png"
class FrameAvatarButton(Button):
    def __init__(self, label, frame_url):
        super().__init__(style=discord.ButtonStyle.green, label=label)
        self.frame_url = frame_url
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user
        avatar_url = user.display_avatar.url
        response = requests.get(avatar_url)
        avatar_image = Image.open(BytesIO(response.content)).convert("RGBA")
        response = requests.get(self.frame_url)
        frame_image = Image.open(BytesIO(response.content)).convert("RGBA")
        avatar_image = avatar_image.resize(frame_image.size)
        combined_image = Image.alpha_composite(avatar_image, frame_image)
        with BytesIO() as image_binary:
            combined_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.followup.send(file=discord.File(fp=image_binary, filename='framed_avatar.png'), ephemeral=True)
class FrameAvatarView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout to None
        for i, frame_url in enumerate(FRAME_URLS):
            self.add_item(FrameAvatarButton(label=f"Frame {i+1}", frame_url=frame_url))
@bot.command()
@commands.has_permissions(administrator=True)
async def setbtn(ctx):
    embed = discord.Embed(title="Free Palestine")
    embed.set_image(url=EMBED_IMAGE_URL)
    await ctx.send(embed=embed, view=FrameAvatarView())
    await ctx.message.delete()
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 ليس لديك صلاحيات لاستخدام هذا الأمر.")
@bot.event
async def on_ready():
    print(f'✅ | Logged in as {bot.user}')
    update_status.start()
    change_role_colors.start()
    reminder.start()
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(
            name="Color Change",
            type=discord.ActivityType.watching,
            url="https://www.twitch.tv/evo_bots?&ab_channel=evo_bots"
        )
    )
    print_status_table()
    print_commands_table()
@tasks.loop(minutes=5)
async def change_role_colors():
    role_ids = load_role_ids()
    for guild in bot.guilds:
        for role_id in role_ids:
            role = discord.utils.get(guild.roles, id=int(role_id))
            if role:
                await role.edit(color=discord.Color.random())
@tasks.loop(hours=6)
async def reminder():
    channel = bot.get_channel(Ziker_channel_ID)
    if channel:
        role = discord.utils.get(channel.guild.roles, id=Ziker_ROLE_ID)
        if role:
            embed = discord.Embed(
                title="الرسالة اليومية:",
                description="صلِّ على سيدنا محمد ﷺ :white_heart:",
                color=discord.Color.blue()
            )
            await channel.send(content=role.mention, embed=embed)
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith(f'{prefix}line'):
        # التحقق من صلاحيات المستخدم
        if message.author.guild_permissions.administrator:
            channel_id = message.channel.id
            if channel_id in auto_line_channels:
                auto_line_channels.remove(channel_id)
                embed = discord.Embed(
                    color=0xFF0000,
                    title='❌ Channel Update',
                    description='This channel has been removed from the auto line channels.'
                )
            else:
                auto_line_channels.append(channel_id)
                embed = discord.Embed(
                    color=0x00FF00,
                    title='✅ Channel Update',
                    description='This channel has been added to the auto line channels.'
                )
        await message.channel.send(embed=embed)
        await message.delete()
        with open('channels.json', 'w') as f:
            json.dump(auto_line_channels, f, indent=4)
    if message.channel.id in auto_line_channels:
        await asyncio.sleep(.5)
        await message.channel.send(content=config['imageUrl'])
    await bot.process_commands(message)
@tasks.loop(minutes=5)
async def update_status():
    channel = bot.get_channel(UPDATE_CHANNEL_ID)
    if channel:
        await send_or_update_embed(channel)
async def send_or_update_embed(channel):
    global status_message_id
    embed = discord.Embed(title="Bot Status", color=0x00ff00)
    for bot_id in BOT_IDS:
        bot_member = channel.guild.get_member(bot_id)
        if bot_member is not None:
            status = "Online <a:13:1240368672367710338>" if bot_member.status != discord.Status.offline else "Offline <a:14:1240368761085755433>"
            embed.add_field(name=f"Bot: {bot_member.name}", value=f"Status: {status}", inline=False)
        else:
            embed.add_field(name=f"Bot ID: {bot_id}", value="Status: Not Found", inline=False)
    if status_message_id:
        try:
            message = await channel.fetch_message(status_message_id)
            await message.edit(embed=embed)
        except discord.NotFound:
            message = await channel.send(embed=embed)
            status_message_id = message.id
    else:
        message = await channel.send(embed=embed)
        status_message_id = message.id
@bot.command()
async def stu(ctx):
    await send_or_update_embed(ctx.channel)
@bot.event
async def on_member_update(before, after):
    if before.id in BOT_IDS and before.status != after.status:
        channel = bot.get_channel(UPDATE_CHANNEL_ID)
        if channel:
            await send_or_update_embed(channel) 
def print_status_table():
    status_info = {
        "Change Role Colors": change_role_colors.is_running(),
        "Reminder": reminder.is_running(),
        "Update Status": update_status.is_running()
    }
    print("┌───────────────────────────────┬────────────┐")
    print("│ Feature                       │   Status   │")
    print("├───────────────────────────────┼────────────┤")
    for command, status in status_info.items():
        status_text = "✅" if status else "❌"
        print(f"│ {command.ljust(29)} │ {status_text.center(9)} │")
    print("└───────────────────────────────┴────────────┘")
def print_commands_table():
    commands_info = {
        "setbtn": True,
        "stu": True,
        "line": True
    }
    print("\n┌───────────────────────────────┬────────────┐")
    print("│ Command Name                  │   Status   │")
    print("├───────────────────────────────┼────────────┤")
    for command, status in commands_info.items():
        status_text = "✅" if status else "❌"
        print(f"│ {command.ljust(29)} │ {status_text.center(9)} │")
    print("└───────────────────────────────┴────────────┘")
    print(f'PREFIX LOAD [{prefix}]')
    print("Coded By Boda3350")
    print("https://discord.gg/DzjuTABN6E")

bot.run(token)
