from app import create_app, host, port
import os

app = create_app()

if __name__ == '__main__':
    app.run()
