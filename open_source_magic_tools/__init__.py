from flask import Flask
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configure the application
    app.config.from_object('open_source_magic_tools.config')

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Set the template folder explicitly
    app.template_folder = os.path.join(app.root_path, 'templates')

    # Set the static folder explicitly (Assuming static is at the root level)
    # Construct the path relative to the directory containing the package
    app.static_folder = os.path.join(os.path.dirname(app.root_path), 'static')


    app.secret_key = 'your_secret_key'

    # Import and register blueprints or routes here
    from . import routes
    app.register_blueprint(routes.bp)

    return app