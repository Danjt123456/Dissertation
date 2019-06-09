from flask import Flask
import json

app = Flask('blockchainApp')



@app.route('/')
def all():
	getData()
	return "test"


def getData():
	print("testing")
	with open(Data.json, 'r') as f:
		data = f.read()

	data2 = json.loads(data)

	print(data)

app.run(debug=True)
