import sys

from marshmallow import fields

from .base import BaseSchema
from .event import EventSchema
from .paging import PageOutSchema


class HallSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    name = fields.String(description='Hall name')
    event = fields.Nested(EventSchema, dump_only=True)


PageOutSchema(HallSchema, sys.modules[__name__])
