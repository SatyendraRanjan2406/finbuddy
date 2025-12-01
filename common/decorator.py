from functools import wraps
from rest_framework.response import Response


def enforce_onboarding_complete(view_func):
    """Block an API if user has not finished onboarding"""

    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        user = request.user
        progress = getattr(user, "onboardingprogress", None)

        if not progress or not progress.is_completed:
            return Response({
                "detail": "Please complete onboarding questionnaire first."
            }, status=403)

        return view_func(self, request, *args, **kwargs)

    return wrapper
