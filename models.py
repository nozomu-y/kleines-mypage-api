from peewee import Model
from peewee import IntegerField, TextField
import dbconnect

dbconnect.db.connect()


class BaseModel(Model):
    class Meta:
        database = dbconnect.db


class Profiles(BaseModel):
    user_id = IntegerField()
    last_name = TextField()
    first_name = TextField()
    name_kana = TextField()
    grade = IntegerField()
    part = TextField()

    class Meta:
        table_name = 'profiles'


class Users(BaseModel):
    user_id = IntegerField()
    email = TextField()
    password = TextField()
    status = TextField()

    class Meta:
        table_name = 'users'
