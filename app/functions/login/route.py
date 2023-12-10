from .use_model import *
from . import login_blueprint

OAUTH2_CLIENT_ID = os.environ.get('OAUTH2_CLIENT_ID')
print(OAUTH2_CLIENT_ID)
OAUTH2_CLIENT_SECRET = os.environ.get('OAUTH2_CLIENT_SECRET')
OAUTH2_REDIRECT_URI = 'http://2306testflask.ddns.net/login/discord/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


google_blueprint = make_google_blueprint(
    client_id=os.environ.get('client_id'),
    client_secret=os.environ.get('client_secret'),
    scope=["https://www.googleapis.com/auth/userinfo.email", "openid",
           "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_url='/login'
)


def third_login_determine(email):
    result = sql_search(ufstr.users(), ufstr.star(), ufstr.email(), ufstr.db_string(email))
    if result:
        username = result.username
        user_id = result.id
        role = result.role
        user = User(user_id, username, role)
        login_user(user)
        next_url = request.args.get('next')
        if next_url == '/logout':
            next_url = None
        return redirect(next_url or '/')
    else:
        return redirect(f'/register/{email}')


@login_blueprint.route('/login/', methods=['get', 'post'])
def login():
    if google.authorized:
        resp = google.get("/oauth2/v2/userinfo")
        assert resp.ok, resp.text
        email = resp.json()["email"]
        return third_login_determine(email)
    if 'email' in session:
        email = session['email']
        session.pop('email', None)
        return third_login_determine(email)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_correct = sql_search('users', 'password', 'username', f'"{username}"', 'one')
        if password_correct:
            if check_password_hash(password_correct, password):
                user_id = sql_search('users', 'id', 'username', f'"{username}"', 'one')
                role = sql_search(ufstr.users(), ufstr.role(), ufstr.id(), user_id)
                user = User(user_id, username, role)
                login_user(user)
                next_url = request.args.get('next')
                if next_url == '/logout':
                    next_url = None
                return redirect(next_url or '/')
            else:
                return redirect('/redirect/密碼錯誤')
        else:
            return redirect('/redirect/使用者不存在')
    next_url = request.args.get('next')
    return render_template('login.html', url=next_url)


@login_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect('/redirect/登出成功')


@login_blueprint.route('/login/discord')
def discord_login():
    scope = request.args.get(
        'scope',
        'identify email')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


def discord_me():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    email = user['email']
    return email


@login_blueprint.route('/login/discord/callback')
def callback():
    if request.values.get('error'):
        return redirect('/redirect/登入失敗')
    discord = make_session(state=session.get('oauth2_state'))
    try:
        token = discord.fetch_token(
            TOKEN_URL,
            client_secret=OAUTH2_CLIENT_SECRET,
            authorization_response=request.url)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return redirect('/redirect/錯誤')

    session['oauth2_token'] = token
    session['email'] = discord_me()
    return redirect("/login")
