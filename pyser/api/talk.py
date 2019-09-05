from urllib.parse import parse_qs, urlparse

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_rest_api import Blueprint, abort

from ..models.auth import User
from ..models.event import Event
from ..models.talk import Talk
from ..schemas.paging import PageInSchema, PageOutSchema, paginate
from ..schemas.talk import TalkSchema
from .methodviews import ProtectedMethodView

announce_subject = '[PySer] Your talk is {}accepted'
announce_message = """
Congratulation,

Your talk titled

"{}"

is accepted. See you at the conference!

Please review the schedule and contact us in the next 3 days if you can't
present at {}.

Regards,
PySer conference
"""

reject_message = """
Hello,

We're sorry to inform you that your talk

"{}"

is not accepted. We wish you more luck next time!

Regards,
PySer conference
"""

blueprint = Blueprint('user', 'user')


@blueprint.route('/year/<year_id>', endpoint='talks')
class TalkListAPI(ProtectedMethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(PageOutSchema(TalkSchema))
    def get(self, pagination, year_id):
        """Get list of talks"""
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            abort(404, message='No such event')
        return paginate(event.talks.order_by(Talk.start), pagination)

    @jwt_required
    @blueprint.arguments(TalkSchema)
    @blueprint.response(TalkSchema)
    def post(self, args, year_id):
        """Create new talk"""
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            abort(404, message='No such event')
        talk = Talk(**args)
        if not user.admin:
            talk.user = user
        else:
            try:
                talk_user = talk.user
                try:
                    talk.user = User.get(email=talk_user.email)
                except User.DoesNotExist:
                    abort(404, message='User not found')
            except User.DoesNotExist:
                talk.user = user
        talk.event = event
        talk.save()
        return talk


@blueprint.route('/year/<year_id>/user', endpoint='talks_user')
class UserTalkListAPI(ProtectedMethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(PageOutSchema(TalkSchema))
    def get(self, pagination, year_id):
        """Get list of talks by user"""
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            abort(404, message='No such event')
        allTalks = event.talks.join(User).where(Talk.user == user)
        query = allTalks.order_by(Talk.start)
        return paginate(query, pagination)


@blueprint.route('/year/<year_id>/published', endpoint='talks_published')
class PublishedTalkListAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(PageOutSchema(TalkSchema))
    def get(self, pagination, year_id):
        """Get list of talks"""
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            abort(404, message='No such event')
        query = event.talks.where(Talk.published).order_by(Talk.start)
        return paginate(query, pagination)


@blueprint.route('/year/<year_id>/announce', endpoint='talks_announce')
class AnnounceTalkListAPI(ProtectedMethodView):
    def post(self, year_id):
        """Announce the talks"""
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        username = current_app.config.get('MAIL_USERNAME', None)
        password = current_app.config.get('MAIL_PASSWORD', None)
        host = current_app.config.get('MAIL_SERVER', None)
        port = current_app.config.get('MAIL_PORT', 25)
        for talk in event.talks.where(Talk.published):
            text = announce_message.format(talk.title, talk.start)
            subject = announce_subject.format('')
            #  try:
            #  error = send_mail(
            #  'office@pyser.org',
            #  talk.user.email,
            #  subject,
            #  text,
            #  username,
            #  password,
            #  host,
            #  port,
            #  )
            #  except Exception:
            #  pass
        for talk in event.talks.where(Talk.published == False):
            text = reject_message.format(talk.title)
            subject = announce_subject.format('not ')
            try:
                error = send_mail(
                    'office@pyser.org',
                    talk.user.email,
                    subject,
                    text,
                    username,
                    password,
                    host,
                    port,
                )
            except Exception:
                pass
        return {'message': 'OK'}


@blueprint.route('/<talk_id>', endpoint='talk')
class TalkDetailAPI(MethodView):
    @blueprint.response(TalkSchema)
    def get(self, talk_id):
        """Get talk details"""
        try:
            talk = Talk.get(id=talk_id)
        except Talk.DoesNotExist:
            abort(404, message='No such talk')
        return talk

    @jwt_required
    @blueprint.arguments(TalkSchema(partial=True))
    @blueprint.response(TalkSchema)
    def patch(self, args, talk_id):
        """Edit talk"""
        try:
            User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            talk = Talk.get(id=talk_id)
        except Talk.DoesNotExist:
            abort(404, message='No such talk')
        for field in args:
            setattr(talk, field, args[field])
        video = getattr(args, 'video', None)
        if video is not None:
            url = urlparse(video)
            video_args = parse_qs(url.query)
            video_id = video_args.get('v', None)
            if video_id is None:
                abort(409, message='Wrong URL')
            talk.video = video_id[0]
        talk.save()
        return talk

    @jwt_required
    @blueprint.response(TalkSchema)
    def delete(self, talk_id):
        """Delete talk"""
        try:
            User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            talk = Talk.get(id=talk_id)
        except Talk.DoesNotExist:
            abort(404, message='No such talk')
        talk.delete_instance()
        return talk
