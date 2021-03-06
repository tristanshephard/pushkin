
""" Tests for the database layer """

from .test_utils import TestBase
from ..models import DBError

class DBLogicTests(TestBase):
    """
    Concernins pure database logic. These tests are performed directly at the
    DB layer and do not involve HTTP requests.
    """

    def test_survey_creation(self):
        """ Test general survey creation """
        user = self.users[0]
        survey = user.surveys.create()
        self.assertEqual(survey.name, 'My Survey')
        self.assertEqual(survey.owner, user)
        self.assertEqual(survey.questions.count(), 0)
        self.assertEqual(survey.responses.count(), 0)
        self.assertEqual(survey.tag_options.count(), 0)
        self.assertEqual(survey.published, False)

    def test_publishing(self):
        """ The survey's `publish()` method has the desired effect """
        survey = self.users[0].surveys.create()
        survey.publish()
        self.assertTrue(survey.published)

    def test_unpublished_response(self):
        """ A survey cannot have responses added before being published """
        survey = self.users[0].surveys.create()
        self.assertRaises(DBError, survey.responses.create)
        survey.publish()
        survey.responses.create()
