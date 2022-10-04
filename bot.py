# Imports
import discord
import wavelink
import datetime
import colorama
import urllib.request
import requests
import json
import time
import datetime
import asyncio
import Cybernator
import os
import sys

# From imports
from discord import member
from config import settings
from colorama import Fore, Back
from discord.ext import commands
from Cybernator import Paginator as pag
from discord_components import Button, Select, SelectOption, ComponentsBot, interaction
from discord_components.component import ButtonStyle
from os import system
from pystyle import Colors, Colorate, Center, Box

# Variables
color_a = Fore.CYAN + '[*] ' + Fore.WHITE
color_b = Fore.LIGHTGREEN_EX + '[+] ' + Fore.WHITE
color_c = Fore.LIGHTRED_EX + '[-] ' + Fore.WHITE
color_d = Fore.LIGHTYELLOW_EX
color_e = Fore.WHITE
id_ticket_category = 969198443820118056
id_channel_ticket_logs = 971816187199639572
id_staff_role = 810402478624735252

# Bot
prefix = settings['prefix']
client = ComponentsBot(f'{prefix}', help_command = None)
client.remove_command('help')

# Main music function
class CustomPlayer(wavelink.Player):
    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()

# Main bot function
@client.event
async def on_ready():
	ComponentsBot(client)
	members = 0
	for guild in client.guilds:
	    members += guild.member_count - 1
	system('clear')
	client.loop.create_task(connect_nodes())
	print("""
OK
""")
	while True:
		await client.change_presence(status = discord.Status.idle, activity = discord.Game('MixLands'))
		await asyncio.sleep(5)
		await client.change_presence(status = discord.Status.idle, activity = discord.Game('!help - справка'))
		await asyncio.sleep(5)

# On command error
@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		emb = discord.Embed(title = 'Команда не найдена', description = """
			Такой команды не существует.
			Введите команду **!помощь** для получения справки.
			""", colour = discord.Color.red())
		await ctx.send(embed = emb)
		print(color_c + "Пользователь " + Fore.LIGHTYELLOW_EX + str(ctx.author) + Fore.WHITE + " ввёл неверную команду.")
	if isinstance(error, commands.MissingRequiredArgument):
		emb = discord.Embed(title = 'Неверный аргумент', description = """
			Вы ввели неверные аргументы.
			Введите команду **!помощь** для получения справки.
			""", colour = discord.Color.gold())
		await ctx.send(embed = emb)
		print(color_c + "Пользователь " + Fore.LIGHTYELLOW_EX + str(ctx.author) + Fore.WHITE + " ввёл неверный аргумент.")
	if isinstance(error, commands.MissingPermissions):
		emb = discord.Embed(title = 'Нет прав', description = """
			У вас нет доступа к этой команде.
			Введите команду **!помощь** для получения справки.
			""", colour = discord.Color.gold())
		await ctx.send(embed = emb)
		print(color_c + "Пользователь " + Fore.LIGHTYELLOW_EX + str(ctx.author) + Fore.WHITE + " ввёл команду без прав.")

# Create voice function
@client.event
async def on_voice_state_update(member, before, after):
    if after.channel != None:
        if after.channel.id == 1007165033958101054:
            category = after.channel.category
            
            channel2 = await member.guild.create_voice_channel(
                name = f'🕒・{member.display_name}', 
                category = category
            )
            
            await channel2.set_permissions(member, connect = True, manage_channels = True)
            await member.move_to(channel2)

            def check(x, y, z): return len(channel2.members) == 0
            
            await client.wait_for('voice_state_update', check = check)
            await channel2.delete()

# Clear command
@client.command(aliases = ['очистить', 'очистка'], pass_context = True)
@commands.has_role(810402478624735252)
async def clear(ctx, amount : int):
	await ctx.channel.purge(limit = amount)
	emb = discord.Embed(title = 'Очистка', description = f"""
Очищено {amount} сообщений!
		""", colour = discord.Color.green())
	await ctx.send(embed = emb)

# Node connection (CHECK application.yml)
async def connect_nodes():
    await client.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=client,
        host='0.0.0.0',
        port=2333,
        password='YOUR_PASSWORD'
    )
@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f'Нода: <{node.identifier}> успешно запущена!')
@client.event
async def on_wavelink_track_end(player: CustomPlayer, track: wavelink.Track, reason):
    if not player.queue.is_empty:
        next_track = player.queue.get()
        await player.play(next_track)
@client.command()
async def connect(ctx):
    vc = ctx.voice_client
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        return await ctx.send("Пожалуйста, зайдите в голосовой канал.")
    if not vc:
        await ctx.author.voice.channel.connect(cls=CustomPlayer())
    else:
        await ctx.send("Бот уже проигрывает музыку в голосовом канале.")
@client.command()
async def stop(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")
@client.command()
async def play(ctx, *, search: wavelink.YouTubeTrack):
    vc = ctx.voice_client
    if not vc:
        custom_player = CustomPlayer()
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
    if vc.is_playing():
        vc.queue.put(item=search)
        await ctx.send(embed=discord.Embed(
            title=search.title,
            url=search.uri,
            author=ctx.author,
            description=f"В очереди `{search.title}` в канале `{vc.channel}`",
			colour = discord.Color.gold()
        ))
    else:
        await vc.play(search)
        await ctx.send(embed=discord.Embed(
            title=vc.source.title,
            url=vc.source.uri,
            author=ctx.author,
            description=f"Играет `{vc.source.title}` в канале `{vc.channel}`",
			colour = discord.Color.green()
        ))
@client.command()
async def skip(ctx):
    vc = ctx.voice_client
    if vc:
        if not vc.is_playing():
            return await ctx.send("Ничего не проигрывается.")
        if vc.queue.is_empty:
            return await vc.stop()

        await vc.seek(vc.track.length * 1000)
        if vc.is_paused():
            await vc.resume()
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")
@client.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc:
        if vc.is_playing() and not vc.is_paused():
            await vc.pause()
        else:
            await ctx.send("Ничего не проигрывается.")
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")
@client.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc:
        if vc.is_paused():
            await vc.resume()
        else:
            await ctx.send("Ничего не приостановлено.")
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")
@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Трек не найден.")
    else:
        await ctx.send("Пожалуйста, зайдите в голосовой канал.")

# Help command
@client.command(aliases = ['help', 'хелп', 'помощь', 'справка', 'команды'], pass_context = True)
async def helppp(ctx):
	emb = discord.Embed(title = 'Помощь / Справка', description = """
`!помощь` - **справка по использованию бота.**
`!спомощь` - **справка для администраторов.**
`!сервер` - **узнать информацию о сервере.**
`!правила` - **узнать правила сервера.**
`!бот` - **узнать текущую информацию о боте.**
`!play` - **включить музыку.**
`!stop` - **выключить музыку.**
`!skip` - **скипнуть музыку.**
		""", colour = discord.Color.purple())
	emb.set_footer(text = '2022 © MixLands. Все права защищены.')
	emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/971816187199639572/1007418211987378276/1aaaa01231231ea14287c6e.png')
	await ctx.send(embed = emb)

@client.command(aliases = ['схелп', 'спомощь', 'скоманды'], pass_context = True)
@commands.has_role(810402478624735252)
async def shelp(ctx):
	emb = discord.Embed(title = 'Помощь / Справка для администрации', description = """
`!очистить  <кол-во сообщений>` - **очистить сообщения.**
		""", colour = discord.Color.purple())
	emb.set_footer(text = '2022 © MixLands. Все права защищены.')
	emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/971816187199639572/1007418211987378276/1aaaa01231231ea14287c6e.png')
	await ctx.send(embed = emb)
# Rules command
@client.command(aliases = ['правила'], pass_context = True)
async def rules(ctx):
	emb = discord.Embed(title = 'Правила сервера', description = """
Правила сервера **обязательны к прочтению**, в случае их не знаний Вас **не освобождают** от последствий ваших действий.

Правила сервера можно прочитать на сайте - **https://mixlands.space/#/wiki**
		""", colour = discord.Color.purple())
	emb.set_footer(text = '2022 © MixLands. Все права защищены.')
	emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/971816187199639572/1007418211987378276/1aaaa01231231ea14287c6e.png')
	await ctx.send(embed = emb)
# Server command
@client.command(aliases = ['сервер', 'онлайн', 'online', 'info', 'инфо'], pass_context = True)
async def server(ctx, ip = None):
	if ip is None:
		urlnone = "https://mcapi.us/server/status?ip=play.mixlands.space"
		filen = urllib.request.urlopen(urlnone)
		for line in filen:
			decodedd_line = line.decode("utf-8")

		json_objectt = json.loads(decodedd_line)

		if json_objectt["online"] == False:
			emb = discord.Embed(
				title = 'Информация о сервере', 
				description = """
Сервер выключен! :(

Возможно, на сервере проводятся технические работы.
Пожалуйста, повторите попытку позже.
				""", 
				colour = discord.Color.red()
			)
			emb.set_footer(text = '2022 © MixLands. Все права защищены.')
			await ctx.send(embed = emb)
		else:
			emb = discord.Embed(
				title = 'Информация о сервере', 
				description = """
**Статус сервера** » `Включён`
**IP-Адрес** » `play.mixlands.space`
**Онлайн** » `{}/{}`
**Версия** » `MixCore 1.19.2`
					""".format(json_objectt["players"]["now"], json_objectt["players"]["max"]), 
				colour = discord.Color.green()
			)
			emb.set_thumbnail(url = f"https://eu.mc-api.net/v3/server/favicon/play.mixlands.space")
			emb.set_footer(text = '2022 © MixLands. Все права защищены.')
			await ctx.send(embed = emb)
	else:
		url = f'https://mcapi.us/server/status?ip={ip}'
		file = urllib.request.urlopen(url)
		for line in file:
			decoded_line = line.decode("utf-8")
		json_object = json.loads(decoded_line)

		if json_object["online"] == False:
			emb = discord.Embed(
				title = 'Информация о сервере', 
				description = """
Сервер выключен! :(

Возможно, на сервере проводятся технические работы.
Пожалуйста, повторите попытку позже.
				""", 
				colour = discord.Color.red()
			)
			emb.set_footer(text = '2022 © MixLands. Все права защищены.')
			await ctx.send(embed = emb)
		else:
			emb = discord.Embed(
				title = 'Информация о сервере', 
				description = """
**Статус сервера** » `Включён`
**IP-Адрес **» `{}`
**Онлайн **» `{}/{}`
**Версия **» `{}`
					""".format(ip, json_object["players"]["now"], json_object["players"]["max"], json_object['server']['name']), 
				colour = discord.Color.green()
			)
			emb.set_thumbnail(url = f"https://eu.mc-api.net/v3/server/favicon/{ip}")
			emb.set_footer(text = '2022 © MixLands. Все права защищены.')
			await ctx.send(embed = emb)
# Drop idea command
@client.command(aliases = ['идея', 'предлагаю'], pass_context = True)
async def __idea(ctx, *, messs):
	emb = discord.Embed(
		title = f'Идея от {ctx.author.display_name}', 
		description = f"""
{messs}
	""", colour = discord.Color.gold())
	emb.set_footer(text = '2022 © MixLands. Все права защищены.')
	idea = client.get_channel(967770766416420895)
	react = await idea.send(embed = emb)
	await react.add_reaction('👍')
	await react.add_reaction('👎')



### TICKET SYSTEM ###

# Setup ticket command
@client.command(aliases = ['setup_ticket', 'установить_тикет'])
@commands.has_permissions(administrator=True)
async def __ticket(ctx):
	await ctx.message.delete()
	await ctx.send(
		embed = discord.Embed(title ='Тикеты', description = 'Добро пожаловать в систему тикетов.\nЗдесь Вам помогут практически с любым вопросом/проблемой/подачей дела на суд.\n\nЧтобы создать тикет - нажмите на кнопку `Создать тикет` ниже.', colour = discord.Color.gold()),
        components = [
			Button(style = ButtonStyle.green, label = "Создать тикет", emoji = '🎲', custom_id = 'Ticket')
		]
	)

@client.event
async def on_button_click(interaction):
    canal = interaction.channel
    canal_logs = interaction.guild.get_channel(id_channel_ticket_logs)
    if interaction.component.custom_id == "Ticket":
        await interaction.send(
            components = [
                Select(
                    placeholder = "Какой тикет хотите создать?",
                    options = [
                        SelectOption(label="Вопрос", value="question", description='Если у Вас есть вопросы.', emoji='❔'),
                        SelectOption(label="Помощь", value="help", description='Если Вам нужна помощь.', emoji='📞'),
                        SelectOption(label="Суд", value="report", description='Если Вы хотите подать дело в суд.', emoji='📝'),
                    ],
                    custom_id = "menu")])

    elif interaction.component.custom_id == 'call_staff':

        embed_llamar_staff = discord.Embed(description=f"🔔 {interaction.author.mention} вызвал модерацию.", color=embed_color)
        await canal.send(f'<@&{id_staff_role}>', embed = embed_llamar_staff, delete_after = 20)

    elif interaction.component.custom_id == 'close_ticket':

        embed_cerrar_ticket = discord.Embed(description=f"⚠️ Вы действительно хотите закрыть тикет?", color=embed_color)
        await canal.send(interaction.author.mention, embed=embed_cerrar_ticket, 
                        components = [[
                        Button(custom_id = 'close_yes', label = "Да", style = ButtonStyle.green),
                        Button(custom_id = 'close_no', label = "Нет", style = ButtonStyle.red)]])

    elif interaction.component.custom_id == 'close_yes':

        await canal.delete()
        embed_logs = discord.Embed(title="Тикеты", description=f"", timestamp = datetime.datetime.utcnow(), color=embed_color)
        embed_logs.add_field(name="Тикет", value=f"{canal.name}", inline=True)
        embed_logs.add_field(name="Закрыт (кем) - ", value=f"{interaction.author.mention}", inline=False)
        embed_logs.set_thumbnail(url=interaction.author.avatar_url)
        await canal_logs.send(embed=embed_logs)


    elif interaction.component.custom_id == 'close_no':
        await interaction.message.delete()

@client.event
async def on_select_option(interaction):
    if interaction.component.custom_id == "menu":

        guild = interaction.guild
        category = discord.utils.get(interaction.guild.categories, id = id_ticket_category)
        rol_staff = discord.utils.get(interaction.guild.roles, id = id_staff_role)

        if interaction.values[0] == 'question':

            channel = await guild.create_text_channel(name=f'❔・вопрос-{interaction.author.name}', category=category)
            
            await channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                            send_messages=False,
                            read_messages=False)
            await channel.set_permissions(interaction.author, 
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True)
            await channel.set_permissions(rol_staff,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True,
                                                manage_messages=True)
                                            
            embed_question = discord.Embed(title=f'Вопрос - Привет, {interaction.author.name}!', description='В этом тикете тебе дадут ответ на твой вопрос.\n\nВ случае, если вопрос срочный - нажмите на кнопку `🔔 Вызвать модерацию`.', color=embed_color)
            embed_question.set_thumbnail(url=interaction.author.avatar_url)


            await channel.send(interaction.author.mention, embed=embed_question,

             components = [[
                    Button(custom_id = 'close_ticket', label = "Закрыть тикет", style = ButtonStyle.red, emoji ='🔐'),
                    Button(custom_id = 'call_staff', label = "Вызвать модерацию", style = ButtonStyle.blue, emoji ='🔔')]])

        elif interaction.values[0] == 'help':

            channel = await guild.create_text_channel(name=f'📞・помощь-{interaction.author.name}', category=category)

            await channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                            send_messages=False,
                            read_messages=False)
            await channel.set_permissions(interaction.author, 
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True)
            await channel.set_permissions(rol_staff,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True,
                                                manage_messages=True)

            embed_question = discord.Embed(title=f'Помощь - Привет, {interaction.author.name}!', description='В этом тикете тебе помогут решить проблему.\n\nЕсли Вы нуждаетесь в срочной помощи - нажмите кнопку `🔔 Вызвать модерацию`.', color=embed_color)
            embed_question.set_thumbnail(url=interaction.author.avatar_url)


            await channel.send(interaction.author.mention, embed=embed_question, 

            components = [[
                    Button(custom_id = 'close_ticket', label = "Закрыть тикет", style = ButtonStyle.red, emoji ='🔐'),
                    Button(custom_id = 'call_staff', label = "Вызвать модерацию", style = ButtonStyle.blue, emoji ='🔔')]])

        elif interaction.values[0] == 'report':

            channel = await guild.create_text_channel(name=f'📝・суд-{interaction.author.name}', category=category)

            await channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                            send_messages=False,
                            read_messages=False)
            await channel.set_permissions(interaction.author, 
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True)
            await channel.set_permissions(rol_staff,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True,
                                                manage_messages=True)

            embed_question = discord.Embed(title=f'Жалоба - Привет, {interaction.author.name}!', description='В этом тикете тебе помогут решить проблему.\n\nЕсли Вы нуждаетесь в срочной помощи - нажмите на кнопку `🔔 Вызвать модерацию`.', color=embed_color)
            embed_question.set_thumbnail(url=interaction.author.avatar_url)

            await channel.send(interaction.author.mention, embed=embed_question, 
            
            components = [[
                    Button(custom_id = 'close_ticket', label = "Закрыть тикет", style = ButtonStyle.red, emoji ='🔐'),
                    Button(custom_id = 'call_staff', label = "Вызвать модерацию", style = ButtonStyle.blue, emoji ='🔔')]])

# Deleted message logging
dt = datetime.datetime.now()
dt1 = dt.strftime('%d.%m.%Y, %H:%M')
@client.event
async def on_message_delete(message):
    embed = discord.Embed(title="Удалённое сообщение", description = f"Автор сообщения: `{message.author}`\nСодержимое сообщения: `{message.content}`\nКанал: {message.channel.mention}  -  `{message.channel}`", colour = discord.Color.red())
    logs = client.get_channel(971816187199639572)
    await logs.send(embed=embed)

# Chat filter
bad_words = ['сука']
@client.event
async def on_message(message):
    await client.process_commands(message)
    msg = message.content.lower()
    if msg in bad_words:
        await message.delete()
        await message.author.send('Это слово запрещено писать!')

# Bot information command
@client.command(aliases = ['bot', 'бот'])
async def __bot(ctx):
	pref = settings['prefix']
	emb = discord.Embed(
		title = 'Информация о боте',
		description = """
**Название бота**: `MixLands`
**Префикс**: `{}`
**Пинг:** `{}мс`
**Команда справки**: `!help`
**Разработчик**: `m1xeee`
		""".format(pref, round(client.latency * 1000)), colour = discord.Color.blue())
	emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/971816187199639572/1007418211987378276/1aaaa01231231ea14287c6e.png')
	emb.set_footer(text = '2022 © MixLands. Все права защищены.')
	await ctx.send(embed = emb)

# New tiktok video command
@client.command(aliases = ['видео', 'тикток'], pass_context = True)
@commands.has_role(810402478624735252)
async def __video(ctx, *, messagea):
	emb = discord.Embed(
		title = 'Новое видео', 
		description = f"""
В нашем тиктоке вышло новое видео!
[Кликните для просмотра]({messagea})
	""", colour = discord.Color.gold())
	emb.set_footer(text = '2022 © MixLands. Все права защищены.')
	await ctx.channel.purge(limit=1)
	await ctx.send("<@&902982511720792105>")
	await ctx.channel.purge(limit=1)
	channel = client.get_channel(1019692794626969721)
	await channel.send('В нашем TikTok вышло новое видео!')
	tt = await ctx.send(embed = emb)



### DISCORD SRV SYNCHORNIZATION ###

# Whitelist command
@client.command(aliases = ['вл', 'whitelist', 'проходка', 'вайтлист'], pass_context = True)
@commands.has_role(810402478624735252)
async def wl(ctx, member: discord.Member, *, whitel):
	channel = client.get_channel(1015969008014594048)
	guild = client.get_guild(802848667191083019)
	role = guild.get_role(902982511720792105)
	await ctx.channel.purge(limit=1)
	await member.edit(nick=whitel)
	await member.add_roles(role)
	await channel.send(f'easywl add {whitel}')
	await ctx.author.send(f'Игрок `{nickname}` успешно добавлен в вайтлист!')
# Game-ban command
@client.command(aliases = ['ban', 'бан', 'блок', 'забанить'], pass_context = True)
@commands.has_role(810402478624735252)
async def __ban(ctx, member: discord.Member, nickname, *, reason):
	channel = client.get_channel(1015969008014594048)
	nakaz = client.get_channel(1023349352560853012)
	guild = client.get_guild(802848667191083019)
	role = guild.get_role(902982511720792105)
	await ctx.channel.purge(limit=1)
	await member.remove_roles(role)
	emb = discord.Embed(
		title = f'Бан', 
		description = f"""
Игрок `{nickname}` забанен администратором `{ctx.message.author.display_name}`
Причина: `{reason}`
		""", colour = discord.Color.red())
	await nakaz.send(embed=emb)
	await channel.send(f'ban {nickname} {reason}')
	await ctx.author.send(f'Игрок `{nickname}` успешно забанен!')

# Game-unban command
@client.command(aliases = ['unban', 'разбан', 'разблок', 'разбанить'], pass_context = True)
@commands.has_role(810402478624735252)
async def __unban(ctx, member: discord.Member, *, nickname):
	channel = client.get_channel(1015969008014594048)
	nakaz = client.get_channel(1023349352560853012)
	guild = client.get_guild(802848667191083019)
	role = guild.get_role(902982511720792105)
	await ctx.channel.purge(limit=1)
	await member.add_roles(role)
	emb = discord.Embed(
		title = f'Разбан', 
		description = f"""
Игрок `{nickname}` разбанен администратором `{ctx.message.author.display_name}`
		""", colour = discord.Color.green())
	await nakaz.send(embed=emb)
	await channel.send(f'unban {nickname}')
	await ctx.author.send(f'Игрок `{nickname}` успешно разбанен!')

# Game-mute command
@client.command(aliases = ['mute', 'мут', 'мьют', 'замутить'], pass_context = True)
@commands.has_role(810402478624735252)
async def tempmute(ctx, nickname, time: int, *, reason):
	channel = client.get_channel(1015969008014594048)
	nakaz = client.get_channel(1023349352560853012)
	await ctx.channel.purge(limit=1)
	emb = discord.Embed(
		title = f'Мут', 
		description = f"""
Игрок `{nickname}` замучен администратором `{ctx.message.author.display_name}`
Причина: `{reason}`
Срок: `{time} ч`
		""", colour = discord.Color.red())
	await nakaz.send(embed=emb)
	await channel.send(f'tempmute {nickname} {time}h {reason}')
	await ctx.author.send(f'Игрок `{nickname}` успешно замучен!')

# Game-warn command
@client.command(aliases = ['warn', 'pred', 'пред', 'варн', 'заварнить', 'предупредить'], pass_context = True)
@commands.has_role(810402478624735252)
async def tempwarn(ctx, nickname, time: int, *, reason):
	channel = client.get_channel(1015969008014594048)
	nakaz = client.get_channel(1023349352560853012)
	await ctx.channel.purge(limit=1)
	emb = discord.Embed(
		title = f'Предупреждение', 
		description = f"""
Игрок `{nickname}` получил предупреждение от администратора `{ctx.message.author.display_name}`
Причина: `{reason}`
Срок: `{time} дн`
		""", colour = discord.Color.gold())
	await nakaz.send(embed=emb)
	await channel.send(f'tempwarn {nickname} {time}d {reason}')
	await ctx.author.send(f'Игрок `{nickname}` успешно заварнен!')

# Broadcast command
@client.command(aliases = ['объявление', 'bc'], pass_context = True)
async def obyava(ctx, *, messs):
	channel = client.get_channel(915628908215406742)
	emb = discord.Embed(
		title = f'Объявление от {ctx.author.display_name}', 
		description = f"""
{messs}
		""", colour = discord.Color.green())
	await channel.send(embed=emb)
	await ctx.author.send('Ваше объявление успешно отправлено!')

# Buy broadcast command
@client.command(aliases = ['купить', 'куплю', 'buy'], pass_context = True)
async def __buy(ctx, budget: int, *, messss):
	channel = client.get_channel(915628908215406742)
	if budget > 64 and budget <= 128:
		emb = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Куплю: `{messss}`
Бюджет: `1 стак {budget - 64} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif budget > 128 and budget <= 192:
		emb1 = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Куплю: `{messss}`
Бюджет: `2 стака {budget - 128} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb1)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif budget > 192 and budget <= 256:
		emb2 = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Куплю: `{messss}`
Бюджет: `3 стака {budget - 192} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb2)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif budget > 256 and budget <= 320:
		emb3 = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Куплю: `{messss}`
Бюджет: `4 стака {budget - 256} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb3)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif budget > 320 and budget <= 384:
		emb4 = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Куплю: `{messss}`
Бюджет: `5 стаков {budget - 320} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb4)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif budget > 384:
		await ctx.author.send('Бюджет слишком большой, укажите значение меньше.')
	elif budget != int:
		await ctx.author.send('Введите бюджет как число!')
	else:
		await ctx.author.send('Ошибка, обратитесь к администратору.')

# Sell broadcast command
@client.command(aliases = ['продать', 'продам', 'sell'], pass_context = True)
async def __sell(ctx, price: int, *, messsss):
	channel = client.get_channel(915628908215406742)
	if price <= 64:
		emb = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Продам: `{messsss}`
	Цена: `{price} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif price > 64 and price < 128:
		emb = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Продам: `{messsss}`
	Цена: `1 стак {price - 64} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif price > 128 and price < 192:
		emb = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Продам: `{messsss}`
	Цена: `2 стака {price - 128} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif price > 192 and price < 256:
		emb = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Продам: `{messsss}`
	Цена: `3 стака {price - 192} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif price > 256 and price < 320:
		emb = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Продам: `{messsss}`
	Цена: `4 стака {price - 256} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif price > 320 and price < 384:
		emb = discord.Embed(
			title = f'Объявление от {ctx.author.display_name}', 
			description = f"""Продам: `{messsss}`
	Цена: `5 стаков {price - 320} АР`\nИгрок: {ctx.author.mention}""", colour = discord.Color.gold())
		await channel.send(embed=emb)
		await ctx.author.send('Ваше объявление успешно отправлено!')
	elif price > 384:
		await ctx.author.send('Бюджет слишком большой, укажите значение меньше.')
	elif price != int:
		await ctx.author.send('Введите цену как число!')
	else:
		await ctx.author.send('Ошибка, обратитесь к администратору.')

# Bot running
client.run(settings['token'])
