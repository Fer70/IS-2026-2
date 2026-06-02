from flask import Flask, jsonify, session
from sqlalchemy import URL
import os
from flask_login import LoginManager, current_user
from alchemyClasses import db
from alchemyClasses.Administrador import Administrador
from alchemyClasses.Alumno import Alumno
from alchemyClasses.Profesor import Profesor
from alchemyClasses.Usuario import Usuario
from alchemyClasses.CursoMaterial import CursoMaterial
from alchemyClasses.Curso import Curso
from alchemyClasses.CursoAlumno import CursoAlumno
from alchemyClasses.Usuario import Usuario
from auth import auth_bp
from home import home_bp
from role_views import role_views_bp
from admin import admin_bp
from profe import profe_bp
from alumno import alumno_bp
from werkzeug.security import generate_password_hash
from flask import send_from_directory




def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
        drivername="mysql+pymysql",
        username="root",  # Cambiar a su usuario de MySQL
        password="bolillo70",  # Cambiar a su contraseña de MySQL
        host="localhost",
        port=3306, # Cambiar al puerto de MySQL si es diferente
        database="cursos"  # Cambiar a su base de datos de MySQL
    )
    app.config.from_mapping(SECRET_KEY="dev")
    db.init_app(app)
    @app.context_processor
    def inject_user():
        return dict(user=session.get("user"))
    
    @app.route("/materials/<filename>")
    def ver_material(filename):

        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            filename
        )
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(role_views_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profe_bp)
    app.register_blueprint(alumno_bp)

    UPLOAD_FOLDER = "uploads/materials"

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    """with app.app_context():

        admin = Usuario(
            nombre_usuario="admin",
            contrasena_usuario=generate_password_hash("admin123"),
            rol="admin"
        )

        db.session.add(admin)
        db.session.commit()

    print("Admin creado")"""

    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
