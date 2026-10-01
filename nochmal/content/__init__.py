"""Published lesson content and its validation contract."""

from .a1_a2_lessons import A1_A2_LESSONS
from .a1_course_lessons import A1_COURSE_LESSONS
from .core_lessons import LESSONS as PREPARED_LESSONS


# The sequenced foundation course comes first.  The original audio lessons
# remain available afterwards as additional A2-B2 practice.
LESSONS = [*A1_COURSE_LESSONS, *A1_A2_LESSONS, *PREPARED_LESSONS]

__all__ = ["A1_COURSE_LESSONS", "A1_A2_LESSONS", "PREPARED_LESSONS", "LESSONS"]
