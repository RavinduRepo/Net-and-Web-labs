const fs = require("fs");
const express = require("express");

const app = express();

app.get("/users", (req, res) => {
    fs.readFile("users.txt", "utf8", (err, data) => {
        if (err) {
            res.status(500).json({ error: "Error reading file" });
            return;
        }
        const users = data.split("\n").map(line => {
            const [name, email] = line.split(",");
            return { name, email };
        });
        res.json(users);
    });
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));
