import flask
import requests_oauthlib
import os

from requests_oauthlib.compliance_fixes import facebook_compliance_fix

# Your ngrok url, obtained after running "ngrok http 5000"
URL = "https://679e4c83.ngrok.io"

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

SCOPE = ["email"]

# This allows us to use a plain HTTP callback
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = flask.Flask(__name__)


@app.route("/")
def index():
    return """
    <a href="/login">Login with Facebook</a>
    """


@app.route("/login")
def login():
    facebook = requests_oauthlib.OAuth2Session(
        CLIENT_ID, redirect_uri=URL + "/callback", scope=SCOPE
    )
    authorization_url, _ = facebook.authorization_url(AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)


@app.route("/callback")
def callback():
    facebook = requests_oauthlib.OAuth2Session(
        CLIENT_ID, scope=SCOPE, redirect_uri=URL + "/callback"
    )

    # we need to apply a fix for Facebook here
    facebook = facebook_compliance_fix(facebook)

    facebook.fetch_token(
        TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=flask.request.url
    )

    # Fetch a protected resource, i.e. user profile, via Graph API

    facebook_user_data = facebook.get(
        "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
    ).json()

    email = facebook_user_data["email"]
    name = facebook_user_data["name"]
    picture_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")
    
    return f"""
    User information: <br>
    Name: {name} <br>
    Email: {email} <br>
    Avatar <img src="{picture_url}"> <br>
    <a href="/">Home</a>
    """


if __name__ == "__main__":
    app.run(debug=True)
