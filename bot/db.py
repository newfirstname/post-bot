import psycopg2
from psycopg2.extras import DictCursor

DB_HOST='localhost'
DB_NAME='post-bot'
DB_USER='postgres'
DB_PASS=''
DB_PORT=5432

DAYS_TO_KEEP_MESSAGES = 7

db = None

def connectDB():
  global db

  db = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)

def exec(query, *args):
  global db

  try:
    cur = db.cursor(cursor_factory=DictCursor)

    if args:
      cur.execute(query, args[0])
    else:
      cur.execute(query)

    db.commit()

    cur.close()
  except Exception as e:
    print(e)

def exec_fetch(query, *args):
  res = None
  
  with db.cursor(cursor_factory=DictCursor) as cur:
    cur = db.cursor(cursor_factory=DictCursor)

    if args:
      cur.execute(query, args[0])
    else:
      cur.execute(query)

    res = cur.fetchall()

  db.commit()

  return res

def initDB():
  exec('CREATE TABLE connectors (id SERIAL PRIMARY KEY, name varchar(32), owner_id integer, sources text[], destinations text[], rules text[])')

  exec('CREATE TABLE users (id SERIAL PRIMARY KEY, name varchar, telegram_id integer, active_connector integer, bitly_token text, site_id text, membership text, is_admin boolean, current_action text)')

  exec('CREATE TABLE messages (id SERIAL PRIMARY KEY, source_id integer, id_in_source integer, dest_id integer, id_in_dest integer, rules text[], message_date date)')

def addUser(id, name):
  try:
    exec('INSERT INTO users (name, telegram_id, membership, is_admin, active_connector, current_action) VALUES (%s, %s, %s, %s, %s, %s)', (name, id, 'all', False, 0, 'none',))

    return True
  except:
    return False

def updateUser(id, col, val):
  exec(f'UPDATE users SET {col} = %s WHERE telegram_id = %s', (val, id,))

def deleteOldMessages():
  exec('delete from messages where message_date < now() - interval %s', (f'{DAYS_TO_KEEP_MESSAGES} days',))

def closeDB():
  global db
  
  db.close()
