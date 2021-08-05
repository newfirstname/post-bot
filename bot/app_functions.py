from telethon.tl.types import Channel, User
import db
from responses import responses

async def validateChannelId(id, bot):
  try:
    channel = await bot.get_entity(id)

    if type(channel) == Channel:
      return True
    elif type(channel) == User:
      return 'isuser'
    else:
      return False

  except Exception as e:
    print(e)
    return False

async def getUser(id, bot):
  try:
    user = await bot.get_entity(int(id))

    if type(user) == User:
      return user
    else:
      return False

  except:
    return False

def getConnectorsHavingSource(sourceId):
  li = db.exec_fetch('SELECT * FROM connectors WHERE %s = ANY (sources)', (sourceId.lower(),))

  return li

def getDestAndRuleWithSource(sourceId):
  destAndRules = db.exec_fetch('SELECT destinations, rules FROM connectors WHERE %s = ANY (sources)', (sourceId.lower(),))

  return destAndRules

def removeSource(conId, sourceId):
  db.exec('UPDATE connectors SET sources = array_remove(sources, %s) WHERE id = %s', (sourceId.lower(), conId,))

def removeDest(conId, destId):
  db.exec('UPDATE connectors SET destinations = array_remove(destinations, %s) WHERE id = %s', (destId.lower(), conId,))

def addDest(conId, destId):
  consWithThisIdInSource = db.exec_fetch('SELECT name FROM connectors WHERE %s = ANY (sources)', (destId.lower(),))

  # check if id is not in sources
  if len(consWithThisIdInSource) == 0:
    # check if dest is in this connector
    hasDest = db.exec_fetch('SELECT id FROM connectors WHERE %s = ANY (destinations) AND id = %s', (destId.lower(), conId,))

    if len(hasDest) == 0:
      db.exec('UPDATE connectors SET destinations = array_cat(destinations, %s) WHERE id = %s', ([destId.lower()], conId,))

      return 'success'
    else:
      return 'hasdest'

  else:
    # the id was found in sources therefor it can't be in dests
    return 'isinsources'

def addSource(conId, sourceId):
  consWithThisIdInDests = db.exec_fetch('SELECT id FROM connectors WHERE %s = ANY (destinations)', (sourceId.lower(),))

  # check if id is not in destinations
  if len(consWithThisIdInDests) == 0:
    # check if source is in this connector
    hasSource = db.exec_fetch('SELECT id FROM connectors WHERE %s = ANY (sources) AND id = %s', (sourceId.lower(), conId,))

    if len(hasSource) == 0:
      db.exec('UPDATE connectors SET sources = array_cat(sources, %s) WHERE id = %s', ([sourceId.lower()], conId,))

      return 'success'
    else:
      return 'hassource'
  else:
    # the id was found in destinations therefor it can't be in sources
    return 'isindests'
  
def userOwnsConnector(userId, conId):
  conId = db.exec_fetch('SELECT owner_id FROM connectors WHERE id = %s', (conId,))

  if userId == conId[0][0]:
    return True
  else:
    return False

def setSiteId(userId, siteId):
  try:
    db.updateUser(userId, 'site_id', siteId)
    return True
  except:
    return False

def setBitlyToken(userId, token):
  try:
    db.updateUser(userId, 'bitly_token', token)
    return True
  except:
    return False

def getActiveConnectorSources(userId):
  res = db.exec_fetch('SELECT active_connector FROM users WHERE telegram_id = %s', (userId,))

  conId = res[0][0]

  res1 = db.exec_fetch('SELECT sources FROM connectors WHERE id = %s', (conId,))

  return res1[0]

def addConnector(userId, name):
  db.exec('INSERT INTO connectors (owner_id, name, sources, destinations, rules) VALUES (%s, %s, %s, %s, %s)', (userId, name, [], [], [],))

def deleteConnector(conId):
  try:
    db.exec('DELETE FROM connectors WHERE id = %s', (conId,))

    return True
  except:
    return False

def hasActiveConnector(id):
  res = db.exec_fetch('SELECT active_connector FROM users WHERE telegram_id = %s', (id,))

  if res[0][0] == 0:
    return False
  else:
    return res[0][0]

def resetUser(id, *args):
  if args:
    if args[0] == 'justaction':
      cancelUserAction(id)
  else:
    cancelUserAction(id)
    setUserActiveCon(id, 0)

def setUserActiveCon(userId, conId):
  db.updateUser(userId, 'active_connector', conId)

def setUserCurrentAction(id, action):
  db.updateUser(id, 'current_action', action)

def cancelUserAction(id):
  db.updateUser(id, 'current_action', 'none')

def getUserCurrentAction(id):
  ac = db.exec_fetch('SELECT current_action FROM users WHERE telegram_id = %s', (id,))

  return ac[0][0]

def checkAuthUser(id):
  users = db.exec_fetch('SELECT 1 FROM users WHERE telegram_id = %s', (id,))

  if users:
    return True
  else:
    return False

def getConnector(id):
  con = db.exec_fetch('SELECT * FROM connectors WHERE id = %s', (id,))

  if len(con) == 0:
    return False
  else:
    return con[0]

def checkUserInDb(id):
  user = db.exec_fetch('SELECT * FROM users WHERE telegram_id = %s', (id,))

  if user:
    return True
  else:
    return False

async def respondAction(action, event, bot):
  respond = event.respond
  id = event.original_update.message.peer_id.user_id
  text = event.raw_text

  if action == 'adding-destination-to-connector':
    try:
      # validate if a channel exists
      isChannel = await validateChannelId(text, bot)

      if isChannel == True:
        conId = db.exec_fetch('SELECT active_connector FROM users WHERE telegram_id = %s', (id,))

        success = addDest(conId[0][0], text)

        if success == 'success':
          # dest was added in database
          await respond(responses['get']('dest_added', text, conId[0][0]))
          
          await respond(f'please make sure bot is admin in "{text}"')

          resetUser(id, 'justaction')

          return 'destadded'
        elif success == 'hasdest':
          await respond(f'❗ id "{text}" is already in destinations.\n go back: /connector_{conId[0][0]}')
        elif success == 'isinsources':
          await respond(f'❗ id "{text}" is used by you or other users as a source, you can only use it as a source. enter another id\nor /cancel the operation')
      elif isChannel == 'isuser':
        conId = db.exec_fetch('SELECT active_connector FROM users WHERE telegram_id = %s', (id,))

        success = addDest(conId[0][0], text)

        if success == 'success':
          # dest was added in database
          await respond(responses['get']('dest_added', text, conId[0][0]))
          
          resetUser(id, 'justaction')

          return 'destadded'
        elif success == 'hasdest':
          await respond(responses['get']('already_in_dests', text, conId[0][0]))
        elif success == 'isinsources':
          await respond(f'❗ id "{text}" is used by you or other users as a source, you can only use it as a source. enter another id\nor /cancel the operation')
      else:
        # channel was invalid
        await respond('please enter a valid id')
    except:
      await respond('failed to add destination, please try again or contact supprot')
  elif action == 'adding-source-to-connector':
    try:
      # validate if a channel exists
      isChannel = await validateChannelId(text, bot)

      if isChannel:
        conId = db.exec_fetch('SELECT active_connector FROM users WHERE telegram_id = %s', (id,))

        success = addSource(conId[0][0], text)

        if success == 'success':
          # dest was added in database
          await respond(responses['get']('source_added', text, conId[0][0]))

          resetUser(id, 'justaction')
          
          return 'sourceadded'
        elif success == 'hassource':
          await respond(responses['get']('already_in_sources', text, conId[0][0]))
        elif success == 'isindests':
          await respond(f'❗ id "{text}" is used by you or other users as a destination, you can only use it as a destination. enter another id\nor /cancel the operation')
        
      else:
        await respond('please enter a valid channel id\n or /cancel operation')
    except:
      await respond('failed to add source, please try again or contact supprot')
  elif action == 'getting-new-connector-name':
    try:
      if len(text) < 32:
        addConnector(id, text)
        
        await respond(responses['get']('connector_created', text))

        setUserCurrentAction(id, 'none')
      else:
        await respond('❗ connector name must be less than 32 characters')
    except:
      await respond('failed to add connector please try again or contact supprot')

def getConnectors(userId):
  cons = db.exec_fetch('SELECT id, name FROM connectors WHERE owner_id = %s', (userId,))

  return cons

def saveMessage(sourceId, idInSource, destId, idInDest, date, rules):
  db.exec('INSERT INTO messages (source_id, id_in_source, dest_id, id_in_dest, message_date, rules) VALUES (%s, %s, %s, %s, %s, %s)', (sourceId, idInSource, destId, idInDest, date, rules,))

def getPeerMessagesIds(sourceId, idInsource):
  res = db.exec_fetch('SELECT dest_id, id_in_dest, rules FROM messages WHERE source_id = %s AND id_in_source = %s', (sourceId, idInsource,))

  return res