from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/api/users')
def get_users():
    return{
        'users' : [
            {
                'id': 1,
                'name':'Arnau'
            },
            {
                'id': 2,
                'name':'Eloi'
            },
            {
                'id': 3,
                'name':'Miquel'
            }
        ]
    } 

if __name__ == '__main__':
    app.run(debug=True) # port 5000 per defecte
