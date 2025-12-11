from sqlalchemy import Column, Integer, String, Time, Index

from .database import Base


class CourseSession(Base):
    """ORM model for a course session/time slot.

    Notes:
    - Use generic SQLAlchemy types (String/Integer/Time) for portability.
    - Composite primary key is declared by marking the columns with primary_key=True.
    - Add indexes for commonly queried columns (crn, semester) to improve lookup speed.
    """

    __tablename__ = "course_session"

    crn = Column(String(length=255), primary_key=True)
    section = Column(String(length=255), primary_key=True)
    semester = Column(String(length=255), primary_key=True, index=True)
    time_start = Column(Time)
    time_end = Column(Time)
    day_of_week = Column(Integer, primary_key=True)
    location = Column(String(length=255))
    session_type = Column(String(length=255))
    instructor = Column(String(length=255))

    # additional indexes (optional) — keep lightweight and add only where queries benefit
    __table_args__ = (
        Index("ix_course_session_crn", "crn"),
    )

    def __repr__(self) -> str:
        return (
            f"<CourseSession crn={self.crn!r} section={self.section!r} "
            f"semester={self.semester!r} day_of_week={self.day_of_week!r}>"
        )
