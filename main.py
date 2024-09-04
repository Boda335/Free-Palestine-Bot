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
    bot.add_view(CustomView())
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
            status = "Online <a:yes:1276899279327203451>" if bot_member.status != discord.Status.offline else "Offline <a:no:1276899284289323009>"
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
    await ctx.message.delete()
    
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
    
    
class CustomView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # عدم تحديد توقيت لانتهاء صلاحية الزر

    @discord.ui.button(label="Server Channel", style=discord.ButtonStyle.primary, custom_id="button1")
    async def button1_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed_response = discord.Embed(title="**رومات السيرفر**",color=0xae2fef)
        embed_response.add_field(name="<#1276897170133483590>", value="**قوانين السيرفر التي يجب عليك إتباعها لتجنب العقوبات**", inline=False)
        embed_response.add_field(name="<#1277584362971467847>", value="**تعرف من خلاله جديد السيرفر من فعاليات او تحديثات **", inline=False)
        embed_response.add_field(name="<#1276897178085883935>", value="**اعرف الرتب الي موجودة وممكن تستعملها ازاي**", inline=False)
        embed_response.add_field(name="<#1276897184020697249>", value="**تقدر تاخد منها رتب اهتماماتك زي الالعاب وبرامج الديزاين والفعاليات وكدا**", inline=False)
        embed_response.add_field(name="<#1276897184775802893>", value="**روم يظهر الذين دعموا السيرفر ببوست**", inline=False)
        embed_response.add_field(name="<#1276897163229532221>", value="**روم يمكنك التواصل مع الدعم الفني بخصوص شيء ما في السيرفر (شكوة ، إقتراح ، إعتراض بأسلوب لائق ....)**", inline=False)
        embed_response.add_field(name="<#1276897190916395122>", value="**روم جيف اواي بنعمل فيها جيفاويات على جوايز كتير**", inline=False)
        embed_response.add_field(name="<#1276897191809781891>", value="**الشات العام تقدر تتكلم مع الناس هنا**", inline=False)
        embed_response.add_field(name="<#1276897198151307367>", value="**الشات المخصص للغات الاخرى غير العربية زي الانجليزي وغيرها**", inline=False)
        embed_response.add_field(name="<#1276897199254409348>", value="**روم اقتباسات وكدا**", inline=False)
        embed_response.add_field(name="<#1276897205126697082>", value="**روم بينزل فيها اخر اخبار الالعاب والعروض المجانية**", inline=False)
        embed_response.add_field(name="<#1276897206443577384>", value="**روم الميمز والضحك وكدا**", inline=False)
        embed_response.add_field(name="<#1276897212324118548>", value="**روم تقدر تنزل فيها سكرين شوت لحاجة عجبتك **", inline=False)
        embed_response.add_field(name="<#1276897213322363043>", value="**لو عندك تصميم فيديو اوي اي فيديو عموما تقدر تنزله هنا**", inline=False)
        embed_response.add_field(name="<#1276897219114565634>", value="**تقدر هنا تستعمل اوامر البوت**", inline=False)
        embed_response.add_field(name="<#1276897228144775279>", value="**روم العد ملهاش هدف بس لي لا**", inline=False)
        embed_response.add_field(name="<#1276897230145458259>", value="**لو عندك اقتراح او فكرة للسيرفر او اي حاجة اكتبها هنا**", inline=False)
        embed_response.add_field(name="<#1276897236403490846>", value="**هنا تقدر تجيب تيم للعبة الي بتحبها مع العدد الي نفسك فيه **", inline=False)
        embed_response.set_image(url="https://c.top4top.io/p_3165o81qx2.png")
        embed_response.set_thumbnail(url="https://cdn.discordapp.com/attachments/1276923904392298599/1279402951663947871/logo.png?ex=66d45059&is=66d2fed9&hm=64b4f9259c102bda7b3a22f1d2322e582a41ea8d994be2908e51b398912b2e75&")
        await interaction.response.send_message(embed=embed_response, ephemeral=True)

    @discord.ui.button(label="Server Role", style=discord.ButtonStyle.secondary, custom_id="button2")
    async def button2_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed_response = discord.Embed(title="**رتب السيرفر**",description="**رتب التفاعل **\n\n "
                                       "<@&1276897177297227877> = \n **لفل كتابي 5 **\n **لفل صوتي 5** \n\n"
                                       "<@&1276897176496246865> = \n**لفل كتابي 10** \n **لفل كتابي 10** \n\n"
                                       "<@&1276897175690940457> = \n**لفل كتابي 15** \n **لفل كتابي 15** \n\n"
                                       "<@&1276897174927441992> = \n**لفل كتابي 25** \n **لفل كتابي 25**  \n\n"
                                       "<@&1276897174210220125> = \n**لفل كتابي 35** \n **لفل كتابي 35**\n\n"
                                       "<@&1276897173186809858> = \n**لفل كتابي 45** \n **لفل كتابي 45**\n\n"
                                       "<@&1276897172712984647> = \n**لفل كتابي 55** \n **لفل كتابي 55**\n\n"
                                       "<@&1276897171844759676> = \n**لفل كتابي 65** \n **لفل كتابي 65**\n\n"
                                       "<@&1276897171043782676> = \n**لفل كتابي 75** \n **لفل كتابي 75**\n\n"
                                       "<@&1276897170175557775> = \n**لفل كتابي 100** \n **لفل كتابي 100**\n\n"
                                       
                                       "**رتب الالعاب**\n\n"
                                       "<@&1276897192526741524>\n\n"
                                       "<@&1276897193445294161>\n\n"
                                       "<@&1276897194376560711>\n\n"
                                       "<@&1276897195211358229>\n\n"
                                       "<@&1276897196121526445>\n\n"
                                       "<@&1276897197237207041>\n\n"
                                       "<@&1276897197840924673>\n\n"
                                       "<@&1276897204531101797>\n\n"
                                       "<@&1276897205516763146>\n\n"
                                       "<@&1276897206166880270>\n\n"
                                       "<@&1276897207144157325>\n\n"
                                       "<@&1276897208247259227>\n\n"
                                       "<@&1276897209526255767>\n\n"
                                       "<@&1276897210415448149>\n\n"
                                       "<@&1276897211267022942>\n\n"
                                       "<@&1276897212370255964>\n\n"
                                       
                                       "**رتب التصاميم**\n\n"
                                       "<@&1277588600308891681>\n\n"
                                       "<@&1277588716411682856>\n\n"
                                       "<@&1277588856635523072>\n\n"
                                       "<@&1277589163549397072>\n\n"
                                       "<@&1277588837845176473>\n\n"
                                       "<@&1277588747520573541>\n\n"
                                       "<@&1277588887937617953>\n\n"
                                       
                                       ,color=0xae2fef)
        embed_response.set_image(url="https://b.top4top.io/p_3165ijmkb1.png")
        embed_response.set_thumbnail(url="https://cdn.discordapp.com/attachments/1276923904392298599/1279402951663947871/logo.png?ex=66d45059&is=66d2fed9&hm=64b4f9259c102bda7b3a22f1d2322e582a41ea8d994be2908e51b398912b2e75&")
        await interaction.response.send_message(embed=embed_response, ephemeral=True)


@bot.command()
async def map(ctx):
    embed = discord.Embed(title="**خريطة السيرفر**", description="**نرجوا من كل الأعضاء قراءة خريطة السيرفر و خاصة الجدد سواءا رومات أو رتب لمعرفة كل ما يخص السيرفر و نيل أحسن تجربة فيه**",color=0xae2fef)
    embed.set_image(url="https://d.top4top.io/p_3165msh9p3.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1276923904392298599/1279402951663947871/logo.png?ex=66d45059&is=66d2fed9&hm=64b4f9259c102bda7b3a22f1d2322e582a41ea8d994be2908e51b398912b2e75&")
    await ctx.send(embed=embed, view=CustomView())
    await ctx.message.delete()    
bot.run(token)
