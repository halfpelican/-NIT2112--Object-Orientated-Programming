from dataclasses import dataclass
from datetime import date
from typing import List
from pathlib import Path
from enum import Enum
import json

"""
Student Transcript Generation System
Demonstrates top-down design with clear separation of concerns.
"""



class GradeType(Enum):
    """Enumeration of possible grade values."""
    HD = "High Distinction (85–100)"
    D = "Distinction (75–84)"
    C = "Credit (65–74)"
    P = "Pass (50–64)"
    F = "Fail (0–49)"


@dataclass
class Subject:
    """Represents a subject the student has completed."""
    
    subject_code: str
    subject_name: str
    credit_points: int
    grade: GradeType
    year_completed: int
    
    def grade_point_value(self) -> float:
        """Return numeric equivalent of grade for GPA calculation."""
        grade_map = {
            GradeType.HD: 4.0,
            GradeType.D: 3.0,
            GradeType.C: 2.0,
            GradeType.P: 1.0,
            GradeType.F: 0.0,
        }
        return grade_map[self.grade]

        @dataclass
        class AcademicRecord:
            """
            Represents a student's complete academic record.
            Acts as a data container that bridges Student, Subject, and reporting logic.
            Responsibilities: aggregate student data, validate record integrity.
            """
            
            student: Student
            subjects: List[Subject]
            record_created_date: date
            
            def __post_init__(self) -> None:
                """Validate record after initialisation."""
                if not self.subjects:
                    raise ValueError("Academic record must contain at least one subject.")
            
            def get_subjects_by_grade(self, grade: GradeType) -> List[Subject]:
                """Filter subjects by grade achieved."""
                return [s for s in self.subjects if s.grade == grade]
            
            def get_subjects_by_year(self, year: int) -> List[Subject]:
                """Filter subjects completed in a specific year."""
                return [s for s in self.subjects if s.year_completed == year]
            
            def has_failed_subjects(self) -> bool:
                """Check if student has any fail grades."""
                return any(s.grade == GradeType.F for s in self.subjects)
                def grade_point_value(self) -> float:
                    """Return numeric equivalent of grade for GPA calculation."""
                    grade_map = {
                        GradeType.HD: 4.0,
                        GradeType.D: 3.0,
                        GradeType.C: 2.0,
                        GradeType.P: 1.0,
                        GradeType.F: 0.0,
                    }
                    return grade_map[self.grade]


@dataclass
class Program:
    """Represents a degree program (e.g., Bachelor of Data Science)."""
    
    program_code: str
    program_name: str
    total_credit_points: int
    commencement_date: date
    expected_completion_date: date


class Student:
    """
    Represents a student and manages their academic record.
    Responsibilities: enrol in subjects, record grades, provide record summary.
    """
    
    def __init__(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        program: Program,
    ):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.program = program
        self.subjects_completed: list[Subject] = []
    
    def add_subject_result(self, subject: Subject) -> None:
        """Record a completed subject and grade."""
        self.subjects_completed.append(subject)
    
    def get_gpa(self) -> float:
        """
        Calculate weighted GPA (Grade Point Average).
        GPA = sum(grade_point × credit_points) / total_credit_points
        """
        if not self.subjects_completed:
            return 0.0
        
        total_points = sum(
            s.grade_point_value() * s.credit_points
            for s in self.subjects_completed
        )
        total_credits = sum(s.credit_points for s in self.subjects_completed)
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    
    def get_total_credit_points(self) -> int:
        """Return total credit points achieved."""
        return sum(s.credit_points for s in self.subjects_completed)


class TranscriptGenerator:
    """
    Generates a formatted academic transcript from student data.
    Responsibility: convert Student object into readable, formatted output.
    """
    
    def __init__(self):
        pass
    
    def generate_transcript(self, student: Student) -> str:
        """
        Create a complete transcript as a formatted string.
        Includes header, subject results table, and summary statistics.
        """
        lines = []
        lines.append(self._generate_header(student))
        lines.append(self._generate_subject_table(student))
        lines.append(self._generate_summary(student))
        return "\n".join(lines)
    
    def _generate_header(self, student: Student) -> str:
        """Format the student and program information section."""
        header = (
            f"{'=' * 70}\n"
            f"ACADEMIC TRANSCRIPT\n"
            f"{'=' * 70}\n"
            f"Student ID:  {student.student_id}\n"
            f"Name:        {student.first_name} {student.last_name}\n"
            f"Program:     {student.program.program_name} "
            f"({student.program.program_code})\n"
            f"Commenced:   {student.program.commencement_date.strftime('%d/%m/%Y')}\n"
            f"{'-' * 70}\n"
        )
        return header
    
    def _generate_subject_table(self, student: Student) -> str:
        """Format the table of completed subjects and results."""
        table_header = (
            f"{'Code':<12} {'Subject':<30} {'CP':>4} {'Grade':<5}\n"
            f"{'-' * 70}\n"
        )
        rows = [
            f"{s.subject_code:<12} {s.subject_name:<30} "
            f"{s.credit_points:>4} {s.grade.name:<5}"
            for s in student.subjects_completed
        ]
        return table_header + "\n".join(rows)
    
    def _generate_summary(self, student: Student) -> str:
        """Format the GPA and total credit points summary."""
        summary = (
            f"\n{'-' * 70}\n"
            f"Total Credit Points Completed: {student.get_total_credit_points()}\n"
            f"Grade Point Average (GPA):     {student.get_gpa():.2f} / 4.0\n"
            f"{'=' * 70}\n"
        )
        return summary


class TranscriptExporter:
    """
    Exports transcripts to various file formats (PDF, TXT, JSON).
    Responsibility: handle persistence and format-specific serialisation.
    """
    
    def export_to_text(
        self,
        transcript: str,
        output_path: Path,
    ) -> None:
        """Save transcript as plain text file."""
        output_path.write_text(transcript, encoding="utf-8")
        print(f"✓ Transcript exported to {output_path}")
    
    def export_to_json(
        self,
        student: Student,
        output_path: Path,
    ) -> None:
        """Save student record as JSON (for data interoperability)."""
        
        data = {
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "program": student.program.program_name,
            "gpa": student.get_gpa(),
            "total_credit_points": student.get_total_credit_points(),
            "subjects": [
                {
                    "code": s.subject_code,
                    "name": s.subject_name,
                    "credit_points": s.credit_points,
                    "grade": s.grade.name,
                }
                for s in student.subjects_completed
            ],
        }
        output_path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )
        print(f"✓ JSON export saved to {output_path}")