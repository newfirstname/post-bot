# POST-BOT

A telegram auto-forward bot with react based UI to manage the filters and rules

## Prerequisites

- Python version 3
- Postgresql
- pgAdmin ( comes with postgres )
- Nodejs version 8 or higher
- npm ( comes with Nodejs )

### Install Dependencies:

We need **telethon** and **psycopg2** for this project, install them with:

```sh
$ pip install telethon==1.22.0
```

```sh
$ pip install psycopg2
```

> Make sure the telethin version 1.22.0 is installed

### Create a Database

Use pgAdmin to create a new database, lets name it `post-bot` and set a password of `1234678` for it.

Then we must add the database credentials to the `bot/db.py` file at the top of it:

```python
DB_HOST='localhost'
DB_NAME='post-bot'
DB_USER='postgres'
DB_PASS='12345678'
DB_PORT=5432
```

Then we must initialize the database with running the `bot/initDB.py` file:

```sh
$ py bot/initDB.py
```

### Telegram Credentials

Now in order to get access to telgram we need an `api id` and an `api hash` witch you can get them from [here](https://my.telegram.org/), its fairly straight forward...

Then use telegram [botfather](https://t.me/botfather) to create a new bot and set the following commands for the bot and also make sure to get the `bot token`

```txt
newconnector - create connector
myconnectors - list of connectors
cancel - cancel current operation
```

> You can set the bot command by talking to the botfather bot on telegram, it will guide you itslef

#### Add Telegram Creds to `Bot.py`

Open `bot/bot.py` and edit the following lines, replace the credantails with the ones you just obtained.

```python
API_ID = 123
API_HASH = '123'
BOT_TOKEN = '123'
```

## Start The Bot

Now you must be able to run the bot and use all its forwarding options **exept filterings** ( we will add and remove filters with the UI ).

To run the bot run:

```bash
$ py bot/bot.py
```

> We will use a telegram account to access the channels and enw messages, so make sure to use a brand new, fully empty telegram account, this account will join the channels you use as source and will be informes informed on new messages.

You will be prompted to enter your phone number or bot token. enter your phone number with the **country code**. Then enter the code telegram sends to your accocunt.

> About security concerns: the date of your account will be stored locally on your own machin, a `.session` file will be created witch stors all of your account credentials.

### Bot is ready

now you can use your bot, ( you can find it on telgram by the id you gave to `@botfather` while creating it ) to create new connectors and start **auto-forwarding**.

##### What is a Connector:

Each connection between one or more _sources_ and one or more _destinations_ is called a **Connector**.

> Eqaxmple: a connector can forward messages from `channel 1` to `chanenl 2` and Another connector send from `channel 3` to `channel 2`
> Or you can combine thense two connectors and make just one connector which will forward from both `channel 1` and `3` to `channel 2`

#### How to use the bot:

In some small steps:

- Send `/start` to start it.
- Then use `/newconnector` to create new connector.
- Name your new Connector ( just send the name to the bot ).
- Send `/myconnectors` to see the list of your connecotrs.
- Tab on the connector you wish to edit.
- now you can add sources and destination to the connector.

Now you can test the bot, it will forward messages from every-where ( public ) to your cahnnels

> Just make sure the bot is admin in the destination channels.

# Add Web-Based User Interface to edit filters

first step is to add the database credentials to our UI folder too.
open the `UI/config/config.env` file and add the database creds to it:

```javascript
DBUSER = 'postgres';
DBPASS = '12345678';
DBHOST = 'localhost';
DBPORT = 5432;
DBNAME = 'post-bot';
```

## Install Web Dependencies

We use express as a server to run databse queries, go to the UI folder and run `npm i`

```sh
$ cd UI
$ npm i
```

When the dependencies where installed you can start the UI by:

```sh
npm start
```

now you can go to `localhost:5000` and use the ui to edit the connectors and add/remove/edit the filters of the UI

> in the UI the filters are called rules.
