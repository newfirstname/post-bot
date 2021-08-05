responses = {
  'start_bot': 'Hola!',

  'get_connector_name': 'Send Me the name of new Connector.\ncancel this operation using /cancel',
  
  'cancel_command': '✔️ you commands are canceled \n you can now start new actions \n or use /help\n\ncheckout your connectors /myconnectors',
  
  'delete_connector': '✔️ connector was deleted\ncontinue with /myconnectors',

  'send_dest_id': 'Enter the username of destination like this:\nmy_destination (without @)',

  'send_source_id': 'Enter the username of source like this:\nmy_source (without @)',
}

def get_response(resFor, *args):
  res = 'dude'

  if resFor == 'connector_created':
    res = f'Connector "{args[0]}" created successfully.\nyou can now add Sources and Destination\nStart here: /myconnectors'
  elif resFor == 'dest_added':
    res = f'✔️ "{args[0]}" added successfully\n\nAdd another destination: /adddest\n\n👁 View connector: /connector_{args[1]}'
  elif resFor == 'already_in_dests':
    res = f'❗ id "{args[0]}" is already in destinations.\n go back: /connector_{args[1]}'
  elif resFor == 'source_added':
    res = f'✔️ "{args[0]}" added successfully\n\nAdd another source: /addsource\n\n👁 View connector: /connector_{args[1]}'
  elif resFor == 'already_in_dests':
    res = f'❗ id "{args[0]}" is already in sources.\n go back: /connector_{args[1]}'

  return res

responses['get'] = get_response