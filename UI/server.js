const express = require('express');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: './config/config.env' });

const db = require('./db/db');

const app = express();

app.use(express.json());

db.connect();

app.use(express.static('client'));

app.use('/api/v1/connectors', require('./routes/connectors'));
app.use('/api/v1/auth', require('./routes/auth'));

app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'client', 'index.html'));
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => console.log(`server running on port ${PORT}`));
