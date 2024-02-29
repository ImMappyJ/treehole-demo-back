# How To Use

- Edit your own configuration in config.py

>IP = "localhost" # Your MySQL Address
>
>PORT = 3306 # Your MySQL PORT
>
>USER = "root" # Your MySQL User
>
>PWD = "123456" # Your MySQL Password
>
>NAME = "TreeHole" # The Schema Name
>
>SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USER}:{PWD}@{IP}:{PORT}/{NAME}?charset=utf8mb4" # Connect URL
>
>MAIL_SERVER = "smtp.exmail.qq.com" # SMTP Service Provider
>
>MAIL_PORT = 465 # SMTP PORT
>
>MAIL_USE_SSL = True # Whether Use SSL
>
>MAIL_DEFAULT_SENDER = 'treehole@funworld.cc' # Your Mail
>
>MAIL_USERNAME = "treehole@funworld.cc" # Your SMTP User Name
>
>MAIL_PASSWORD = "" # Your SMTP Password Here

- Execuse the flask-migration command by order

```
python -m flask db init

python -m flask db migrate

python -m flask db update
```

- Then the demo can run in your environment
