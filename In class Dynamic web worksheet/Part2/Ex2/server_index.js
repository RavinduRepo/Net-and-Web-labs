const express = require('express');
const path = require('path');

const app = express();
const port = 5500;

app.use(express.urlencoded({ extended: true })); // To parse URL-encoded bodies

// Serve static files from the current directory
app.use(express.static(__dirname));

// Serve the HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'form.html')); // sends the form.html file to the client to display the form
});

// Route to accept form submission and display the greeting
app.post('/greet', (req, res) => {
    const name = req.body.name || 'Guest';
    console.log("request received");
    res.send(`Hello, ${name}!`);
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});