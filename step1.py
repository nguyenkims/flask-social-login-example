import flask

app = flask.Flask(__name__)

@app.route("/")
def index():
    return """
    <a href="/login">Login with SimpleLogin</a>
    """

if __name__ == '__main__':
    app.run(debug=True)