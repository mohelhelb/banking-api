from app import create_app
from config_app import ConfigDevelopment

app = create_app(config_obj=ConfigDevelopment)

if __name__ == "__main__":
    app.run()
