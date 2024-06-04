import os
from app import create_app

config = os.environ.get("CONFIG") or "default"
app = create_app(config)

if __name__ == "__main__":
    app.run()