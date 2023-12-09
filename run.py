from app import create_app, host, port

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host=host, port=port)
