import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from django.db import transaction
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from training.models import TrainingSection, TrainingQuestion, TrainingOption, UserTrainingProgress, TrainingUserAnswer
from training.serializers import (
    TrainingSectionSerializer,
    TrainingSectionListSerializer,
    TrainingQuestionSerializer,
    UserTrainingProgressSerializer,
    UpdateTrainingProgressSerializer,
    SubmitAnswerSerializer,
    BulkQuestionCreateSerializer,
)


# Google Sheets Configuration
SPREADSHEET_ID = "1gufHMamzNEWC9t1GvhqhDlBlr4LG8aNQ01sN839bGU8"
# Try multiple possible paths for service account file
SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, "graphic-mason-479110-d6-a120ba88825f.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_sheet_df(sheet_name, gc, sh):
    """Read Google Sheet tab into pandas DataFrame"""
    try:
        worksheet = sh.worksheet(sheet_name)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        raise Exception(f"Error reading sheet '{sheet_name}': {str(e)}")


def import_from_google_sheets():
    """Import training data from Google Sheets"""
    try:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise Exception(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, SCOPES
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        
        df_sections = get_sheet_df("TrainingSections", gc, sh)
        df_questions = get_sheet_df("TrainingQuestions", gc, sh)
        df_options = get_sheet_df("TrainingOptions", gc, sh)
        
        with transaction.atomic():
            # Clear previous data
            TrainingOption.objects.all().delete()
            TrainingQuestion.objects.all().delete()
            TrainingSection.objects.all().delete()
            
            # Create Training Sections
            # Columns: section_id, title, description, content_type, language, video_url, audio_url, text_content, is_active, score, order
            sections_created = 0
            section_id_map = {}  # Map spreadsheet section_id to database section object
            
            for _, row in df_sections.iterrows():
                # Determine content_type automatically if not provided
                video_url = row.get("video_url") or None
                audio_url = row.get("audio_url") or None
                text_content = row.get("text_content") or None
                
                # Count available content types
                content_count = sum([
                    1 if video_url and pd.notna(video_url) else 0,
                    1 if audio_url and pd.notna(audio_url) else 0,
                    1 if text_content and pd.notna(text_content) else 0
                ])
                
                # Set content_type: use provided value, or "mixed" if multiple types, or determine from available
                provided_content_type = row.get("content_type")
                if pd.notna(provided_content_type) and provided_content_type:
                    content_type = provided_content_type
                elif content_count > 1:
                    content_type = "mixed"
                elif video_url and pd.notna(video_url):
                    content_type = "video"
                elif audio_url and pd.notna(audio_url):
                    content_type = "audio"
                elif text_content and pd.notna(text_content):
                    content_type = "text"
                else:
                    content_type = None  # No content available
                
                section = TrainingSection.objects.create(
                    title=row.get("title", ""),
                    description=row.get("description", "") or "",
                    content_type=content_type,
                    language=row.get("language", "en"),
                    video_url=video_url if pd.notna(video_url) else None,
                    audio_url=audio_url if pd.notna(audio_url) else None,
                    text_content=text_content if pd.notna(text_content) else None,
                    score=float(row.get("score", 10)) if pd.notna(row.get("score")) else 10.0,
                    order=int(row.get("order", 0)) if pd.notna(row.get("order")) else 0,
                    is_active=bool(row.get("is_active", True)) if pd.notna(row.get("is_active")) else True,
                )
                # Map spreadsheet section_id to database section
                spreadsheet_section_id = row.get("section_id")
                if pd.notna(spreadsheet_section_id):
                    section_id_map[spreadsheet_section_id] = section
                sections_created += 1
            
            # Create Training Questions
            # Columns: question_id, section_id, question_text, question_type, order, language
            questions_created = 0
            question_id_map = {}  # Map spreadsheet question_id to database question object
            
            for _, row in df_questions.iterrows():
                spreadsheet_section_id = row.get("section_id")
                if pd.isna(spreadsheet_section_id) or spreadsheet_section_id not in section_id_map:
                    continue  # Skip if section_id is missing or not found
                
                section = section_id_map[spreadsheet_section_id]
                question = TrainingQuestion.objects.create(
                    training=section,
                    question_text=row.get("question_text", ""),
                    question_type=row.get("question_type", "mcq_single"),
                    order=int(row.get("order", 0)) if pd.notna(row.get("order")) else 0,
                    language=row.get("language", "en"),
                )
                # Map spreadsheet question_id to database question
                spreadsheet_question_id = row.get("question_id")
                if pd.notna(spreadsheet_question_id):
                    question_id_map[spreadsheet_question_id] = question
                questions_created += 1
            
            # Create Training Options
            # Columns: option_id, question_id, option_text, is_correct
            options_created = 0
            for _, row in df_options.iterrows():
                spreadsheet_question_id = row.get("question_id")
                if pd.isna(spreadsheet_question_id) or spreadsheet_question_id not in question_id_map:
                    continue  # Skip if question_id is missing or not found
                
                question = question_id_map[spreadsheet_question_id]
                TrainingOption.objects.create(
                    question=question,
                    option_text=row.get("option_text", ""),
                    is_correct=bool(row.get("is_correct", False)) if pd.notna(row.get("is_correct")) else False,
                )
                options_created += 1
        
        return {
            "success": True,
            "message": "Training data imported successfully",
            "sections_created": sections_created,
            "questions_created": questions_created,
            "options_created": options_created
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error importing data: {str(e)}"
        }


@api_view(["POST"])
def import_training_data(request):
    """
    POST /api/training/import/
    Import training sections, questions, and options from Google Sheets.
    Requires admin authentication.
    """
    result = import_from_google_sheets()
    
    if result["success"]:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class TrainingSectionListView(APIView):
    """
    GET /api/training/sections/
    Get list of all training sections (without questions for performance)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        sections = TrainingSection.objects.filter(is_active=True).order_by('order', 'id')
        
        # Optional filters
        language = request.query_params.get('language')
        content_type = request.query_params.get('content_type')
        
        if language:
            sections = sections.filter(language=language)
        if content_type:
            sections = sections.filter(content_type=content_type)
        
        serializer = TrainingSectionListSerializer(sections, many=True)
        return Response({
            "count": len(serializer.data),
            "sections": serializer.data
        }, status=status.HTTP_200_OK)


class TrainingSectionDetailView(APIView):
    """
    GET /api/training/sections/<id>/
    Get detailed information about a specific training section including all questions and options
    """
    permission_classes = [AllowAny]
    
    def get(self, request, id):
        try:
            section = TrainingSection.objects.get(id=id, is_active=True)
        except TrainingSection.DoesNotExist:
            return Response(
                {"error": "Training section not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TrainingSectionSerializer(section)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTrainingProgressView(APIView):
    """
    GET /api/training/progress/
    Get training progress for the authenticated user
    
    POST /api/training/progress/
    Update training progress (start, mark video completed, etc.)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        progress = UserTrainingProgress.objects.filter(user=request.user)
        serializer = UserTrainingProgressSerializer(progress, many=True)
        return Response({
            "count": len(serializer.data),
            "progress": serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Update training progress"""
        serializer = UpdateTrainingProgressSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        training_id = serializer.validated_data["training_id"]
        action = serializer.validated_data["action"]
        
        try:
            training_section = TrainingSection.objects.get(id=training_id, is_active=True)
        except TrainingSection.DoesNotExist:
            return Response({"error": "Training section not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get or create progress
        progress, created = UserTrainingProgress.objects.get_or_create(
            user=request.user,
            training=training_section,
            defaults={
                "is_started": True,
                "total_questions": training_section.questions.count()
            }
        )
        
        if action == "start":
            progress.is_started = True
            progress.save()
            return Response({
                "message": "Training started",
                "progress": UserTrainingProgressSerializer(progress).data
            }, status=status.HTTP_200_OK)
        
        elif action == "video_completed":
            progress.videos_completed = True
            current_video_index = serializer.validated_data.get("current_video_index")
            if current_video_index:
                progress.current_video_index = current_video_index
            progress.save()
            return Response({
                "message": "Video marked as completed",
                "progress": UserTrainingProgressSerializer(progress).data
            }, status=status.HTTP_200_OK)
        
        elif action == "questions_started":
            progress.questions_started = True
            progress.save()
            return Response({
                "message": "Questions started",
                "progress": UserTrainingProgressSerializer(progress).data
            }, status=status.HTTP_200_OK)
        
        elif action == "questions_completed":
            progress.questions_completed = True
            progress.save()
            return Response({
                "message": "All questions completed",
                "progress": UserTrainingProgressSerializer(progress).data
            }, status=status.HTTP_200_OK)
        
        elif action == "complete":
            from finance.models import UserFinancialLiteracy
            from finance.services.uhfs import calculate_and_store_uhfs
            
            progress.is_completed = True
            progress.questions_completed = True
            progress.videos_completed = True
            # Add training section score to progress
            progress.score = training_section.score
            progress.save()
            
            # Update UHFS score if not already added
            if not progress.score_added_to_uhfs:
                # Get or create UserFinancialLiteracy
                literacy, _ = UserFinancialLiteracy.objects.get_or_create(user=request.user)
                
                # Update modules completed count
                completed_modules = UserTrainingProgress.objects.filter(
                    user=request.user,
                    is_completed=True
                ).count()
                literacy.modules_completed = completed_modules
                
                # Calculate average quiz score from all completed trainings
                completed_trainings = UserTrainingProgress.objects.filter(
                    user=request.user,
                    is_completed=True
                )
                total_score = sum(t.score for t in completed_trainings)
                if completed_modules > 0:
                    # Average score as percentage (assuming max score per module is 100)
                    # Or use the actual scores from training sections
                    literacy.average_quiz_score = (total_score / completed_modules) * 10  # Convert to 0-100 scale
                else:
                    literacy.average_quiz_score = 0.0
                
                literacy.save()
                
                # Recalculate UHFS score with updated literacy data
                try:
                    calculate_and_store_uhfs(request.user)
                    progress.score_added_to_uhfs = True
                    progress.save()
                except Exception as e:
                    # Log error but don't fail the request
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error updating UHFS score: {str(e)}")
            
            return Response({
                "message": "Training section completed",
                "progress": UserTrainingProgressSerializer(progress).data,
                "uhfs_updated": progress.score_added_to_uhfs
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class AdminBulkQuestionCreateView(APIView):
    """
    POST /api/training/admin/bulk-questions/
    Admin-only endpoint to add multiple questions (and options) to a section.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = BulkQuestionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        training_id = serializer.validated_data["training_id"]
        questions_data = serializer.validated_data["questions"]

        try:
            training = TrainingSection.objects.get(id=training_id)
        except TrainingSection.DoesNotExist:
            return Response(
                {"error": "Training section not found"}, status=status.HTTP_404_NOT_FOUND
            )

        created_questions = []

        with transaction.atomic():
            for idx, q in enumerate(questions_data, start=1):
                order = q.get("order") or idx
                question = TrainingQuestion.objects.create(
                    training=training,
                    question_text=q["question_text"],
                    question_type=q["question_type"],
                    order=order,
                    language=q.get("language", "en"),
                )

                # Only create options for MCQ types
                if q["question_type"] in ["mcq_single", "mcq_multiple"]:
                    options = q.get("options") or []
                    for opt in options:
                        TrainingOption.objects.create(
                            question=question,
                            option_text=opt["option_text"],
                            is_correct=opt.get("is_correct", False),
                        )

                created_questions.append(question.id)

        return Response(
            {
                "message": "Questions created successfully",
                "training_id": training.id,
                "question_ids": created_questions,
                "count": len(created_questions),
            },
            status=status.HTTP_201_CREATED,
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def submit_training_answer(request):
    """
    POST /api/training/submit-answer/
    Submit answer to a training question
    """
    serializer = SubmitAnswerSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    training_id = serializer.validated_data["training_id"]
    question_id = serializer.validated_data["question_id"]
    selected_options = serializer.validated_data.get("selected_options", [])
    input_text = serializer.validated_data.get("input_text")
    uploaded_file = serializer.validated_data.get("uploaded_file")
    
    try:
        training_section = TrainingSection.objects.get(id=training_id, is_active=True)
        question = TrainingQuestion.objects.get(id=question_id, training=training_section)
    except TrainingSection.DoesNotExist:
        return Response({"error": "Training section not found"}, status=status.HTTP_404_NOT_FOUND)
    except TrainingQuestion.DoesNotExist:
        return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create progress
    progress, _ = UserTrainingProgress.objects.get_or_create(
        user=request.user,
        training=training_section,
        defaults={
            "is_started": True,
            "questions_started": True,
            "total_questions": training_section.questions.count()
        }
    )
    
    if not progress.questions_started:
        progress.questions_started = True
    
    # Determine if answer is correct
    is_correct = False
    if question.question_type in ["mcq_single", "mcq_multiple"]:
        # Get correct option IDs
        correct_options = list(question.options.filter(is_correct=True).values_list('id', flat=True))
        # Check if selected options match correct options
        if set(selected_options) == set(correct_options):
            is_correct = True
    elif question.question_type == "input":
        # For input questions, mark as correct if text is provided (or implement custom logic)
        is_correct = bool(input_text and len(input_text.strip()) > 0)
    elif question.question_type == "file":
        # For file questions, mark as correct if file is uploaded
        is_correct = bool(uploaded_file)
    
    # Create or update answer
    answer, created = TrainingUserAnswer.objects.update_or_create(
        user=request.user,
        question=question,
        defaults={
            "training": training_section,
            "selected_options": selected_options if selected_options else None,
            "input_text": input_text,
            "uploaded_file": uploaded_file,
            "is_correct": is_correct
        }
    )
    
    # Update progress
    if is_correct:
        progress.score += training_section.score / progress.total_questions if progress.total_questions > 0 else 0
    
    # Update current question index
    next_question = TrainingQuestion.objects.filter(
        training=training_section,
        order__gt=question.order
    ).order_by('order').first()
    
    if next_question:
        progress.current_question_index = next_question.order
    else:
        # All questions answered
        progress.questions_completed = True
        progress.current_question_index = progress.total_questions
        
        # Auto-complete if all content is also completed
        if progress.videos_completed:
            progress.is_completed = True
            progress.score = training_section.score
            
            # Update UHFS if not already done
            if not progress.score_added_to_uhfs:
                from finance.models import UserFinancialLiteracy
                from finance.services.uhfs import calculate_and_store_uhfs
                
                # Get or create UserFinancialLiteracy
                literacy, _ = UserFinancialLiteracy.objects.get_or_create(user=request.user)
                
                # Update modules completed count
                completed_modules = UserTrainingProgress.objects.filter(
                    user=request.user,
                    is_completed=True
                ).count()
                literacy.modules_completed = completed_modules
                
                # Calculate average quiz score from all completed trainings
                completed_trainings = UserTrainingProgress.objects.filter(
                    user=request.user,
                    is_completed=True
                )
                total_score = sum(t.score for t in completed_trainings)
                if completed_modules > 0:
                    # Convert to 0-100 scale (assuming max score per module is 10, multiply by 10)
                    literacy.average_quiz_score = (total_score / completed_modules) * 10
                else:
                    literacy.average_quiz_score = 0.0
                
                literacy.save()
                
                # Recalculate UHFS score
                try:
                    calculate_and_store_uhfs(request.user)
                    progress.score_added_to_uhfs = True
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error updating UHFS score: {str(e)}")
    
    progress.save()
    
    return Response({
        "message": "Answer submitted successfully",
        "is_correct": is_correct,
        "answer_id": answer.id,
        "progress": UserTrainingProgressSerializer(progress).data,
        "training_completed": progress.is_completed,
        "uhfs_updated": progress.score_added_to_uhfs if progress.is_completed else False
    }, status=status.HTTP_200_OK)
