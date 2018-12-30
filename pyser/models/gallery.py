from peewee import ForeignKeyField, TextField

from ..db import db
from .event import Event

Model = db.Model


class GalleryAlbum(Model):
    event = ForeignKeyField(Event, related_name='albums', null=True)
    name = TextField(index=True)


class GalleryFile(Model):
    album = ForeignKeyField(GalleryAlbum, related_name='files')
    filename = TextField(index=True)

    def url(self, prefix=''):
        return f'{prefix}/{self.album.event.year}/{self.album.name}/{self.filename}'

    def path(self, prefix):
        return f'{prefix}/{self.album.event.year}/{self.album.name}/{self.filename}'
