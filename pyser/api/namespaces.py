from flask_restplus.namespace import Namespace

ns_auth = Namespace('auth', description='Auth operations')
ns_blog = Namespace('blog', description='Blog operations')
ns_cfp = Namespace('cfp', description='Call for papers')
ns_cfs = Namespace('cfs', description='Call for sponsors')
ns_email = Namespace('email', description='Email operations')
ns_event = Namespace('event', description='Event operations')
ns_gallery = Namespace('gallery', description='Gallery operations')
ns_hall = Namespace('hall', description='Hall operations')
ns_me = Namespace('me', description='Me operations')
ns_talk = Namespace('talk', description='Task operations')
ns_user = Namespace('users', description='User operations')

namespaces = [
    ns_auth,
    ns_blog,
    ns_cfp,
    ns_cfs,
    ns_email,
    ns_event,
    ns_gallery,
    ns_hall,
    ns_me,
    ns_talk,
    ns_user,
]
