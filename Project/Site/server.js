const express = require('express')
const cors = require('cors')
const app = express()
const path = require('path');
const ip = require('ip');
const curIP = ip.address();
const fs = require('fs');
const XMLHttpRequest = require('xmlhttprequest').XMLHttpRequest;

app.use(express.static(path.join(__dirname, 'public')));

const port = 3000;

// Basic HTML page hosting
app.get('/', function(req, res) {
	res.sendFile(path.join(__dirname + '/index.html'));
});

app.get('/home2', function(req, res) {
	res.sendFile(path.join(__dirname + '/index.html'));
});

app.get('/vote', function(req, res) {
	res.sendFile(path.join(__dirname + '/public/vote.html'));
});

app.get('/results', function(req, res) {
	res.sendFile(path.join(__dirname + '/public/results.html'));
});

app.get('/connect', function(req, res) {
	res.sendFile(path.join(__dirname + '/public/connect.html'));
});

app.get('/admin', function(req, res) {
	res.sendFile(path.join(__dirname + '/public/admin.html'));
});






app.get('/chain', function(req, res) {
	var xmlhttp2 = new XMLHttpRequest();

	var reqNode = req.query.address;
	var url = reqNode + '/chain';
	var data = [];

	xmlhttp2.onreadystatechange = function() {
		if (this.readyState == 4) {
			data = JSON.parse(this.responseText);
			res.send(data);
		}
	}

	xmlhttp2.open("GET", url, true);
	xmlhttp2.send();
});


app.get('/getnodelist', function(req, res) {
	var data = fs.createReadStream(path.join(__dirname + '/public/nodeList.json'));
	data.pipe(res);
});

app.post('/submitVote', function(req, res) {
	var response = sendVote(req.query.sender, req.query.vote)

	res.send(response)
});

app.post('/registernode', function(req, res) {
	var nameVal = req.query.name;
	var ipVal = fullIp(req.query.ip, req.query.port);

	var newEntry = {
		'ip': ipVal,
		'nameVal': nameVal
	};


	var nodeListFile = path.join(__dirname + '/public/nodeList.json');

	fs.readFile(nodeListFile, function(err, content) {
		if (err) throw err;
		var parseJson = JSON.parse(content);
		parseJson.push(newEntry);
		sendAddresses(parseJson);

		fs.writeFile(nodeListFile, JSON.stringify(parseJson), function(err) {
			if (err) throw err;
		})
	});



	res.send('added'), 200
});


app.post('/clearnodelist', function(req, res) {
	var nodeListFile = path.join(__dirname + '/public/nodeList.json');
	fs.writeFileSync(nodeListFile, '[]', {
		encoding: 'utf8',
		flag: 'w'
	});

	res.send('Node List Cleared')
});


app.get('/getData', function(req, res) {

	var xmlhttp2 = new XMLHttpRequest();

	var reqNode = req.query.node;
	var url = reqNode + '/getdata';

	var data = [];

	xmlhttp2.onreadystatechange = function() {
		if (this.readyState == 4) {
			data = JSON.parse(this.responseText);
			res.send(data);

		}
	}

	xmlhttp2.open("GET", url, true);
	xmlhttp2.send();

});


app.get('/toBeMined', function(req, res) {

	var xmlhttp2 = new XMLHttpRequest();

	var reqNode = req.query.address;
	var url = reqNode + '/tobemined';
	var data = [];

	xmlhttp2.onreadystatechange = function() {
		if (this.readyState == 4) {
			data = JSON.parse(this.responseText);

			res.send(data);

		}
	}

	xmlhttp2.open("GET", url, true);
	xmlhttp2.send();

});


app.post('/setupchain', function(req, res) {

	var xmlhttp2 = new XMLHttpRequest();

	var reqNode = req.query.address;
	var url = reqNode + '/setupchain';

	var data = [];

	xmlhttp2.onreadystatechange = function() {
		if (this.readyState == 4) {
			data = JSON.parse(this.responseText);

			res.send(data);

		}
	}

	xmlhttp2.open("POST", url, true);
	xmlhttp2.send();

});

app.post('/verify', function(req, res) {

	var xmlhttp2 = new XMLHttpRequest();

	var reqNode = req.query.address;
	var url = reqNode + '/verifychain';

	var data = [];

	xmlhttp2.onreadystatechange = function() {
		if (this.readyState == 4) {

			data = JSON.parse(this.responseText);
			res.send(data);

		}
	}

	xmlhttp2.open("GET", url, true);
	xmlhttp2.send();

});


app.post('/resolve', function(req, res) {

	var xmlhttp2 = new XMLHttpRequest();

	var reqNode = req.query.address;
	var url = reqNode + '/nodes/resolve';

	var data = [];

	xmlhttp2.onreadystatechange = function() {
		if (this.readyState == 4) {
			data = JSON.parse(this.responseText);

			res.send(data);

		}
	}

	xmlhttp2.open("GET", url, true);
	xmlhttp2.send();

});

app.post('/resolveAll', function(req, res) {


	var rawNodes = JSON.parse(fs.readFileSync(path.join(__dirname + '/public/nodeList.json')));
	var nodes = []
	for (i = 0; i < rawNodes.length; i++) {
		if (nodes.indexOf(rawNodes[i].ip) === -1) {
			nodes.push(rawNodes[i].ip);
		}
	}

	var i = 0;
	while (i < nodes.length) {
		var xmlhttp2 = new XMLHttpRequest();
		var url = nodes[i] + '/nodes/resolve'

		xmlhttp2.open("GET", url, false);
		xmlhttp2.send();
		i += 1;
	}
	res.send('Resolve All Comand given');
});



app.get('/mine', function(req, res) {


	var rawNodes = JSON.parse(fs.readFileSync(path.join(__dirname + '/public/nodeList.json')));
	var nodes = []
	for (i = 0; i < rawNodes.length; i++) {
		if (nodes.indexOf(rawNodes[i].ip) === -1) {
			nodes.push(rawNodes[i].ip);
		}
	}

	var i = 0;
	while (i < nodes.length) {
		var xmlhttp2 = new XMLHttpRequest();
		var url = nodes[i] + '/mine'

		xmlhttp2.onreadystatechange = function() {
			if (this.readyState == 4) {

			}
		}

		xmlhttp2.open("GET", url, true);
		xmlhttp2.send();
		i += 1;
	}
	res.send('Mine Comands given');
});


app.post('/breakChain', function(req, res) {

	var xmlhttp2 = new XMLHttpRequest();

	var reqNode = req.query.address;
	var url = reqNode + '/breakchain';

	var data = [];

	xmlhttp2.onreadystatechange = function() {
		if (this.readyState == 4) {
			res.send(this.responseText);
		}
	}

	xmlhttp2.open("GET", url, true);
	xmlhttp2.send();

});

app.post('/resetChain', function(req, res) {

	var xmlhttp2 = new XMLHttpRequest();

	var reqNode = req.query.address;
	var url = reqNode + '/resetchain';

	var data = [];

	xmlhttp2.onreadystatechange = function() {
		if (this.readyState == 4) {

			res.send(this.responseText);
		}
	}

	xmlhttp2.open("POST", url, true);
	xmlhttp2.send();

});




function fullIp(ip, port) {
	var fullIp = 'http://' + ip + ':' + port;
	return fullIp
}


function sendAddresses(json) {
	if (json.length > 1) {
		for (i = 0; i < json.length; i++) {
			url = json[i].ip + '/nodes/register?address=' + json[json.length - 1].ip;

			const xmlHttp = new XMLHttpRequest();
			xmlHttp.open("POST", url, false);
			xmlHttp.send();

			xmlHttp.onreadystatechane = function() {}
		}
	}
}


function sendVote(sender, vote) {
	var rawNodes = JSON.parse(fs.readFileSync(path.join(__dirname + '/public/nodeList.json')));
	var nodes = []
	for (i = 0; i < rawNodes.length; i++) {
		if (nodes.indexOf(rawNodes[i].ip) === -1) {
			nodes.push(rawNodes[i].ip);
		}
	}


	var statusCodes = [];
	var i = 0
	while (i < nodes.length) {
		var xmlhttp2 = new XMLHttpRequest();
		var reqNode = nodes[i];
		var params = '/transactions/new?sender=' + sender + '&vote=' + vote;
		var url = reqNode + params;
		console.log('sending' + url);

		var data = [];


		xmlhttp2.onreadystatechange = function() {
			if (this.readyState == 4) {
				statusCodes.push(this.status);

			}
		}

		xmlhttp2.open("POST", url, false);
		xmlhttp2.send();

		i += 1;
	}


	var numNodes = nodes.length;
	var numAccepted = 0;
	var k = 0
	while (k < statusCodes.length) {
		if (statusCodes[k] == 201) {
			numAccepted += 1;
		}
		k += 1;
	}

	var numNoResponse = 0;
	var l = 0
	while (l < statusCodes.length) {
		if (statusCodes[l] == 0) {
			numNoResponse += 1;
		}
		l += 1;
	}

	return {
		'numNodes': (numNodes - numNoResponse),
		'numAccepted': numAccepted
	};
}


app.listen(port, () => console.log(`Example app listening on port ${port} at local ${curIP}`));
