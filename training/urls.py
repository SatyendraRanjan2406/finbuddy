from django.urls import path
from training.views import (
    import_training_data,
    TrainingSectionListView,
    TrainingSectionDetailView,
    UserTrainingProgressView,
    submit_training_answer,
    AdminBulkQuestionCreateView,
)

urlpatterns = [
    path("import/", import_training_data, name="import-training-data"),
    path("sections/", TrainingSectionListView.as_view(), name="training-sections-list"),
    path("sections/<int:id>/", TrainingSectionDetailView.as_view(), name="training-section-detail"),
    path("progress/", UserTrainingProgressView.as_view(), name="user-training-progress"),
    path("submit-answer/", submit_training_answer, name="submit-training-answer"),
    path("admin/bulk-questions/", AdminBulkQuestionCreateView.as_view(), name="training-admin-bulk-questions"),
]

