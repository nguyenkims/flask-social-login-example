import os

import flask
import requests_oauthlib
from dotenv import load_dotenv

# Glitch url https://nguyenkims-flask-social-login-example.glitch.me
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

load_dotenv()
URL = "https://nguyenkims-flask-social-login-example.glitch.me"

# SimpleLogin config
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

AUTHORIZATION_BASE_URL = "https://app.simplelogin.io/oauth2/authorize"
TOKEN_URL = "https://app.simplelogin.io/oauth2/token"
USERINFO_URL = "https://app.simplelogin.io/oauth2/userinfo"

# Facebook Config
FB_CLIENT_ID = os.environ.get("FB_CLIENT_ID")
FB_CLIENT_SECRET = os.environ.get("FB_CLIENT_SECRET")

FB_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

FB_SCOPE = ["email"]

# This allows us to use a plain HTTP callback
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = flask.Flask(__name__)


@app.route("/")
def index():
    return flask.render_template("login.html")


# <<< SimpleLogin endpoints >>>
@app.route("/login")
def login():
    simplelogin = requests_oauthlib.OAuth2Session(
        CLIENT_ID, redirect_uri=URL + "/callback"
    )
    authorization_url, _ = simplelogin.authorization_url(AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)


@app.route("/callback")
def callback():
    simplelogin = requests_oauthlib.OAuth2Session(CLIENT_ID)
    simplelogin.fetch_token(
        TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=flask.request.url
    )

    user_info = simplelogin.get(USERINFO_URL).json()
    name = user_info["name"]
    email = user_info["email"]
    avatar_url = user_info.get("avatar_url")
    return flask.render_template(
        "user_info.html",
        name=name,
        email=email,
        avatar_url=avatar_url,
        provider="Simple Login",
    )


# <<< Facebook endpoints >>>
@app.route("/fb-login")
def fb_login():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, redirect_uri=URL + "/fb-callback", scope=FB_SCOPE
    )
    authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)


@app.route("/fb-callback")
def fb_callback():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, scope=FB_SCOPE, redirect_uri=URL + "/fb-callback"
    )

    # we need to apply a fix for Facebook here
    facebook = facebook_compliance_fix(facebook)

    facebook.fetch_token(
        FB_TOKEN_URL,
        client_secret=FB_CLIENT_SECRET,
        authorization_response=URL + flask.request.full_path,
    )

    # Fetch a protected resource, i.e. user profile, via Graph API

    facebook_user_data = facebook.get(
        "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
    ).json()

    email = facebook_user_data.get("email")
    name = facebook_user_data["name"]
    avatar_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")

    return flask.render_template(
        "user_info.html",
        name=name,
        email=email,
        avatar_url=avatar_url,
        provider="Facebook",
    )


if __name__ == "__main__":
    app.run(debug=True)
