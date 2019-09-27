from flask_security import RoleMixin, UserMixin
from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    TextField
)

from ..db import db

Model = db.Model


class Role(Model, RoleMixin):
    description = TextField(null=True)
    name = CharField(unique=True)


class User(Model, UserMixin):
    class Meta:
        table_name = 'users'

    active = BooleanField(default=True)
    admin = BooleanField(default=False)
    bio = TextField()
    confirmed_at = DateTimeField(null=True)
    email = TextField()
    facebook = TextField()
    firstName = TextField()
    lastName = TextField()
    password = TextField()
    twitter = TextField()
    volunteer = BooleanField(null=True)


class UserRoles(Model):
    description = property(lambda self: self.role.description)
    name = property(lambda self: self.role.name)
    role = ForeignKeyField(Role, related_name='users')
    user = ForeignKeyField(User, related_name='roles')
