from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.sync import events
from telethon import functions, types
import telethon
from bot_functions import *
import requests






client_name = ''
bot_name = ''
API_ID = 
API_HASH = ''
BOT_TOKEN = ''

chatId = None
destChatId = None




client = TelegramClient(client_name, API_ID, API_HASH)
bot = TelegramClient(bot_name, API_ID, API_HASH)

client.start()
bot.start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage)
async def bot_new_message_handler(event):
  if(event.raw_text.startswith('/')):
    command = event.raw_text.split('/')[1]
    
    await botCommandRecieved(event, command)

@client.on(events.NewMessage)
async def new_message_handler(event):
  global chatId
  global destChatId
  
  # check if its not telegram official account
  if event.message.from_id != 777000:
    # check if its recieving message
    if event.out == False:
      
        
        
      

      print('new message')

async def joinChannel(id):
  channel = await client.get_entity(id)
  
  await client(JoinChannelRequest(channel))

async def botCommandRecieved(event, command):
  global chatId
  global destChatId
  
  if command == 'start':
    chat = await event.get_chat()

    chatId = chat.id

    await event.respond('you will get new messages here')

  # set destination channel
  elif command.startswith('setdest'):
    channelId = command.split(' ')[1]

    destChatId = channelId

    await event.respond('channel saved')
    
  # add channel command
  elif command.startswith('addchannel'):
    channelId = command.split(' ')[1]

    isIdValid = await validateChannelId(channelId, bot)

    if isIdValid:
      try:
        await joinChannel(channelId)

        await event.respond('channel added')
      except:
        await event.respond('there was a problem')

    else:
      await event.respond('id is not a valid channel')

  else:
    await event.respond('default command response: ' + command)

client.run_until_disconnected()
