from dataclasses import dataclass
from datetime import date
from typing import List
from pathlib import Path
from enum import Enum
import json

@dataclass
class Student:
    """
    Represents a student and manages their academic record.
    Responsibilities: enrol in subjects, record grades, provide record summary.
    """
    
    student_id: str
    first_name: str
    last_name: str
    program: 'Program'
    subjects_completed: List[Subject] = None
    
    def __post_init__(self):
        """Initialise empty subjects list if not provided."""
        if self.subjects_completed is None:
            self.subjects_completed = []
    
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

    WIDTH = 70  # centralise the line width as a constant

    def __init__(self):
        pass

    # -------------------------------------------------------------------------
    # Public interface
    # -------------------------------------------------------------------------

    def generate_transcript(self, student: Student) -> str:
        """
        Create a complete transcript as a formatted string.
        Includes header, subject results table, yearly breakdown,
        grade distribution, degree progress, and summary statistics.
        """
        sections = [
            self._generate_header(student),
            self._generate_subject_table(student),
            self._generate_yearly_breakdown(student),
            self._generate_grade_distribution(student),
            self._generate_degree_progress(student),
            self._generate_summary(student),
        ]
        return "\n".join(sections)

    # -------------------------------------------------------------------------
    # Private section builders
    # -------------------------------------------------------------------------

    def _generate_header(self, student: Student) -> str:
        """Format the student and program information section."""
        return (
            f"{'=' * self.WIDTH}\n"
            f"{'ACADEMIC TRANSCRIPT':^{self.WIDTH}}\n"
            f"{'=' * self.WIDTH}\n"
            f"Student ID:  {student.student_id}\n"
            f"Name:        {student.first_name} {student.last_name}\n"
            f"Program:     {student.program.program_name} "
            f"({student.program.program_code})\n"
            f"Commenced:   {student.program.commencement_date.strftime('%d/%m/%Y')}\n"
            f"Expected:    {student.program.expected_completion_date.strftime('%d/%m/%Y')}\n"
            f"{'-' * self.WIDTH}\n"
        )

    def _generate_subject_table(self, student: Student) -> str:
        """Format the table of completed subjects and results."""
        if not student.subjects_completed:
            return "No subjects completed.\n"

        table_header = (
            f"{'Code':<12} {'Subject':<30} {'CP':>4} {'Year':>5} {'Grade':<5}\n"
            f"{'-' * self.WIDTH}\n"
        )
        rows = [
            f"{s.subject_code:<12} {s.subject_name:<30} "
            f"{s.credit_points:>4} {s.year_completed:>5} {s.grade.name:<5}"
            for s in student.subjects_completed
        ]
        return table_header + "\n".join(rows) + "\n"

    def _generate_yearly_breakdown(self, student: Student) -> str:
        """
        Group completed subjects by year and display as sub-sections.
        Useful for seeing academic progression at a glance.
        """
        if not student.subjects_completed:
            return ""

        # Group subjects by year
        years: dict[int, list[Subject]] = {}
        for s in student.subjects_completed:
            years.setdefault(s.year_completed, []).append(s)

        lines = [f"\n{'YEARLY BREAKDOWN':^{self.WIDTH}}", f"{'-' * self.WIDTH}"]
        for year in sorted(years):
            subjects = years[year]
            year_credits = sum(s.credit_points for s in subjects)
            lines.append(f"\n  {year}  ({year_credits} CP)")
            for s in subjects:
                lines.append(f"    {s.subject_code:<12} {s.subject_name:<30} {s.grade.name}")

        return "\n".join(lines) + "\n"

    def _generate_grade_distribution(self, student: Student) -> str:
        """
        Show a count of each grade type achieved across all subjects.
        Gives a quick snapshot of overall academic performance.
        """
        if not student.subjects_completed:
            return ""

        # Count occurrences of each grade
        distribution: dict[GradeType, int] = {g: 0 for g in GradeType}
        for s in student.subjects_completed:
            distribution[s.grade] += 1

        lines = [f"\n{'GRADE DISTRIBUTION':^{self.WIDTH}}", f"{'-' * self.WIDTH}"]
        for grade_type, count in distribution.items():
            if count > 0:
                bar = "█" * count          # simple visual bar
                lines.append(f"  {grade_type.name:<4}  {bar:<20} {count}")

        return "\n".join(lines) + "\n"

    def _generate_degree_progress(self, student: Student) -> str:
        """
        Display progress toward total credit points required for graduation.
        Shows completed vs required and a simple text progress bar.
        """
        completed = student.get_total_credit_points()
        required = student.program.total_credit_points
        percentage = min(completed / required * 100, 100) if required > 0 else 0

        filled = int(percentage / 5)        # 20-block bar (100% / 5 = 20)
        bar = "█" * filled + "░" * (20 - filled)

        lines = [
            f"\n{'DEGREE PROGRESS':^{self.WIDTH}}",
            f"{'-' * self.WIDTH}",
            f"  Completed:  {completed} / {required} credit points",
            f"  Progress:   [{bar}] {percentage:.1f}%",
        ]

        if completed >= required:
            lines.append(f"  ✓ All credit points completed — eligible for graduation.")
        else:
            remaining = required - completed
            lines.append(f"  Remaining:  {remaining} credit points to complete.")

        return "\n".join(lines) + "\n"

    def _generate_summary(self, student: Student) -> str:
        """Format the GPA and total credit points summary."""
        gpa = student.get_gpa()
        standing = self._get_academic_standing(gpa)
        return (
            f"\n{'-' * self.WIDTH}\n"
            f"Total Credit Points Completed: {student.get_total_credit_points()}\n"
            f"Grade Point Average (GPA):     {gpa:.2f} / 4.0\n"
            f"Academic Standing:             {standing}\n"
            f"{'=' * self.WIDTH}\n"
        )

    # -------------------------------------------------------------------------
    # Helper
    # -------------------------------------------------------------------------

    def _get_academic_standing(self, gpa: float) -> str:
        """
        Map a GPA value to a descriptive academic standing label.

        Args:
            gpa: Weighted GPA on a 0.0–4.0 scale.

        Returns:
            str: Standing label e.g. 'High Distinction Standing'.
        """
        if gpa >= 3.5:
            return "High Distinction Standing"
        elif gpa >= 3.0:
            return "Distinction Standing"
        elif gpa >= 2.0:
            return "Credit Standing"
        elif gpa >= 1.0:
            return "Pass Standing"
        else:
            return "At Risk"
        
class TranscriptExporter:
    """
    Exports transcripts to various file formats (TXT, JSON, CSV, Markdown).
    Responsibility: handle persistence and format-specific serialisation.
    """

    ENCODING = "utf-8"

    def __init__(self):
        pass

    # -------------------------------------------------------------------------
    # Public interface
    # -------------------------------------------------------------------------

    def export_all(self, student: Student, transcript: str, output_dir: Path) -> None:
        """
        Convenience method — export all available formats in one call.
        Creates the output directory if it does not exist.

        Args:
            student:    The Student object to export data from.
            transcript: Pre-generated transcript string from TranscriptGenerator.
            output_dir: Directory to write all output files into.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        self.export_to_text(transcript, output_dir / f"{student.student_id}_transcript.txt")
        self.export_to_json(student, output_dir / f"{student.student_id}_record.json")
        self.export_to_csv(student, output_dir / f"{student.student_id}_subjects.csv")
        self.export_to_markdown(student, transcript, output_dir / f"{student.student_id}_transcript.md")

    # -------------------------------------------------------------------------
    # Format exporters
    # -------------------------------------------------------------------------

    def export_to_text(self, transcript: str, output_path: Path) -> None:
        """
        Save the pre-generated transcript string as a plain text file.

        Args:
            transcript:  Formatted transcript string.
            output_path: Destination file path.
        """
        try:
            output_path.write_text(transcript, encoding=self.ENCODING)
            print(f"✓ Text transcript exported to {output_path}")
        except OSError as e:
            print(f"✗ Failed to write text file: {e}")
            raise

    def export_to_json(self, student: Student, output_path: Path) -> None:
        """
        Serialise the student record to a structured JSON file.
        Suitable for data interchange or loading into other systems.

        Args:
            student:     The Student object to serialise.
            output_path: Destination file path.
        """
        data = self._build_json_payload(student)
        try:
            output_path.write_text(
                json.dumps(data, indent=2),
                encoding=self.ENCODING,
            )
            print(f"✓ JSON record exported to {output_path}")
        except OSError as e:
            print(f"✗ Failed to write JSON file: {e}")
            raise

    def export_to_csv(self, student: Student, output_path: Path) -> None:
        """
        Export the student's subject results as a CSV file.
        Each row represents one completed subject.

        Args:
            student:     The Student object whose subjects are exported.
            output_path: Destination file path.
        """
        import csv

        fieldnames = ["subject_code", "subject_name", "credit_points", "grade", "year_completed"]
        try:
            with output_path.open("w", newline="", encoding=self.ENCODING) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for s in student.subjects_completed:
                    writer.writerow({
                        "subject_code":   s.subject_code,
                        "subject_name":   s.subject_name,
                        "credit_points":  s.credit_points,
                        "grade":          s.grade.name,
                        "year_completed": s.year_completed,
                    })
            print(f"✓ CSV export saved to {output_path}")
        except OSError as e:
            print(f"✗ Failed to write CSV file: {e}")
            raise

    def export_to_markdown(
        self,
        student: Student,
        transcript: str,
        output_path: Path,
    ) -> None:
        """
        Export the transcript as a Markdown file.
        Wraps the plain text transcript in a code block with a metadata header.
        Useful for rendering in GitHub, Notion, or documentation tools.

        Args:
            student:     The Student object (used for metadata header).
            transcript:  Pre-generated transcript string.
            output_path: Destination file path.
        """
        md = self._build_markdown(student, transcript)
        try:
            output_path.write_text(md, encoding=self.ENCODING)
            print(f"✓ Markdown transcript exported to {output_path}")
        except OSError as e:
            print(f"✗ Failed to write Markdown file: {e}")
            raise

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _build_json_payload(self, student: Student) -> dict:
        """
        Build the dictionary structure for JSON serialisation.
        Kept separate so it can be tested or reused independently.

        Args:
            student: The Student object to convert.

        Returns:
            dict: A JSON-serialisable representation of the student record.
        """
        return {
            "student_id":          student.student_id,
            "first_name":          student.first_name,
            "last_name":           student.last_name,
            "program":             student.program.program_name,
            "program_code":        student.program.program_code,
            "total_credit_points": student.get_total_credit_points(),
            "gpa":                 student.get_gpa(),
            "commencement_date":   student.program.commencement_date.isoformat(),
            "expected_completion": student.program.expected_completion_date.isoformat(),
            "subjects": [
                {
                    "code":          s.subject_code,
                    "name":          s.subject_name,
                    "credit_points": s.credit_points,
                    "grade":         s.grade.name,
                    "year":          s.year_completed,
                    "grade_point":   s.grade_point_value(),
                }
                for s in student.subjects_completed
            ],
        }

    def _build_markdown(self, student: Student, transcript: str) -> str:
        """
        Wrap the transcript string in a Markdown document with a metadata header.

        Args:
            student:    The Student object (used for the title and metadata).
            transcript: Pre-generated plain text transcript.

        Returns:
            str: A complete Markdown-formatted document.
        """
        return (
            f"# Academic Transcript\n\n"
            f"| Field | Value |\n"
            f"|---|---|\n"
            f"| Student ID | {student.student_id} |\n"
            f"| Name | {student.first_name} {student.last_name} |\n"
            f"| Program | {student.program.program_name} ({student.program.program_code}) |\n"
            f"| GPA | {student.get_gpa():.2f} / 4.0 |\n"
            f"| Credit Points | {student.get_total_credit_points()} |\n\n"
            f"## Full Transcript\n\n"
            f"```\n{transcript}\n```\n"
        )
    
def main() -> None:
    """Main entry point demonstrating the transcript system."""
    
    # === Create a program ===
    program = Program(
        program_code="BDS",
        program_name="Bachelor of Data Science",
        total_credit_points=240,
        commencement_date=date(2023, 1, 15),
        expected_completion_date=date(2026, 11, 30),
    )
    
    # === Create a student ===
    student = Student(
        student_id="S12345678",
        first_name="Alice",
        last_name="Chen",
        program=program,
    )
    
    # === Add completed subjects ===
    subjects_data = [
        Subject("NIT1101", "Foundations of Programming", 12, GradeType.HD, 2023),
        Subject("NIT1102", "Data Fundamentals", 12, GradeType.D, 2023),
        Subject("NIT2112", "Object Orientated Programming", 12, GradeType.C, 2024),
        Subject("NIT2201", "Database Design", 12, GradeType.HD, 2024),
    ]
    
    for subject in subjects_data:
        student.add_subject_result(subject)
    
    # === Generate and display transcript ===
    generator = TranscriptGenerator()
    transcript = generator.generate_transcript(student)
    print(transcript)
    
    # === Export to files ===
    exporter = TranscriptExporter()
    exporter.export_all(student, transcript, Path("./transcripts"))

if __name__ == "__main__":
    main()