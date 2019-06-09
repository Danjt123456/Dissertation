const express = require('express')
const app = express()
const path = require('path');
const ip = require('ip');
const curIP = ip.address();
const fs = require('fs');

app.use(express.static(path.join(__dirname,'public')));

const port = 3000;

app.get('/', function(req, res) {
res.sendFile(path.join(__dirname + '/index.html'));
});

app.get('/home', function(req, res) {
res.sendFile(path.join(__dirname + '/index.html'));
});

app.get('/vote', function(req, res) {
res.sendFile(path.join(__dirname + '/public/vote.html'));
});

app.get('/results', function(req, res) {
res.sendFile(path.join(__dirname + '/public/results.html'));
});

app.get('/getdata', function(req, res) {
	console.log(req.query.ip);
	getNodeData(req.query.ip);
var data = fs.createReadStream(path.join(__dirname + '/../Node/Data.json'));
data.pipe(res);
});

app.get('/getnodelist', function(req, res) {
var data = fs.createReadStream(path.join(__dirname + '/public/nodeList.json'));
data.pipe(res);
});

app.listen(port, () => console.log(`Example app listening on port ${port} at local ${curIP}`));





function getNodeData(ip) {
	console.log("here test " + ip);
}



