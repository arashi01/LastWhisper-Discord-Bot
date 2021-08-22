# LastWhisper-Discord-Bot
This is the code for the discord bot of The Last Whisper Free Company in the game Final Fantasy XIV.

# Table of contents:
- [Features of the Discord bot](#features-of-the-discord-bot)
- [Prerequisites](#prerequisites)
  - [Docker](#docker)
  - [Manual](#manual)
- [Installation](#installation)
  - [Step 1](#step-1)
  - [Step 2](#step-2)
  - [Step 3](#step-3)
  - [Step 4](#step-4)

## Features of the Discord bot:
* Periodically post a message about the buff for the day.
* Config manager that allows for changing of setting from Discord.
* Config framework allowing for 3RD party Cogs to utilize the Config Manager Cog.
* Extension Manager Cog that allows for managing of extension files (WIP).

## Prerequisites

### Docker
A docker file has been provided along with a docker composer file.
Assuming you have the docker setup correctly on your machine this should be the simplest method of setting up.

### Manual
* Python 3.8 or above (3.6 might work, but it is untested).
* discord.py Python libraries.

## Installation

###Step 1:
Create a bot application in the Discord Development Page.

###Step 2:
Get the key for the bot (found under bot section of the developer page) and create a fill called `token` (no extension) in the `secrets` folder.

###Step 3:
Clone the project to your desired location.
```shell
git clone --recurse-submodules https://github.com/ShadowKing345/LastWhisper-Discord-Bot.git
```

###Step 4:
####The fork in the road.

Assuming you are using docker-compose.
Run docker compose up in the root directory of the project.
```shell
docker-compose up
```

However, if you are not going to use docker then there are a few more steps to take.
Firstly make sure you are in the bot dir.
```shell
cd ./bot
```
This is because if you attempt to run the bot from the project root directory it will result in the working directory being set to that folder which the bot was not designed around. So to avoid many errors simply cd to the correct directory.

Now then get your version of python installed.
```shell
python --version
```
For Window's it may be py (I find references to both, but I primarily use linux so.... sorry).

Install the libraries needed for to run the bot.
```shell
python3 -m pip install -U discord.py
# provided by discord.py docs
```
For Windows:
```shell
py -3 -m pip install -U discord.py
# provided by discord.py docs
```
Global installations will require administration privileges.

Finally, simply run
```shell
python[version number] client.py
#eg:
python3.9.2 client.py
#or:
python3 client.py
```
The reason for this is that sometimes you may have multiple versions of python that are installed. While running python by itself may result in the latest version, when you run it without any version it can and sometimes will just use the lowest version you have installed. Since some versions have syntax changes such as 3.8 introducing the `:=` operator it can break compatability and prevent the bot from running to begin with. So force the correct python version to be used would be the safest option.

If you are having issues finding the libraries when attempting to run the bot try to install discord.py with the same trick.
```shell
python3.9.2 -m pip install discord.py
```
ya if you think version management is a shot in the dark for python, lua is worse sadly.

[Back to top](#lastwhisper-discord-bot)