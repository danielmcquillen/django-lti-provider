from hashlib import sha1

from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from nameparser import HumanName
from pylti.common import LTIException

import logging
logger = logging.getLogger(__name__)


class LTIBackend(object):

    def create_user(self, request, lti, username):
        # create the user if necessary
        logger.info(f"LTIBackend: create_user() with username: {username}")
        user = User(username=username, password='LTI user')
        user.set_unusable_password()
        user.email = lti.user_email(request) or ''

        name = HumanName(lti.user_fullname(request))

        logger.info(f"LTIBackend: create_user() name: {name}")
        user.first_name = name.first[:30]
        logger.info(f"LTIBackend: create_user() first_name: {user.first_name}")
        user.last_name = name.last[:30]
        logger.info(f"LTIBackend: create_user() last_name: {user.last_name}")

        user.save()
        return user

    def get_hashed_username(self, request, lti):
        # (http://developers.imsglobal.org/userid.html)
        # generate a username to avoid overlap with existing system usernames
        # sha1 hash result + trunc to 30 chars should result in a valid
        # username with low-ish-chance of collisions
        logger.info(f"LTIBackend(): get_hashed_username() lti.consumer_user_id(request): {lti.consumer_user_id(request)}")
        uid = force_bytes(lti.consumer_user_id(request))
        result = sha1(uid).hexdigest()[:30]
        logger.info(f"LTIBackend(): get_hashed_username() result: {result}")
        return result

    def get_username(self, request, lti):
        logger.info(f"LTIBackend: get_username()...")
        username = lti.user_identifier(request)
        logger.info(f"LTIBackend: get_username() username {username}")
        if not username:
            logger.info(f"LTIBackend: get_username() no username so called get_hashed_username")
            username = self.get_hashed_username(request, lti)
            logger.info(f"LTIBackend: get_username() username is now {username}")
        return username

    def find_user(self, request, lti):
        # find the user via lms identifier first
        logger.info(f"LTIBackend: find_user() looking for user using username {lti.user_identifier(request)}")
        user = User.objects.filter(
            username=lti.user_identifier(request)).first()

        # find the user via email address, if it exists
        email = lti.user_email(request)
        if user is None and email:
            logger.info(f"LTIBackend: find_user() Couldn't find user, looking via email {email}")
            user = User.objects.filter(email=email).first()

        if user is None:
            # find the user via hashed username
            username = self.get_hashed_username(request, lti)
            logger.info(f"LTIBackend: find_user() Couldn't find user, looking via hashed username {username}")
            user = User.objects.filter(username=username).first()

        return user

    def find_or_create_user(self, request, lti):
        logger.info("LTIBackend: find_or_create_user()")
        user = self.find_user(request, lti)
        if user is None:
            logger.info("LTIBackend: find_or_create_user() user was None")
            username = self.get_username(request, lti)
            logger.info(f"LTIBackend: find_or_create_user() username : {username}")
            user = self.create_user(request, lti, username)

        return user

    def authenticate(self, request, lti):
        try:
            lti.verify(request)
            return self.find_or_create_user(request, lti)
        except LTIException:
            lti.clear_session(request)
            return None

    def get_user(self, user_id):
        logger.info(f"LTIBackend: get_user() user_id {user_id}")
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
