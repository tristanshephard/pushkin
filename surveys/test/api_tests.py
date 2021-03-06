
""" Tests the API itself; http codes and response bodies """

from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework import status

from .test_utils import TestBase
from ..models import Survey
from ..serializers import SurveySerializer

class APITests(TestBase):
    """ Tests concerning serialized responses and HTTP codes """

    def test_survey_creation(self):
        """ A survey can be added by posting """
        self.check_response_code('/surveys/', self.client.post,
                                 [status.HTTP_201_CREATED], {'name' : 'foo'})
        Survey.objects.get(owner=self.users[0], name='foo')

    def test_question_creation(self):
        """ Questions can be added by posting """
        user = self.users[0]
        survey = user.surveys.create(name='foo')
        self.check_response_code('/surveys/%s/questions/' % survey.id,
                                 self.client.post, [status.HTTP_201_CREATED],
                                 {'question_text' : 'bar?'})
        survey.questions.get(question_text='bar?')

    def test_tag_creation(self):
        """ Tags can be added by posting """
        survey = self.users[0].surveys.first()
        self.check_response_code('/surveys/%s/tags/' % survey.id,
                                 self.client.post, [status.HTTP_201_CREATED],
                                 {'tag_text' : 'tagtagtag'})
        survey.tag_options.get(tag_text='tagtagtag')

    def test_duplicate_tag_creation(self):
        """ Attempting to create duplicate tags has no effect """
        survey = self.users[0].surveys.first()
        # Add a tag, then assert that adding the same tag again does not
        # increase the tag count
        self.check_response_code('/surveys/%s/tags/' % survey.id,
                                 self.client.post, [status.HTTP_201_CREATED],
                                 {'tag_text' : 'tagtagtag'})
        tag_count = survey.tag_options.count()
        self.check_response_code('/surveys/%s/tags/' % survey.id,
                                 self.client.post, [status.HTTP_201_CREATED],
                                 {'tag_text' : 'tagtagtag'})
        self.assertEqual(tag_count, survey.tag_options.count())

    def test_survey_view_ownership(self):
        """ When a user lists surveys, they see only their own surveys """
        # Construct a set of all the survey names the user owns, and assert
        # it is identical to the serialized names retrieved from the API.
        user = self.users[0]
        db_names = {survey.name for survey in user.surveys.all()}

        # Get the serialized data and validate
        response = self.client.get('/surveys/')
        data = JSONParser().parse(BytesIO(response.content))
        serializer = SurveySerializer(data=data, many=True)
        self.assertTrue(serializer.is_valid())

        serialized_names = {survey['name']
                            for survey in serializer.validated_data}
        self.assertEqual(db_names, serialized_names)

    def test_publication_by_api(self):
        """ A survey is published by the appropriate data message, and
        requests to unpublish are ignored.
         """
        survey = self.users[0].surveys.create()
        self.assertEqual(survey.published, False)
        self.check_response_code('/surveys/%s/' % survey.id,
                                 self.client.patch, [status.HTTP_200_OK],
                                 {"published":True})
        survey.refresh_from_db()
        self.assertEqual(survey.published, True)

    def test_404_nonexistent_objects(self):
        """ Accessing an object that does not exist under a survey that
        does exist returns a 404, e.g. trying to get the 5th question under
        a survey that only has 4 questions
        """
        survey = self.users[0].surveys.first()
        self.check_response_code('/surveys/%s/questions/999/' % survey.id,
                                 self.client.get, [status.HTTP_404_NOT_FOUND])
