from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    temp_url = "https://thingsboard.cs.cf.ac.uk/dashboard/9c597b10-0b04-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2" 
    humid_url = "https://thingsboard.cs.cf.ac.uk/dashboard/74d87180-0dbc-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2"
    return render_template('index.html', temp_url=temp_url, humid_url = humid_url)

if __name__ == '__main__':
    app.run(debug=True)

    