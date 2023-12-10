from app import create_app, host, port
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host=host, port=port)
