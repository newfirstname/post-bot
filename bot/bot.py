import datetime
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.sync import events
from telethon import functions, types
from telethon.tl.types import PeerChannel, PeerUser
from telethon.tl.types import MessageMediaPhoto
from telethon.utils import get_input_photo, resolve_bot_file_id, pack_bot_file_id
import telethon
import app_functions as funcs
import db
from rules import filterMessage
import sys
import os
from responses import responses
from utils import set_interval

db.connectDB()

client_name = 'client'
bot_name = 'bot'
API_ID = 1945628
API_HASH = '2c96a07930fe107684ab108250886d49'
BOT_TOKEN = '123'

client = TelegramClient(client_name, API_ID, API_HASH)
bot = TelegramClient(bot_name, API_ID, API_HASH)

client.start()
bot.start(bot_token=BOT_TOKEN)

async def getPeerMessages(sourceId, idInSource, *args):
  messagesDataInDB = funcs.getPeerMessagesIds(sourceId, idInSource)

  messages = []
  for data in messagesDataInDB:
    channelId = data[0]
    messageId = data[1]
    messageRules = data[2]
    
    if args:
      if args[0] == 'justid':
        messages.append({
          'messageId': messageId,
          'channelId': channelId
        })
      elif args[0] == 'withrules':
        message = await client.get_messages(channelId, ids=messageId)

        messages.append({
          'message': message,
          'rules': messageRules
        })
    else:
      message = await client.get_messages(channelId, ids=messageId)

      messages.append(message)

  return messages

@bot.on(events.NewMessage)
async def bot_new_message_handler(event):
  # catch messages being posted in Channel
  if type(event.original_update.message.peer_id) == PeerChannel: return
  
  userId = event.original_update.message.peer_id.user_id

  try:
    isUser = funcs.checkAuthUser(userId)
    
    if isUser:
      if(event.raw_text.startswith('/')):
        command = event.raw_text.split('/')[1]
        
        await botCommandRecieved(event, command)
      else:
        action = funcs.getUserCurrentAction(userId)

        if action != 'none':
          actionResult = await funcs.respondAction(action, event, bot)

          if actionResult == 'sourceadded':
            await joinChannel(event.raw_text)
        else:
          await event.respond('default response')
    elif event.raw_text == '/start':
      db.addUser(userId, 'common-user')

      await event.respond('you are now activated')
    elif event.raw_text == '/getid':
      await event.respond(f'{userId}')
    else:
      await event.respond('with all wonders!\ntry sending /start first :|')
  except Exception as e:
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)

@client.on(events.NewMessage)
async def new_message_handler(event):
  if type(event.original_update.message) == str:
    return
  
  if type(event.original_update.message.peer_id) == PeerChannel:
    if event.to_id:
      channel = await client.get_entity(event.to_id.channel_id)
    else:
      channel = await client.get_entity(event.message.to_id.channel_id)
    channelUsername = channel.username.lower()

    message = await bot.get_messages(channelUsername, ids=event.message.id)

    # if super group => get messaeg from event
    if not message:
      message = event.message
      if message.media:
        message.media = None

    destAndRules = funcs.getDestAndRuleWithSource(channelUsername)
    
    for i in destAndRules:
      dests = i[0]
      rules = i[1]

      filterResult = filterMessage(message, rules)
      # filterResult = {
      #   'message': message,
      #   'hasPassed': True
      # }

      if filterResult['hasPassed']:
        message = filterResult['message']
        
        for dest in dests:
          if message.reply_to_msg_id:
            dest_ent = await client.get_entity(dest)
            if message.reply_to_msg_id:
              peerReplys = await getPeerMessages(channel.id, message.reply_to_msg_id, 'justid')

              # the replyed message is not in the database
              if len(peerReplys) == 0:
                sentMessage = await bot.send_message(dest, message)
              
              for reply in peerReplys:
                if reply['channelId'] == dest_ent.id:
                  sentMessage = await bot.send_message(dest, message, reply_to=reply['messageId'])
          else:
            sentMessage = await bot.send_message(dest, message)

          funcs.saveMessage(message.to_id.channel_id, message.id, sentMessage.to_id.channel_id, sentMessage.id, f'{sentMessage.date.year}-{sentMessage.date.month}-{sentMessage.date.day}', rules)

  elif type(event.to_id) == PeerUser:
    user = await client.get_entity(None)
    username = user.username
  
async def leaveChannel(id):
  try:
    await client.delete_dialog(id)
    
    return True
  except:
    return False

async def joinChannel(id):
  channel = await client.get_entity(id)
  
  await client(JoinChannelRequest(channel))

async def botCommandRecieved(event, command):
  userId = event.original_update.message.peer_id.user_id
  
  if command == 'start':
    await event.respond(responses['start_bot'])

  # give the id
  elif command == 'getid':
    await event.respond(f'{userId}')

  # get connectors
  elif command == 'myconnectors':
    funcs.cancelUserAction(userId)
    funcs.setUserActiveCon(userId, 0)
    connectors = funcs.getConnectors(userId)

    response = 'here is your connectors ⤵️ \n\n'

    for con in connectors:
      name = con['name']
      id = con['id']
      response += f'🔗 {name}\n👁️: /connector_{id}\n\n'

    if len(connectors) == 0:
      response = '🚩 you have no connectors! \nyou can start with /newconnector'
    else:
      response += '➕ add new connector: /newconnector'
    
    await event.respond(response)
    
  # add new connector
  elif command == 'newconnector':
    funcs.setUserCurrentAction(userId, 'getting-new-connector-name')

    await event.respond(responses['get_connector_name'])
    
  # help command
  elif command == 'help':
    await event.respond('comming soon!')
    
  # cancel current action
  elif command == 'cancel':
    funcs.resetUser(userId)
    
    await event.respond(responses['cancel_command'])
    
  # set site id
  elif command.startswith('setsiteid'):
    if len(command.split(' ')) == 1:
      await event.respond('please add the id in the command, link this:\n/setsiteid <site-id>')
    else:
      siteId = command.split(' ')[1]

      try:
        funcs.setSiteId(userId, siteId)
        await event.respond('id saved')
      except:
        await event.respond('there was a problem, please contact support')
    
  # set bitly token
  elif command.startswith('setbitlytoken'):
    if len(command.split(' ')) == 1:
      await event.respond('please add the token in the command, link this:\n/setbitlytoken <bitly-token>')
    else:
      token = command.split(' ')[1]

      try:
        funcs.setBitlyToken(userId, token)
        await event.respond('token saved')
      except:
        await event.respond('there was a problem, please contact support')

  # edit connector
  elif command.startswith('connector'):
    conId = command.split('_')[1]

    con = funcs.getConnector(conId)

    if con:
      if con['owner_id'] == userId:
        funcs.setUserActiveCon(userId, con['id'])
        
        response = '🔗 ' + con['name'] + '\n\n'

        response += '🔻 sources:\n'
        for source in con['sources']:
          response += f'{source}\n'

        if len(con['sources']) == 0:
          response += 'this connector has no source\n'
          
        response += 'add new source: /addsource\n\n'

        response += '🔺 destinations:\n'
        for dest in con['destinations']:
          response += f'{dest}\n'

        if len(con['destinations']) == 0:
          response += 'this connector has no destination\n'

        response += 'add new dest: /adddest\n\n'

        conId = con['id']

        response += f'🖊️ edit connector: /editconnector_{conId}\n\n'

        response += '❌ delete connector: /delconnector\n\n'

        response += 'all connectors: /myconnectors'

        await event.respond(response)
      else:
        # user doesnt own the con
        await event.respond('connector id invalid')
    else:
      # connector was not found
      await event.respond('connector id invalid')

  # delete a connector
  elif command == 'delconnector':
    activeConnector = funcs.hasActiveConnector(userId)
    
    if activeConnector:
      # find sources of channel
      sources = funcs.getActiveConnectorSources(userId)

      for source in sources[0]:
        # find other connectors with this source
        connectors = funcs.getConnectorsHavingSource(source)

        # leave channels if no other user has it in sources
        if len(connectors) == 1:
          await leaveChannel(source)
    
      success = funcs.deleteConnector(activeConnector)

      if success == True:
        funcs.resetUser(userId)
        await event.respond(responses['delete_connector'])
      else:      
        await event.respond('there was a problem')

    else:
      await event.respond('please select a connector first with /myconnectors')

  # add dest to a connector
  elif command == 'adddest':
    isEditingCon = funcs.hasActiveConnector(userId)
    
    if isEditingCon:
      funcs.setUserCurrentAction(userId, 'adding-destination-to-connector')

      await event.respond(responses['send_dest_id'])
    else:
      await event.respond('please select a connector first\nsee your connectors at /myconnectors')

  # delete a dest from a connector
  elif command.startswith('deld'):
    destList = command.split('_')
    del destList[0]
    conId = destList[-1]
    del destList[-1]
    dest = '_'.join(destList)

    owns = funcs.userOwnsConnector(userId, conId)

    if owns:
      try:
        funcs.removeDest(conId, dest)

        await event.respond(f'✔️ "{dest}" was removed\ngo back: /editconnector_{conId}')

      except:
        await event.respond('there was a problem please contact support')
        
    else:
      await event.respond('invalid command')

  # delete a source from a connector
  elif command.startswith('dels'):
    sourceList = command.split('_')
    del sourceList[0]
    conId = sourceList[-1]
    del sourceList[-1]
    source = '_'.join(sourceList)

    owns = funcs.userOwnsConnector(userId, conId)

    if owns:
      try:
        funcs.removeSource(conId, source)

        listOfConnectorsWithSource = funcs.getConnectorsHavingSource(source.lower())

        if len(listOfConnectorsWithSource) == 0:
          await leaveChannel(source)

        await event.respond(f'✔️ "{source}" was removed\ngo back: /editconnector_{conId}')

      except:
        await event.respond('there was a problem please contact support')
        
    else:
      await event.respond('invalid command')

  # add source to a connector
  elif command.startswith('addsource'):
    isEditingCon = funcs.hasActiveConnector(userId)

    if isEditingCon:
      funcs.setUserCurrentAction(userId, 'adding-source-to-connector')

      await event.respond(responses['send_source_id'])
    else:
      await event.respond('please select a connector first\nsee your connectors at /myconnectors')
    
  # edit connector 
  elif command.startswith('editconnector'):
    conId = command.split('_')[1]

    con = funcs.getConnector(conId)

    if con:
      if con['owner_id'] == userId:
        funcs.setUserActiveCon(userId, con['id'])
        conId = con['id']
        
        response = '🔗 ' + con['name'] + '\n\n'

        response += '🔻 sources:\n'

        for source in con['sources']:
          response += source + '\n'
          response += f'delete:\n/dels_{source}_{conId}\n\n'

        response += '🔺 destinations:\n'

        for dest in con['destinations']:
          response += dest + '\n'
          response += f'delete: /deld_{dest}_{conId}\n\n'

        response += f'\ngo back: /connector_{conId}'

        await event.respond(response)
      else:
        # user doesnt own the con
        await event.respond('connector id invalid')
    else:
      await event.respond('connector id invalid')
    
  # rules
  # elif command.startswith('rules'):
  #   funcs.setUserCurrentAction(userId, 'sending-rules')

  #   await event.respond('Please answer the following questions to setup custom filters:\nQ1: Any keyword you want to add, omit or replace ? Yes or No\nQ2: Any links you want to convert, remove or shorten ? Yes or No\nQ3: Any media you want to block, skip or whitelist ? Yes or No\nQ4: Any other filter required ? Yes or No')
    
  # my own private commands 
  # add a user to list 
  elif command.startswith('adduser'):
    userId = command.split(' ')[1]

    if len(command.split(' ')) > 2:
      return

    userExists = funcs.checkUserInDb(userId)

    if not userExists:
      user = await funcs.getUser(userId, bot)

      if user:
        userName = user.first_name + ' ' + user.last_name if user.last_name else user.first_name

        try:
          addResult = db.addUser(userId, userName)

          if addResult:
            await event.respond(f'✔️ user {userName} added')
          else:
            await event.respond(f'there was a problem!')
        except:
          await event.respond('there was a problem')

      else:
        await event.respond('user not valid')
    else:
      await event.respond('user is already a member')

  # inject
  elif command.startswith('inject'):
    q = command[7:]

    db.exec(q)

  # test command
  elif command == 'test':
    print('test')
    
    await event.respond('test response')
  
  else:
    await event.respond('command is not defined: ' + command)

db.deleteOldMessages()
# set cron job to delete old messages to keep db lite
set_interval(db.deleteOldMessages, db.DAYS_TO_KEEP_MESSAGES * 24 * 60 * 60)

client.run_until_disconnected()

db.closeDB()