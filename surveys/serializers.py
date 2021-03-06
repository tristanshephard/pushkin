
""" Serialization definitions for the models in this app """

from rest_framework import serializers

from .models import Survey, Response, Question, Answer, Tag


class TagSerializer(serializers.ModelSerializer):
    """ Serialization definition for the `Tag` object.

    Tags are serialized as:
        {
            'tag_text' : <tag_text>
        }
    """
    class Meta:
        model = Tag
        fields = ('tag_text',)

class AnswerSerializer(serializers.ModelSerializer):
    """ Serialization definition for the `Answer` object.

    Answers are serialized as:
        {
            'answer_text' : <answer_text>,
            'tags' : [<tag_text>, <tag_text>, ...]
        }
    """
    tag_strings = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Answer
        read_only_fields = ('answer_text',)
        fields = ('answer_text', 'tag_strings',)

class ResponseSerializer(serializers.ModelSerializer):
    """ Serialization definition for the the `Response` objects

    Responses are serialized as:
        {
            'answer_strings' : [<answer_text>, <answer_text>, ...]
        }
    """

    answers = serializers.SlugRelatedField(slug_field='answer_text',
                                           many=True, read_only=True)

    class Meta:
        model = Response
        fields = ('answers',)

class QuestionSerializer(serializers.ModelSerializer):
    """ Serialization definition for the the `Question` objects

    Questions are serialized as:
        {
            'question_text' : <question_text>
        }
    """
    class Meta:
        model = Question
        fields = ('question_text',)

class SurveySerializer(serializers.ModelSerializer):
    """ Serialization definition for the the `Survey` object

    Responses are serialized as:
        {
            'questions' : [<question_text>, <question_text>, ...],
            'tag_options' : [<tag_text>, <tag_text>, ...],
            'id' : <id>,
            'name' : <name>,
            'response_count' : <number of associated `Response` objects>,
            'published' : <True|False>
        }

    """
    # Use SlugRelatedFields for questions and tags rather than the entire
    # respective serializers
    questions = serializers.SlugRelatedField(many=True,
                                             slug_field='question_text',
                                             read_only=True)
    tag_options = serializers.SlugRelatedField(many=True,
                                               slug_field='tag_text',
                                               read_only=True)

    def validate(self, data):
        """ Prevent the `published` variable being set to False """
        if 'published' in data and not data.get('published'):
            del data['published']
        return data

    class Meta:
        model = Survey
        fields = ('id', 'name', 'questions', 'tag_options', 'response_count',
                  'published')

