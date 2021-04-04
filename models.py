from peewee import Model
from peewee import IntegerField, TextField, DateTimeField
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


class AccountingRecords(BaseModel):
    accounting_id = IntegerField()
    user_id = IntegerField()
    price = IntegerField()
    paid_cash = IntegerField()
    datetime = DateTimeField()

    class Meta:
        table_name = 'accounting_records'


class IndividualAccountingRecords(BaseModel):
    user_id = IntegerField()
    datetime = DateTimeField()
    price = IntegerField()
    accounting_id = IntegerField()
    list_id = IntegerField()

    class Meta:
        table_name = "individual_accounting_records"
