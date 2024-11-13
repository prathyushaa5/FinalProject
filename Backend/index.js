const express = require('express');
const session = require('express-session');
const app = express();

const cors = require('cors');
const conn = require('./config/db');

// Configure CORS to allow requests from your frontend
app.use(cors({
  origin: 'http://localhost:8080', // Replace with your frontend's origin
  credentials: true // If your frontend makes requests with credentials (like cookies or sessions)
}));

app.get('/', (req, res) => res.send('API Running'));

// Connect to database
conn.connectDB();

// Init Middleware for parsing JSON
app.use(express.json());

app.get('/test_api', async function(req, res) {
    await conn.query('SELECT * from users', async function(error, results) {
        if (error) {
            res.writeHead(200, {
                'Content-Type': 'text/plain'
            });
            res.send(error.code);
        } else {
            res.writeHead(200, {
                'Content-Type': 'application/json'
            });
            res.end(JSON.stringify(results));
        }
    });
});

// Define Routes
app.use('/api', require('./routes/UserRoute'));
app.use('/exercise', require('./routes/ExerciseRoute'));
app.use('/email', require('./routes/EmailRoute'));

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => console.log(`Server started on port ${PORT}`));

module.exports = app;
