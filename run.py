from app.routes import main
from flask import Flask

app = Flask(__name__)
app.secret_key = "01849347859f77cc69e6066da70d2a2b3f67bf9b649d98a878d6ee4b76bc3b5e"

app.register_blueprint(main)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
