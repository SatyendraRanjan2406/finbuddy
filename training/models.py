from django.db import models
from common.models import TimeStampedModel, UserOwnedModel
from accounts.models import User

class TrainingSection(TimeStampedModel):
    """
    A training module: can have video, audio, and/or text content
    and supports multiple languages.
    A section can have multiple content types simultaneously.
    """
    TYPE_CHOICES = (
        ("video", "Video"),
        ("audio", "Audio"),
        ("text", "Text"),
        ("mixed", "Mixed"),  # Multiple content types
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        blank=True, 
        null=True,
        help_text="Primary content type (optional). Use 'mixed' if section has multiple types."
    )

    # Multilingual fields
    language = models.CharField(max_length=10, default="en")  # en, hi, bn, te, ta, etc.

    # Content paths or text - a section can have all three simultaneously
    video_url = models.URLField(blank=True, null=True, help_text="Video content URL")
    audio_url = models.URLField(blank=True, null=True, help_text="Audio content URL")
    text_content = models.TextField(blank=True, null=True, help_text="Text content")

    is_active = models.BooleanField(default=True)
    
    # Score and ordering
    score = models.FloatField(default=10.0, help_text="Score points awarded on completion (default: 10)")
    order = models.PositiveIntegerField(default=0, help_text="Order of content: video, text, audio")

    def get_available_content_types(self):
        """Returns list of content types available in this section"""
        types = []
        if self.video_url:
            types.append("video")
        if self.audio_url:
            types.append("audio")
        if self.text_content:
            types.append("text")
        return types
    
    def has_video(self):
        """Check if section has video content"""
        return bool(self.video_url)
    
    def has_audio(self):
        """Check if section has audio content"""
        return bool(self.audio_url)
    
    def has_text(self):
        """Check if section has text content"""
        return bool(self.text_content)
    
    def get_ordered_content(self):
        """
        Returns content in order: video, text, audio
        Each content item is a dict with type, url/content, and order
        """
        content_items = []
        
        # Add video if available
        if self.video_url:
            content_items.append({
                "type": "video",
                "url": self.video_url,
                "order": 1
            })
        
        # Add text if available
        if self.text_content:
            content_items.append({
                "type": "text",
                "content": self.text_content,
                "order": 2
            })
        
        # Add audio if available
        if self.audio_url:
            content_items.append({
                "type": "audio",
                "url": self.audio_url,
                "order": 3
            })
        
        return content_items

    def __str__(self):
        return f"{self.title} ({self.language})"


class UserTrainingProgress(TimeStampedModel, UserOwnedModel):
    """
    Tracks training suggestions and completion.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    training = models.ForeignKey(TrainingSection, on_delete=models.CASCADE)
    current_video_index = models.PositiveIntegerField(default=1)
    videos_completed = models.BooleanField(default=False)
    questions_started = models.BooleanField(default=False)
    questions_completed = models.BooleanField(default=False)
    total_questions = models.PositiveIntegerField(default=0)
    current_question_index = models.PositiveIntegerField(default=1)
    score = models.FloatField(default=0.0)
    is_started = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    score_added_to_uhfs = models.BooleanField(default=False, help_text="Whether score was already added to UHFS")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'training')
        ordering = ['-updated_at']

class TrainingQuestion(TimeStampedModel):
    """
    MCQ questions linked to a training section.
    """
    QUESTION_TYPES = (
        ("mcq_single", "MCQ - Single Choice"),
        ("mcq_multiple", "MCQ - Multiple Choice"),
        ('input', 'Input Text'),
        ('file', 'File Upload'),
    )

    training = models.ForeignKey(TrainingSection, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField(default=0, help_text="Order of question within training")

    language = models.CharField(max_length=10, default="en")  # multilingual support

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.question_text


class TrainingOption(TimeStampedModel):
    """
    Options for each MCQ question.
    """
    question = models.ForeignKey(
        TrainingQuestion, related_name="options", on_delete=models.CASCADE
    )
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text


class TrainingUserAnswer(TimeStampedModel, UserOwnedModel):
    """
    Stores user answers to training quizzes.
    Works for both single & multiple choice.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    training = models.ForeignKey(TrainingSection, on_delete=models.CASCADE)
    question = models.ForeignKey(TrainingQuestion, on_delete=models.CASCADE)

    # For single or multiple choice
    selected_options = models.JSONField(
        null=True, blank=True,
        help_text="Single → ['A'], Multiple → ['A','C']"
    )

    # For input responses
    input_text = models.TextField(null=True, blank=True)

    # For file upload responses
    uploaded_file = models.FileField(
        upload_to="training_uploads/",
        null=True, 
        blank=True
    )

    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "question")
