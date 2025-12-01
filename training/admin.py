from django.contrib import admin
import nested_admin

from .models import (
    TrainingSection,
    TrainingQuestion,
    TrainingOption,
    UserTrainingProgress,
    TrainingUserAnswer,
)


class TrainingOptionInline(nested_admin.NestedTabularInline):
    model = TrainingOption
    extra = 2


class TrainingQuestionInline(nested_admin.NestedStackedInline):
    model = TrainingQuestion
    extra = 1
    show_change_link = True
    inlines = [TrainingOptionInline]


@admin.register(TrainingSection)
class TrainingSectionAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        "id",
        "title",
        "language",
        "content_type",
        "has_video",
        "has_audio",
        "has_text",
        "score",
        "order",
        "is_active",
    )
    list_filter = ("language", "content_type", "is_active")
    search_fields = ("title", "description")
    inlines = [TrainingQuestionInline]

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "title",
                    "description",
                    "language",
                    "is_active",
                )
            },
        ),
        (
            "Content (Video / Audio / Text)",
            {
                "fields": (
                    "content_type",
                    "video_url",
                    "audio_url",
                    "text_content",
                )
            },
        ),
        (
            "Scoring & Order",
            {
                "fields": (
                    "score",
                    "order",
                )
            },
        ),
    )

    def has_video(self, obj):
        return obj.has_video()

    has_video.boolean = True
    has_video.short_description = "Video"

    def has_audio(self, obj):
        return obj.has_audio()

    has_audio.boolean = True
    has_audio.short_description = "Audio"

    def has_text(self, obj):
        return obj.has_text()

    has_text.boolean = True
    has_text.short_description = "Text"


@admin.register(TrainingQuestion)
class TrainingQuestionAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        "id",
        "training",
        "question_text",
        "question_type",
        "order",
        "language",
    )
    list_filter = ("question_type", "language", "training")
    search_fields = ("question_text", "training__title")
    inlines = [TrainingOptionInline]


@admin.register(TrainingOption)
class TrainingOptionAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "option_text", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("option_text", "question__question_text")


@admin.register(UserTrainingProgress)
class UserTrainingProgressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "training",
        "is_started",
        "videos_completed",
        "questions_completed",
        "score",
        "is_completed",
        "score_added_to_uhfs",
        "updated_at",
    )
    list_filter = (
        "is_started",
        "videos_completed",
        "questions_completed",
        "is_completed",
        "score_added_to_uhfs",
    )
    search_fields = ("user__username", "training__title")


@admin.register(TrainingUserAnswer)
class TrainingUserAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "training",
        "question",
        "is_correct",
        "submitted_at",
    )
    list_filter = ("is_correct", "training")
    search_fields = ("user__username", "question__question_text", "training__title")

