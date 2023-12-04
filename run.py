from app import create_app, host, port
from mysql.connector import connect

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host=host, port=port)
