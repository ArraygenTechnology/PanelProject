import os
class Config(object):
    DEBUG = True
    TESTING = False
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'guess'
    UPLOAD_FOLDER = "app/static/uploads"
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = False
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', "csv", "xls", "xlsx"}
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://admin:Arraygen123$@paneldb.cpquggjyqqa1.ap-south-1.rds.amazonaws.com/panel_project_dev"
    #SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/panel_project"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'bioinformatics.arraygen.ak@gmail.com'
    MAIL_PASSWORD = 'arraygen123$'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_ASCII_ATTACHMENTS = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    pass

class TestingConfig(Config):
    pass
