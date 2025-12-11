from sqlalchemy import Column, Integer, String, Index

from .database import Base


class CoursePrerequisite(Base):
    """Mapping of a course prerequisite rule.

    Composite primary key: (department, level, prerequisite).
    """

    __tablename__ = "course_prerequisite"

    department = Column(String(length=255), primary_key=True, nullable=False)
    level = Column(Integer, primary_key=True, nullable=False)
    prerequisite = Column(String(length=255), primary_key=True, nullable=False)

    __table_args__ = (
        # Index to speed lookups by department+level when resolving prerequisites
        Index("ix_course_prereq_dept_level", "department", "level"),
    )

    def __repr__(self) -> str:  # helpful for debugging and logging
        return f"<CoursePrerequisite {self.department!r} {self.level!r} -> {self.prerequisite!r}>"