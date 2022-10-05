# MixLands Discord BOT

In order to install the bot, first of all you need to insert your token and guild ID into the **config.yml** file.

After setting up the token and guild ID, it's worth going to the **application.yml** file and inserting your password to create a node.

Install JDK.
### ```sudo apt install default-jre```
### ```sudo apt install default-jdk```

Once you have set the password for creating the node and the JDK, create a screen on your Linux server and run the Lavalink.jar file.
### ```screen -S lavalink```
### ```java -jar Lavalink.jar```

Now for stable work, you need to install the old version of discord.py.
### ```sudo apt uninstall discord.py```
### ```sudo apt install discord.py==1.7.3```
Since the discord-components library is no longer updated, it must be installed manually, so move the discord-components folder from the repository to **/usr/lib/python3.10/**

Go to the **bot.py** file, replace all the IDs of roles, channels and categories there for yourself.
In the music system, set the password that was specified in the **application.yml** file.
Customize the bot for yourself and run it on the second screen of your Linux server.
### ```screen -S bot```
### ```python3 bot.py```

All is ready!
I want to ask you not to change the name of the developer in the embed of the !bot command.

If you have any problems or have questions - write to me in telegram: `@justice_code`.
