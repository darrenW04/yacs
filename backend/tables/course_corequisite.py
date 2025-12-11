from sqlalchemy import Column, Integer, String, Index

from .database import Base


class CourseCorequisite(Base):
    """Model for course corequisites.

    Composite primary key: (department, level, corequisite).
    """

    __tablename__ = 'course_corequisite'

    department = Column(String(length=255), primary_key=True, nullable=False)
    level = Column(Integer, primary_key=True, nullable=False)
    corequisite = Column(String(length=255), primary_key=True, nullable=False)

    __table_args__ = (
        Index('ix_course_coreq_dept_level', 'department', 'level'),
    )

    def __repr__(self) -> str:
        return f"<CourseCorequisite {self.department!r} {self.level!r} -> {self.corequisite!r}>"