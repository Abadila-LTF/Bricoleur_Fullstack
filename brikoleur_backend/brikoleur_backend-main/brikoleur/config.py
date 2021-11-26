# config.py

#dev
MYSQL_HOST = 'database-1.cdyguxgp6lky.eu-west-3.rds.amazonaws.com' 
MYSQL_USERNAME = 'reda'
MYSQL_PASSWORD = 'ef7zgHFRoln9i8dRLWUS'
MYSQL_DATABASE = 'brikoleur'
MYSQL_PORT = '3307'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'+MYSQL_USERNAME+':'+MYSQL_PASSWORD+'@'+MYSQL_HOST+':'+MYSQL_PORT+'/'+MYSQL_DATABASE
SERVER_HOST = '0.0.0.0'
KEY_JWT = 'mySecret'  # Prod
MAIL_SERVER = 'smtp.gmail.com'
MAIL_USERNAME = 'redaabdou49@gmail.com'
MAIL_PASSWORD = 'hblnjyhikjcddhli'