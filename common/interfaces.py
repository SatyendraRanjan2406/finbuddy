from typing import Protocol, Dict


class QuestionnaireInterface(Protocol):
    """Each questionnaire model should implement these"""

    def save_answers(self, user, data: Dict): ...
    def calculate_section_score(self, user) -> float: ...
