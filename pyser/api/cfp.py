from flask import current_app, request
from flask_restplus import Resource, abort
from .namespaces import ns_cfp
from .schemas import CfPSchema, TalkSchema
from ..models.auth import User
from ..models.event import Event
from ..utils import send_mail


message_format = """
Details: {referrer}/{talk.id}

First Name: {person.firstName}
Last Name: {person.lastName}
Email: {person.email}
Twitter: {person.twitter}
Facebook: {person.facebook}
Bio:
{person.bio}


Title: {talk.title}
Hall: {talk.hall}
Duration: {talk.duration}min
Description:
{talk.description}
"""

subject_format = "[CfP] {}"


@ns_cfp.route('', endpoint='cfp')
class CfpAPI(Resource):
    @ns_cfp.response(409, 'Invalid data')
    def post(self):
        """Authenticates and generates a token."""
        schema = CfPSchema()
        cfp, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        username = current_app.config.get('MAIL_USER', None)
        password = current_app.config.get('MAIL_PASSWORD', None)
        host = current_app.config.get('MAIL_SERVER', None)
        to = current_app.config.get('MAIL_ADDRESS', None)
        subject = subject_format.format(cfp.talk.title)
        fromAddress = cfp.person.email
        try:
            cfp.person = User.get(email=cfp.person.email)
        except User.DoesNotExist:
            cfp.person.save()
        cfp.talk.event = Event.select().order_by(Event.year)[0]
        cfp.talk.user = cfp.person
        cfp.talk.save()
        text = message_format.format(
            talk=cfp.talk,
            person=cfp.person,
            referrer=request.referrer,
        )
        error = send_mail(fromAddress, to, subject, text, username, password, host)
        if error:
            return {'message': 'Unable to send email'}, 409
        schema = TalkSchema()
        response, errors = schema.dump(cfp.talk)
        if errors:
            return errors, 409
        return response