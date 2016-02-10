
from surveys.models import *

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from rest_framework import status

URLs = ['/surveys/','/surveys/1/','/surveys/1/questions/', '/surveys/1/questions/1', '/surveys/1/tags/', '/surveys/1/tags/1', '/surveys/1/responses/', '/surveys/1/responses/1', '/surveys/1/responses/1/answers/', '/surveys/1/responses/1/answers/1']

class Setup:

    @staticmethod
    def oneUser(test_func):
        def setup_func(suite):
            # Setup
            user = User.objects.create(username='user1')

            # Execute the test
            test_func(suite, user)

            # Cleanup
            user.delete()
        return setup_func


class AuthTests(APITestCase):

    def test_unauthenticated_get(self):
        """
        HTTP requests are met with 403s if not authenticated on all URLs
        """
        requests = [self.client.get, self.client.post, self.client.put, self.client.patch, self.client.delete]
        for req in requests:
            for url in URLs:
                self.assertEqual(req(url).status_code, status.HTTP_403_FORBIDDEN,
                                 "Unauthenticated request %s/%s did not receive 403" % (req , url))

    @Setup.oneUser
    def test_create_user(self, user):
        print("Got user %s" % user)
