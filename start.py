from app import app

ssl_context = (
    './ssl/fullchain.pem',
    './ssl/key.pem'
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context=ssl_context, debug=False)


