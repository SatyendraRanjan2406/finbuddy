from rest_framework import serializers
from training.models import (
    TrainingSection,
    TrainingQuestion,
    TrainingOption,
    UserTrainingProgress,
    TrainingUserAnswer
)


class TrainingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingOption
        fields = ['id', 'option_text', 'is_correct', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrainingQuestionSerializer(serializers.ModelSerializer):
    options = TrainingOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = TrainingQuestion
        fields = [
            'id', 'training', 'question_text', 'question_type', 
            'order', 'language', 'options', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrainingSectionSerializer(serializers.ModelSerializer):
    questions = TrainingQuestionSerializer(many=True, read_only=True)
    questions_count = serializers.SerializerMethodField()
    available_content_types = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()
    has_text = serializers.SerializerMethodField()
    ordered_content = serializers.SerializerMethodField()
    
    class Meta:
        model = TrainingSection
        fields = [
            'id', 'title', 'description', 'content_type', 'language',
            'video_url', 'audio_url', 'text_content', 'is_active',
            'score', 'order', 'questions', 'questions_count',
            'available_content_types', 'has_video', 'has_audio', 'has_text',
            'ordered_content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_questions_count(self, obj):
        return obj.questions.count()
    
    def get_available_content_types(self, obj):
        return obj.get_available_content_types()
    
    def get_has_video(self, obj):
        return obj.has_video()
    
    def get_has_audio(self, obj):
        return obj.has_audio()
    
    def get_has_text(self, obj):
        return obj.has_text()
    
    def get_ordered_content(self, obj):
        """Returns content in play order: video, text, audio"""
        return obj.get_ordered_content()


class TrainingSectionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing sections without questions"""
    questions_count = serializers.SerializerMethodField()
    available_content_types = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()
    has_text = serializers.SerializerMethodField()
    
    class Meta:
        model = TrainingSection
        fields = [
            'id', 'title', 'description', 'content_type', 'language',
            'video_url', 'audio_url', 'text_content', 'is_active',
            'score', 'order', 'questions_count', 'available_content_types',
            'has_video', 'has_audio', 'has_text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_questions_count(self, obj):
        return obj.questions.count()
    
    def get_available_content_types(self, obj):
        return obj.get_available_content_types()
    
    def get_has_video(self, obj):
        return obj.has_video()
    
    def get_has_audio(self, obj):
        return obj.has_audio()
    
    def get_has_text(self, obj):
        return obj.has_text()


class UserTrainingProgressSerializer(serializers.ModelSerializer):
    training_details = TrainingSectionListSerializer(source='training', read_only=True)
    
    class Meta:
        model = UserTrainingProgress
        fields = [
            'id', 'user', 'training', 'training_details',
            'current_video_index', 'videos_completed',
            'questions_started', 'questions_completed',
            'total_questions', 'current_question_index',
            'score', 'is_started', 'is_completed',
            'score_added_to_uhfs', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrainingUserAnswerSerializer(serializers.ModelSerializer):
    question_details = TrainingQuestionSerializer(source='question', read_only=True)
    
    class Meta:
        model = TrainingUserAnswer
        fields = [
            'id', 'user', 'training', 'question', 'question_details',
            'selected_options', 'input_text', 'uploaded_file',
            'is_correct', 'submitted_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'created_at', 'updated_at']


class UpdateTrainingProgressSerializer(serializers.Serializer):
    """Serializer for updating training progress"""
    training_id = serializers.IntegerField(help_text="ID of the training section")
    action = serializers.ChoiceField(
        choices=[
            ("start", "Start training"),
            ("video_completed", "Mark video as completed"),
            ("questions_started", "Mark questions as started"),
            ("question_answered", "Submit answer to a question"),
            ("questions_completed", "Mark all questions as completed"),
            ("complete", "Complete entire training section"),
        ],
        help_text="Action to perform on training progress"
    )
    current_video_index = serializers.IntegerField(required=False, help_text="Current video index (for video progress)")
    current_question_index = serializers.IntegerField(required=False, help_text="Current question index (for question progress)")
    question_id = serializers.IntegerField(required=False, help_text="Question ID (for submitting answers)")
    selected_options = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Selected option IDs (for MCQ questions)"
    )
    input_text = serializers.CharField(required=False, allow_blank=True, help_text="Text input (for input type questions)")
    score = serializers.FloatField(required=False, help_text="Score for the question (optional, will be calculated for MCQ)")


class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting answers to training questions"""
    training_id = serializers.IntegerField(help_text="ID of the training section")
    question_id = serializers.IntegerField(help_text="ID of the question")
    selected_options = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Selected option IDs (for MCQ questions - single or multiple)"
    )
    input_text = serializers.CharField(required=False, allow_blank=True, help_text="Text input (for input type questions)")
    uploaded_file = serializers.FileField(required=False, help_text="File upload (for file type questions)")

