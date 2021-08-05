const { Client } = require('pg');

DBUSER = process.env.DBUSER;
DBPASS = process.env.DBPASS;
DBHOST = process.env.DBHOST;
DBPORT = process.env.DBPORT;
DBNAME = process.env.DBNAME;

let client = new Client({
  user: DBUSER,
  host: DBHOST,
  database: DBNAME,
  password: DBPASS,
  port: Number(DBPORT),
  // ssl: {
  //   rejectUnauthorized: false,
  // },
});

exports.connect = () => {
  client.connect();
};

exports.exec = async (str, params) => {
  if (!params) {
    params = [];
  }

  let data = null;

  await client
    .query(str, params)
    .then((res) => (data = res.rows))
    .catch((err) => console.log(err));

  return data;
};
