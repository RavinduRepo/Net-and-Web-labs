const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");



const app = express();
app.use(bodyParser.json());  
  
const DATA_FILE =  "data.json";  
       
function readData() {
    return JSON.parse(fs.readFileSync(DATA_FILE));
}



function writeData(data) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 4)); 
}     


// get all users
app.get("/users", (req, res) => res.json(readData()));

// get one user by ID
app.get("/users/:id", (req, res) => {
    const users = readData();
    const user = users.find(u => u.id === parseInt(req.params.id));
    user ? res.json(user) : res.status(404).json({ error: "User not found" });   
});

// make a new user
app.post("/users", (req, res) => { 
    const users = readData(); 
    const newUser = { id: users.length + 1, ...req.body };  
    users.push(newUser);
    writeData(users);  
    res.status(201).json(newUser);  

});

// update user details
app.put("/users/:id", (req, res) => {
    const users = readData();
    const index = users.findIndex(u => u.id === parseInt(req.params.id)); 
    if (index === -1) return res.status(404).json({ error: "User not found" });  

    users[index] = { ...users[index], ...req.body }; 
    writeData(users);
    res.json(users[index]);
});

// del a user
app.delete("/users/:id", (req, res) => {
    let users = readData();  
    users = users.filter(u => u.id !== parseInt(req.params.id));
    writeData(users); 
    res.json({ message: "User deleted" }); 
     
});
 
app.listen(3000, () => console.log("Server running on http://localhost:3000")); 
 

