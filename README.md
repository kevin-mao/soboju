# 2020 Virtual Campus Design Challenge
## Sobujo (The first social bullet journel)

### Installation
`$ git clone https://github.com/kevin-mao/sobujo.git`

### Environment setup and activation
```
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

### Running the app
```
$ python run.py
```

### Testing databse
Run inside python shell
```
from flaskblog import db
# will reset local db
db.create_all()

from flaskblog.models import User
User.query.all()
```