"""
Online Course Platform - Complete OOP Reference Implementation
==============================================================

This module demonstrates all major Object-Oriented Programming concepts
through a comprehensive Online Course Platform implementation.

Concepts Demonstrated:
- Class Hierarchies with Abstract Base Classes (ABC)
- Interfaces using ABC
- Encapsulation with private/protected attributes and properties
- Custom Exception Hierarchies
- Design Patterns: Factory, Adapter, Observer, Singleton
- Enums for type safety
- Business rule implementation

Author: OOP Learning Reference
Version: 1.0
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Set, Callable
from dataclasses import dataclass, field
import uuid


# =============================================================================
# SECTION 1: ENUMS - Type-safe constants for the platform
# =============================================================================

class CourseType(Enum):
    """Types of courses available on the platform."""
    VIDEO = auto()
    LIVE = auto()
    INTERACTIVE = auto()
    CERTIFICATION = auto()


class ContentType(Enum):
    """Types of content within a course."""
    VIDEO = auto()
    TEXT = auto()
    QUIZ = auto()
    ASSIGNMENT = auto()
    PROJECT = auto()


class DifficultyLevel(Enum):
    """Course difficulty levels."""
    BEGINNER = auto()
    INTERMEDIATE = auto()
    ADVANCED = auto()
    EXPERT = auto()


class EnrollmentStatus(Enum):
    """Status of a student's enrollment in a course."""
    ACTIVE = auto()
    COMPLETED = auto()
    EXPIRED = auto()
    REFUNDED = auto()
    PAUSED = auto()


class SubscriptionTier(Enum):
    """Available subscription tiers."""
    FREE = auto()
    BASIC = auto()
    PRO = auto()
    ENTERPRISE = auto()


class GradeStatus(Enum):
    """Status of grading for content."""
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    PASSED = auto()
    FAILED = auto()


class UserRole(Enum):
    """User roles on the platform."""
    STUDENT = auto()
    INSTRUCTOR = auto()
    TA = auto()
    ADMIN = auto()


# =============================================================================
# SECTION 2: CUSTOM EXCEPTIONS - Hierarchical exception handling
# =============================================================================

class PlatformException(Exception):
    """Base exception for all platform-related errors."""
    def __init__(self, message: str = "A platform error occurred"):
        self.message = message
        super().__init__(self.message)


class CourseException(PlatformException):
    """Base exception for course-related errors."""
    pass


class CourseNotFoundError(CourseException):
    """Raised when a requested course doesn't exist."""
    def __init__(self, course_id: str):
        super().__init__(f"Course with ID '{course_id}' not found")
        self.course_id = course_id


class CourseFullError(CourseException):
    """Raised when attempting to enroll in a full course."""
    def __init__(self, course_title: str, max_students: int):
        super().__init__(f"Course '{course_title}' is full (max: {max_students} students)")
        self.course_title = course_title
        self.max_students = max_students


class PrerequisiteNotMetError(CourseException):
    """Raised when prerequisites for a course haven't been completed."""
    def __init__(self, course_title: str, missing_prereqs: List[str]):
        prereqs_str = ", ".join(missing_prereqs)
        super().__init__(f"Prerequisites not met for '{course_title}'. Missing: {prereqs_str}")
        self.course_title = course_title
        self.missing_prereqs = missing_prereqs


class EnrollmentException(PlatformException):
    """Base exception for enrollment-related errors."""
    pass


class AlreadyEnrolledError(EnrollmentException):
    """Raised when a student is already enrolled in a course."""
    def __init__(self, student_name: str, course_title: str):
        super().__init__(f"'{student_name}' is already enrolled in '{course_title}'")
        self.student_name = student_name
        self.course_title = course_title


class EnrollmentExpiredError(EnrollmentException):
    """Raised when an enrollment has expired."""
    def __init__(self, course_title: str, expiry_date: datetime):
        super().__init__(f"Enrollment in '{course_title}' expired on {expiry_date.strftime('%Y-%m-%d')}")
        self.course_title = course_title
        self.expiry_date = expiry_date


class NotEnrolledError(EnrollmentException):
    """Raised when a user tries to access a course they're not enrolled in."""
    def __init__(self, course_title: str):
        super().__init__(f"Not enrolled in course '{course_title}'")
        self.course_title = course_title


class ContentException(PlatformException):
    """Base exception for content-related errors."""
    pass


class ContentLockedError(ContentException):
    """Raised when trying to access locked content."""
    def __init__(self, content_title: str, required_completion: str):
        super().__init__(f"Content '{content_title}' is locked. Complete '{required_completion}' first.")
        self.content_title = content_title
        self.required_completion = required_completion


class QuizAttemptLimitError(ContentException):
    """Raised when quiz attempt limit is reached."""
    def __init__(self, quiz_title: str, max_attempts: int):
        super().__init__(f"Maximum attempts ({max_attempts}) reached for quiz '{quiz_title}'")
        self.quiz_title = quiz_title
        self.max_attempts = max_attempts


class AssignmentPastDueError(ContentException):
    """Raised when an assignment is submitted past its due date."""
    def __init__(self, assignment_title: str, due_date: datetime):
        super().__init__(f"Assignment '{assignment_title}' was due on {due_date.strftime('%Y-%m-%d')}")
        self.assignment_title = assignment_title
        self.due_date = due_date


class PaymentException(PlatformException):
    """Base exception for payment-related errors."""
    pass


class SubscriptionRequiredError(PaymentException):
    """Raised when a feature requires a higher subscription tier."""
    def __init__(self, required_tier: SubscriptionTier, current_tier: SubscriptionTier):
        super().__init__(f"This feature requires {required_tier.name} subscription (current: {current_tier.name})")
        self.required_tier = required_tier
        self.current_tier = current_tier


class PaymentFailedError(PaymentException):
    """Raised when a payment transaction fails."""
    def __init__(self, amount: float, reason: str):
        super().__init__(f"Payment of ${amount:.2f} failed: {reason}")
        self.amount = amount
        self.reason = reason


class UserException(PlatformException):
    """Base exception for user-related errors."""
    pass


class InstructorNotApprovedError(UserException):
    """Raised when an unapproved instructor tries to create courses."""
    def __init__(self, instructor_name: str):
        super().__init__(f"Instructor '{instructor_name}' is not yet approved to create courses")
        self.instructor_name = instructor_name


# =============================================================================
# SECTION 3: INTERFACES (ABC classes) - Contract definitions
# =============================================================================

class Enrollable(ABC):
    """Interface for entities that support enrollment."""
    
    @abstractmethod
    def enroll(self, student: 'Student') -> bool:
        """Enroll a student in this entity."""
        pass
    
    @abstractmethod
    def unenroll(self, student: 'Student') -> bool:
        """Remove a student from this entity."""
        pass
    
    @abstractmethod
    def check_eligibility(self, student: 'Student') -> bool:
        """Check if a student is eligible to enroll."""
        pass


class Completable(ABC):
    """Interface for entities that can be completed."""
    
    @abstractmethod
    def mark_complete(self, user: 'User') -> bool:
        """Mark this entity as complete for a user."""
        pass
    
    @abstractmethod
    def get_progress(self, user: 'User') -> float:
        """Get completion progress (0.0 to 1.0) for a user."""
        pass
    
    @abstractmethod
    def calculate_grade(self, user: 'User') -> float:
        """Calculate the grade (0-100) for a user."""
        pass


class Observable(ABC):
    """Interface for implementing the Observer pattern."""
    
    @abstractmethod
    def add_observer(self, observer: 'Observer') -> None:
        """Add an observer to be notified of events."""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: 'Observer') -> None:
        """Remove an observer from notifications."""
        pass
    
    @abstractmethod
    def notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        pass


class Reviewable(ABC):
    """Interface for entities that can be reviewed."""
    
    @abstractmethod
    def add_review(self, user: 'User', rating: int, comment: str) -> 'Review':
        """Add a review from a user."""
        pass
    
    @abstractmethod
    def get_reviews(self) -> List['Review']:
        """Get all reviews for this entity."""
        pass
    
    @abstractmethod
    def get_average_rating(self) -> float:
        """Get the average rating across all reviews."""
        pass


# =============================================================================
# SECTION 4: OBSERVER PATTERN - Event handling system
# =============================================================================

class Observer(ABC):
    """Abstract base class for all observers."""
    
    @abstractmethod
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Called when an observed event occurs."""
        pass


class StudentNotifier(Observer):
    """Notifies students of important events via simulated email/push."""
    
    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        notification = {
            "timestamp": datetime.now(),
            "event": event,
            "recipient": data.get("student_name", "Unknown"),
            "message": self._generate_message(event, data)
        }
        self.notifications.append(notification)
        print(f"  📧 [StudentNotifier] Sent to {notification['recipient']}: {notification['message']}")
    
    def _generate_message(self, event: str, data: Dict[str, Any]) -> str:
        messages = {
            "enrolled": f"Welcome to '{data.get('course_title', 'the course')}'! Start learning today.",
            "lesson_completed": f"Great job completing '{data.get('content_title', 'the lesson')}'!",
            "quiz_passed": f"Congratulations! You passed '{data.get('quiz_title', 'the quiz')}' with {data.get('score', 0)}%",
            "course_completed": f"🎉 You've completed '{data.get('course_title', 'the course')}'!",
            "certificate_issued": f"Your certificate for '{data.get('course_title', 'the course')}' is ready!"
        }
        return messages.get(event, f"Event: {event}")


class InstructorNotifier(Observer):
    """Notifies instructors about student progress and course activity."""
    
    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        # Only notify instructors for relevant events
        instructor_events = {"enrolled", "course_completed", "new_review"}
        if event in instructor_events:
            notification = {
                "timestamp": datetime.now(),
                "event": event,
                "instructor": data.get("instructor_name", "Unknown"),
                "message": self._generate_message(event, data)
            }
            self.notifications.append(notification)
            print(f"  👨‍🏫 [InstructorNotifier] Notified {notification['instructor']}: {notification['message']}")
    
    def _generate_message(self, event: str, data: Dict[str, Any]) -> str:
        messages = {
            "enrolled": f"New student enrolled in '{data.get('course_title', 'your course')}'",
            "course_completed": f"A student completed '{data.get('course_title', 'your course')}'",
            "new_review": f"New review received for '{data.get('course_title', 'your course')}'"
        }
        return messages.get(event, f"Event: {event}")


class CertificateGenerator(Observer):
    """Generates certificates when courses are completed."""
    
    def __init__(self):
        self.certificates: List['Certificate'] = []
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        if event == "course_completed" and data.get("passed", False):
            certificate = Certificate(
                student_name=data.get("student_name", "Unknown"),
                course_title=data.get("course_title", "Unknown Course"),
                grade=data.get("grade", 0),
                completion_date=datetime.now()
            )
            self.certificates.append(certificate)
            print(f"  🎓 [CertificateGenerator] Certificate generated for {certificate.student_name}")
            # Trigger certificate issued notification
            data["certificate_id"] = certificate.certificate_id


class AnalyticsDashboard(Observer):
    """Collects analytics data from platform events."""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.metrics: Dict[str, int] = {
            "total_enrollments": 0,
            "total_completions": 0,
            "total_quiz_attempts": 0,
            "total_certificates": 0
        }
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        self.events.append({
            "timestamp": datetime.now(),
            "event": event,
            "data": data.copy()
        })
        
        # Update metrics
        if event == "enrolled":
            self.metrics["total_enrollments"] += 1
        elif event == "course_completed":
            self.metrics["total_completions"] += 1
        elif event == "quiz_attempted":
            self.metrics["total_quiz_attempts"] += 1
        elif event == "certificate_issued":
            self.metrics["total_certificates"] += 1
        
        print(f"  📊 [AnalyticsDashboard] Recorded event: {event}")
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "metrics": self.metrics.copy(),
            "total_events": len(self.events)
        }


@dataclass
class Certificate:
    """Represents a completion certificate."""
    student_name: str
    course_title: str
    grade: float
    completion_date: datetime
    certificate_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    
    def __str__(self) -> str:
        return (f"Certificate {self.certificate_id}: {self.student_name} completed "
                f"'{self.course_title}' with grade {self.grade:.1f}%")


# =============================================================================
# SECTION 5: SINGLETON PATTERN - Platform Registry
# =============================================================================

class SingletonMeta(type):
    """
    Metaclass implementing the Singleton pattern.
    Ensures only one instance of a class exists.
    """
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class LearningPlatformRegistry(metaclass=SingletonMeta):
    """
    Central registry for all platform entities.
    Implements Singleton pattern to ensure single source of truth.
    """
    
    def __init__(self):
        self._courses: Dict[str, 'Course'] = {}
        self._users: Dict[str, 'User'] = {}
        self._enrollments: Dict[str, List['Enrollment']] = {}  # user_id -> enrollments
        self._progress: Dict[str, Dict[str, 'Progress']] = {}  # user_id -> {course_id -> progress}
        self._observers: List[Observer] = []
        
        # Initialize with default observers
        self._student_notifier = StudentNotifier()
        self._instructor_notifier = InstructorNotifier()
        self._certificate_generator = CertificateGenerator()
        self._analytics = AnalyticsDashboard()
        
        self._observers.extend([
            self._student_notifier,
            self._instructor_notifier,
            self._certificate_generator,
            self._analytics
        ])
    
    def register_course(self, course: 'Course') -> None:
        """Register a new course on the platform."""
        self._courses[course.course_id] = course
        print(f"  ✅ Course registered: '{course.title}'")
    
    def get_course(self, course_id: str) -> 'Course':
        """Get a course by ID."""
        if course_id not in self._courses:
            raise CourseNotFoundError(course_id)
        return self._courses[course_id]
    
    def register_user(self, user: 'User') -> None:
        """Register a new user on the platform."""
        self._users[user.user_id] = user
        self._enrollments[user.user_id] = []
        self._progress[user.user_id] = {}
    
    def get_user(self, user_id: str) -> 'User':
        """Get a user by ID."""
        if user_id not in self._users:
            raise UserException(f"User with ID '{user_id}' not found")
        return self._users[user_id]
    
    def create_enrollment(self, student: 'Student', course: 'Course') -> 'Enrollment':
        """Create a new enrollment."""
        enrollment = Enrollment(student=student, course=course)
        self._enrollments[student.user_id].append(enrollment)
        self._progress[student.user_id][course.course_id] = Progress(
            student_id=student.user_id,
            course_id=course.course_id
        )
        return enrollment
    
    def get_user_enrollments(self, user_id: str) -> List['Enrollment']:
        """Get all enrollments for a user."""
        return self._enrollments.get(user_id, [])
    
    def get_progress(self, user_id: str, course_id: str) -> Optional['Progress']:
        """Get progress for a user in a course."""
        return self._progress.get(user_id, {}).get(course_id)
    
    def notify_all(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all registered observers of an event."""
        for observer in self._observers:
            observer.update(event, data)
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary from the dashboard."""
        return self._analytics.get_summary()
    
    @property
    def all_courses(self) -> List['Course']:
        """Get all registered courses."""
        return list(self._courses.values())
    
    @property
    def all_users(self) -> List['User']:
        """Get all registered users."""
        return list(self._users.values())


# =============================================================================
# SECTION 6: REVIEW AND PROGRESS TRACKING
# =============================================================================

@dataclass
class Review:
    """Represents a user review of a course."""
    user_id: str
    user_name: str
    rating: int  # 1-5
    comment: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")


@dataclass
class Progress:
    """Tracks a student's progress in a course."""
    student_id: str
    course_id: str
    completed_content: Set[str] = field(default_factory=set)
    quiz_attempts: Dict[str, int] = field(default_factory=dict)
    quiz_scores: Dict[str, List[float]] = field(default_factory=dict)
    assignment_scores: Dict[str, float] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def mark_content_complete(self, content_id: str) -> None:
        """Mark a piece of content as complete."""
        self.completed_content.add(content_id)
    
    def record_quiz_attempt(self, quiz_id: str, score: float) -> None:
        """Record a quiz attempt."""
        self.quiz_attempts[quiz_id] = self.quiz_attempts.get(quiz_id, 0) + 1
        if quiz_id not in self.quiz_scores:
            self.quiz_scores[quiz_id] = []
        self.quiz_scores[quiz_id].append(score)
    
    def get_quiz_attempts(self, quiz_id: str) -> int:
        """Get number of attempts for a quiz."""
        return self.quiz_attempts.get(quiz_id, 0)
    
    def get_best_quiz_score(self, quiz_id: str) -> float:
        """Get the best score for a quiz."""
        scores = self.quiz_scores.get(quiz_id, [])
        return max(scores) if scores else 0.0


# =============================================================================
# SECTION 7: SUBSCRIPTION HIERARCHY
# =============================================================================

class Subscription(ABC):
    """Abstract base class for subscription plans."""
    
    def __init__(self, user: 'User'):
        self._user = user
        self._tier = SubscriptionTier.FREE
        self._start_date = datetime.now()
        self._features: Dict[str, Any] = {}
    
    @property
    def tier(self) -> SubscriptionTier:
        return self._tier
    
    @property
    @abstractmethod
    def max_concurrent_courses(self) -> int:
        """Maximum number of courses that can be taken simultaneously."""
        pass
    
    @property
    @abstractmethod
    def quiz_attempts_per_quiz(self) -> int:
        """Maximum quiz attempts allowed per quiz."""
        pass
    
    @property
    @abstractmethod
    def has_certificates(self) -> bool:
        """Whether certificates are included."""
        pass
    
    @property
    @abstractmethod
    def has_downloadable_resources(self) -> bool:
        """Whether downloadable resources are available."""
        pass
    
    @property
    @abstractmethod
    def monthly_price(self) -> float:
        """Monthly subscription price."""
        pass
    
    @abstractmethod
    def can_access_feature(self, feature: str) -> bool:
        """Check if a feature is accessible with this subscription."""
        pass


class FreeTier(Subscription):
    """Free subscription tier with limited features."""
    
    def __init__(self, user: 'User'):
        super().__init__(user)
        self._tier = SubscriptionTier.FREE
        self._features = {
            "basic_courses": True,
            "community_forums": True,
            "email_support": False,
            "certificates": False,
            "downloadable_resources": False,
            "priority_support": False
        }
    
    @property
    def max_concurrent_courses(self) -> int:
        return 1
    
    @property
    def quiz_attempts_per_quiz(self) -> int:
        return 3
    
    @property
    def has_certificates(self) -> bool:
        return False
    
    @property
    def has_downloadable_resources(self) -> bool:
        return False
    
    @property
    def monthly_price(self) -> float:
        return 0.0
    
    def can_access_feature(self, feature: str) -> bool:
        return self._features.get(feature, False)


class BasicPlan(Subscription):
    """Basic paid subscription with more features."""
    
    def __init__(self, user: 'User'):
        super().__init__(user)
        self._tier = SubscriptionTier.BASIC
        self._features = {
            "basic_courses": True,
            "community_forums": True,
            "email_support": True,
            "certificates": False,
            "downloadable_resources": True,
            "priority_support": False
        }
    
    @property
    def max_concurrent_courses(self) -> int:
        return 5
    
    @property
    def quiz_attempts_per_quiz(self) -> int:
        return 10
    
    @property
    def has_certificates(self) -> bool:
        return False
    
    @property
    def has_downloadable_resources(self) -> bool:
        return True
    
    @property
    def monthly_price(self) -> float:
        return 9.99
    
    def can_access_feature(self, feature: str) -> bool:
        return self._features.get(feature, False)


class ProPlan(Subscription):
    """Pro subscription with full features."""
    
    def __init__(self, user: 'User'):
        super().__init__(user)
        self._tier = SubscriptionTier.PRO
        self._features = {
            "basic_courses": True,
            "community_forums": True,
            "email_support": True,
            "certificates": True,
            "downloadable_resources": True,
            "priority_support": True,
            "offline_access": True
        }
    
    @property
    def max_concurrent_courses(self) -> int:
        return 999  # Unlimited
    
    @property
    def quiz_attempts_per_quiz(self) -> int:
        return 999  # Unlimited
    
    @property
    def has_certificates(self) -> bool:
        return True
    
    @property
    def has_downloadable_resources(self) -> bool:
        return True
    
    @property
    def monthly_price(self) -> float:
        return 29.99
    
    def can_access_feature(self, feature: str) -> bool:
        return self._features.get(feature, False)


class EnterprisePlan(Subscription):
    """Enterprise subscription with team features and API access."""
    
    def __init__(self, user: 'User', team_size: int = 10):
        super().__init__(user)
        self._tier = SubscriptionTier.ENTERPRISE
        self._team_size = team_size
        self._features = {
            "basic_courses": True,
            "community_forums": True,
            "email_support": True,
            "certificates": True,
            "downloadable_resources": True,
            "priority_support": True,
            "offline_access": True,
            "team_management": True,
            "custom_branding": True,
            "api_access": True,
            "sso_integration": True
        }
    
    @property
    def max_concurrent_courses(self) -> int:
        return 999  # Unlimited
    
    @property
    def quiz_attempts_per_quiz(self) -> int:
        return 999  # Unlimited
    
    @property
    def has_certificates(self) -> bool:
        return True
    
    @property
    def has_downloadable_resources(self) -> bool:
        return True
    
    @property
    def monthly_price(self) -> float:
        return 99.99 + (self._team_size * 10)  # Base + per seat
    
    @property
    def team_size(self) -> int:
        return self._team_size
    
    def can_access_feature(self, feature: str) -> bool:
        return self._features.get(feature, False)


# =============================================================================
# SECTION 8: USER HIERARCHY
# =============================================================================

class User(ABC):
    """Abstract base class for all platform users."""
    
    def __init__(self, name: str, email: str):
        self._user_id = str(uuid.uuid4())[:8]
        self._name = name
        self._email = email
        self._created_at = datetime.now()
        self._role = UserRole.STUDENT
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError("Invalid email format")
        self._email = value
    
    @property
    def role(self) -> UserRole:
        return self._role
    
    @abstractmethod
    def get_permissions(self) -> Set[str]:
        """Get the permissions for this user type."""
        pass
    
    def __str__(self) -> str:
        return f"{self._role.name}: {self._name} ({self._email})"


class Student(User):
    """Represents a student on the platform."""
    
    def __init__(self, name: str, email: str, subscription: Optional[Subscription] = None):
        super().__init__(name, email)
        self._role = UserRole.STUDENT
        self._subscription: Subscription = subscription if subscription else FreeTier(self)
        self._completed_courses: List[str] = []
        self._certificates: List[Certificate] = []
    
    @property
    def subscription(self) -> Subscription:
        return self._subscription
    
    @subscription.setter
    def subscription(self, value: Subscription) -> None:
        self._subscription = value
    
    @property
    def completed_courses(self) -> List[str]:
        return self._completed_courses.copy()
    
    def add_completed_course(self, course_id: str) -> None:
        """Record a completed course."""
        if course_id not in self._completed_courses:
            self._completed_courses.append(course_id)
    
    def add_certificate(self, certificate: Certificate) -> None:
        """Add a certificate to the student's collection."""
        self._certificates.append(certificate)
    
    def get_permissions(self) -> Set[str]:
        return {
            "view_courses",
            "enroll_courses",
            "submit_assignments",
            "take_quizzes",
            "view_progress",
            "write_reviews"
        }


class Instructor(User):
    """Represents an instructor who creates and manages courses."""
    
    def __init__(self, name: str, email: str, bio: str = ""):
        super().__init__(name, email)
        self._role = UserRole.INSTRUCTOR
        self._bio = bio
        self._is_approved = False
        self._courses_created: List[str] = []
        self._total_revenue = 0.0
        self._revenue_share = 0.50  # 50% revenue share
    
    @property
    def bio(self) -> str:
        return self._bio
    
    @property
    def is_approved(self) -> bool:
        return self._is_approved
    
    def approve(self) -> None:
        """Approve this instructor to create courses."""
        self._is_approved = True
    
    @property
    def courses_created(self) -> List[str]:
        return self._courses_created.copy()
    
    def add_course(self, course_id: str) -> None:
        """Record a course created by this instructor."""
        self._courses_created.append(course_id)
    
    @property
    def total_revenue(self) -> float:
        return self._total_revenue
    
    def add_revenue(self, amount: float) -> None:
        """Add revenue from course sales."""
        self._total_revenue += amount * self._revenue_share
    
    def get_permissions(self) -> Set[str]:
        return {
            "view_courses",
            "create_courses",
            "edit_own_courses",
            "view_student_progress",
            "grade_assignments",
            "view_analytics",
            "respond_reviews"
        }


class TeachingAssistant(User):
    """Represents a teaching assistant who helps with courses."""
    
    def __init__(self, name: str, email: str, assigned_instructor: Instructor):
        super().__init__(name, email)
        self._role = UserRole.TA
        self._assigned_instructor = assigned_instructor
        self._assigned_courses: List[str] = []
    
    @property
    def assigned_instructor(self) -> Instructor:
        return self._assigned_instructor
    
    @property
    def assigned_courses(self) -> List[str]:
        return self._assigned_courses.copy()
    
    def assign_to_course(self, course_id: str) -> None:
        """Assign this TA to a course."""
        self._assigned_courses.append(course_id)
    
    def get_permissions(self) -> Set[str]:
        return {
            "view_courses",
            "view_student_progress",
            "grade_assignments",
            "answer_questions",
            "moderate_discussions"
        }


class Admin(User):
    """Represents a platform administrator with full access."""
    
    def __init__(self, name: str, email: str):
        super().__init__(name, email)
        self._role = UserRole.ADMIN
    
    def approve_instructor(self, instructor: Instructor) -> None:
        """Approve an instructor to create courses."""
        instructor.approve()
        print(f"  ✅ Admin {self._name} approved instructor {instructor.name}")
    
    def get_permissions(self) -> Set[str]:
        return {
            "view_courses",
            "create_courses",
            "edit_all_courses",
            "delete_courses",
            "manage_users",
            "approve_instructors",
            "view_all_analytics",
            "manage_subscriptions",
            "issue_refunds",
            "system_settings"
        }


# =============================================================================
# SECTION 9: CONTENT HIERARCHY
# =============================================================================

class Content(ABC):
    """Abstract base class for all course content."""
    
    def __init__(self, title: str, description: str, order: int):
        self._content_id = str(uuid.uuid4())[:8]
        self._title = title
        self._description = description
        self._order = order
        self._content_type = ContentType.TEXT
        self._duration_minutes = 0
        self._is_required = True
    
    @property
    def content_id(self) -> str:
        return self._content_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def order(self) -> int:
        return self._order
    
    @property
    def content_type(self) -> ContentType:
        return self._content_type
    
    @property
    def is_required(self) -> bool:
        return self._is_required
    
    @abstractmethod
    def get_completion_criteria(self) -> str:
        """Get the criteria for completing this content."""
        pass
    
    @abstractmethod
    def check_completion(self, progress: Progress) -> bool:
        """Check if this content is completed based on progress."""
        pass
    
    def __str__(self) -> str:
        return f"[{self._content_type.name}] {self._title}"


class VideoLesson(Content):
    """Video-based lesson content."""
    
    def __init__(self, title: str, description: str, order: int, 
                 video_url: str, duration_minutes: int):
        super().__init__(title, description, order)
        self._content_type = ContentType.VIDEO
        self._video_url = video_url
        self._duration_minutes = duration_minutes
        self._transcript: Optional[str] = None
    
    @property
    def video_url(self) -> str:
        return self._video_url
    
    @property
    def duration_minutes(self) -> int:
        return self._duration_minutes
    
    def get_completion_criteria(self) -> str:
        return f"Watch the complete video ({self._duration_minutes} minutes)"
    
    def check_completion(self, progress: Progress) -> bool:
        return self._content_id in progress.completed_content


class TextLesson(Content):
    """Text-based lesson content."""
    
    def __init__(self, title: str, description: str, order: int,
                 content_text: str, reading_time_minutes: int):
        super().__init__(title, description, order)
        self._content_type = ContentType.TEXT
        self._content_text = content_text
        self._duration_minutes = reading_time_minutes
    
    @property
    def content_text(self) -> str:
        return self._content_text
    
    def get_completion_criteria(self) -> str:
        return f"Read the lesson content (est. {self._duration_minutes} minutes)"
    
    def check_completion(self, progress: Progress) -> bool:
        return self._content_id in progress.completed_content


class Quiz(Content):
    """Quiz content for assessment."""
    
    def __init__(self, title: str, description: str, order: int,
                 questions: List[Dict[str, Any]], passing_score: float = 70.0):
        super().__init__(title, description, order)
        self._content_type = ContentType.QUIZ
        self._questions = questions
        self._passing_score = passing_score
        self._time_limit_minutes: Optional[int] = None
    
    @property
    def questions(self) -> List[Dict[str, Any]]:
        return self._questions.copy()
    
    @property
    def passing_score(self) -> float:
        return self._passing_score
    
    @property
    def question_count(self) -> int:
        return len(self._questions)
    
    def grade_attempt(self, answers: Dict[int, str]) -> float:
        """Grade a quiz attempt and return the score."""
        if not self._questions:
            return 100.0
        
        correct = 0
        for i, question in enumerate(self._questions):
            if answers.get(i) == question.get("correct_answer"):
                correct += 1
        
        return (correct / len(self._questions)) * 100
    
    def get_completion_criteria(self) -> str:
        return f"Pass the quiz with at least {self._passing_score}%"
    
    def check_completion(self, progress: Progress) -> bool:
        best_score = progress.get_best_quiz_score(self._content_id)
        return best_score >= self._passing_score


class Assignment(Content):
    """Assignment content requiring submission."""
    
    def __init__(self, title: str, description: str, order: int,
                 instructions: str, max_points: int, due_date: Optional[datetime] = None):
        super().__init__(title, description, order)
        self._content_type = ContentType.ASSIGNMENT
        self._instructions = instructions
        self._max_points = max_points
        self._due_date = due_date
        self._rubric: List[Dict[str, Any]] = []
    
    @property
    def instructions(self) -> str:
        return self._instructions
    
    @property
    def max_points(self) -> int:
        return self._max_points
    
    @property
    def due_date(self) -> Optional[datetime]:
        return self._due_date
    
    def is_past_due(self) -> bool:
        """Check if the assignment is past its due date."""
        if self._due_date is None:
            return False
        return datetime.now() > self._due_date
    
    def get_completion_criteria(self) -> str:
        due_str = f" (Due: {self._due_date.strftime('%Y-%m-%d')})" if self._due_date else ""
        return f"Submit assignment and receive a passing grade{due_str}"
    
    def check_completion(self, progress: Progress) -> bool:
        score = progress.assignment_scores.get(self._content_id, 0)
        return score >= (self._max_points * 0.7)  # 70% to pass


class Project(Content):
    """Project content for capstone/portfolio work."""
    
    def __init__(self, title: str, description: str, order: int,
                 requirements: List[str], peer_review_required: bool = True):
        super().__init__(title, description, order)
        self._content_type = ContentType.PROJECT
        self._requirements = requirements
        self._peer_review_required = peer_review_required
        self._estimated_hours = 10
    
    @property
    def requirements(self) -> List[str]:
        return self._requirements.copy()
    
    @property
    def peer_review_required(self) -> bool:
        return self._peer_review_required
    
    def get_completion_criteria(self) -> str:
        review_str = " and pass peer review" if self._peer_review_required else ""
        return f"Complete all project requirements{review_str}"
    
    def check_completion(self, progress: Progress) -> bool:
        return self._content_id in progress.completed_content


# =============================================================================
# SECTION 10: COURSE HIERARCHY
# =============================================================================

class Course(Enrollable, Completable, Observable, Reviewable):
    """Abstract base class for all courses."""
    
    def __init__(self, title: str, description: str, instructor: Instructor,
                 price: float, difficulty: DifficultyLevel):
        self._course_id = str(uuid.uuid4())[:8]
        self._title = title
        self._description = description
        self._instructor = instructor
        self._price = price
        self._difficulty = difficulty
        self._course_type = CourseType.VIDEO
        self._content: List[Content] = []
        self._prerequisites: List[str] = []  # Course IDs
        self._enrolled_students: Set[str] = set()  # Student IDs
        self._max_students: Optional[int] = None
        self._reviews: List[Review] = []
        self._observers: List[Observer] = []
        self._created_at = datetime.now()
        self._is_published = False
    
    # ---------- Property Getters/Setters (Encapsulation) ----------
    
    @property
    def course_id(self) -> str:
        return self._course_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        if len(value) < 3:
            raise ValueError("Course title must be at least 3 characters")
        self._title = value
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def instructor(self) -> Instructor:
        return self._instructor
    
    @property
    def price(self) -> float:
        return self._price
    
    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value
    
    @property
    def difficulty(self) -> DifficultyLevel:
        return self._difficulty
    
    @property
    def course_type(self) -> CourseType:
        return self._course_type
    
    @property
    def content(self) -> List[Content]:
        return self._content.copy()
    
    @property
    def prerequisites(self) -> List[str]:
        return self._prerequisites.copy()
    
    @property
    def enrolled_count(self) -> int:
        return len(self._enrolled_students)
    
    @property
    def is_published(self) -> bool:
        return self._is_published
    
    # ---------- Content Management ----------
    
    def add_content(self, content: Content) -> None:
        """Add content to the course."""
        self._content.append(content)
        self._content.sort(key=lambda c: c.order)
    
    def add_prerequisite(self, course_id: str) -> None:
        """Add a prerequisite course."""
        if course_id not in self._prerequisites:
            self._prerequisites.append(course_id)
    
    def publish(self) -> None:
        """Publish the course, making it available for enrollment."""
        if not self._content:
            raise CourseException("Cannot publish a course with no content")
        self._is_published = True
    
    # ---------- Enrollable Interface Implementation ----------
    
    def enroll(self, student: Student) -> bool:
        """Enroll a student in the course."""
        if not self.check_eligibility(student):
            return False
        
        if student.user_id in self._enrolled_students:
            raise AlreadyEnrolledError(student.name, self._title)
        
        if self._max_students and len(self._enrolled_students) >= self._max_students:
            raise CourseFullError(self._title, self._max_students)
        
        self._enrolled_students.add(student.user_id)
        self._instructor.add_revenue(self._price)
        
        # Notify observers
        self.notify_observers("enrolled", {
            "student_name": student.name,
            "student_id": student.user_id,
            "course_title": self._title,
            "course_id": self._course_id,
            "instructor_name": self._instructor.name
        })
        
        return True
    
    def unenroll(self, student: Student) -> bool:
        """Remove a student from the course."""
        if student.user_id not in self._enrolled_students:
            raise NotEnrolledError(self._title)
        
        self._enrolled_students.remove(student.user_id)
        return True
    
    def check_eligibility(self, student: Student) -> bool:
        """Check if a student is eligible to enroll."""
        # Check subscription limits
        registry = LearningPlatformRegistry()
        active_enrollments = [
            e for e in registry.get_user_enrollments(student.user_id)
            if e.status == EnrollmentStatus.ACTIVE
        ]
        
        if len(active_enrollments) >= student.subscription.max_concurrent_courses:
            return False
        
        # Check prerequisites
        missing = self._get_missing_prerequisites(student)
        if missing:
            raise PrerequisiteNotMetError(self._title, missing)
        
        return True
    
    def _get_missing_prerequisites(self, student: Student) -> List[str]:
        """Get list of missing prerequisites for a student."""
        completed = set(student.completed_courses)
        missing = []
        registry = LearningPlatformRegistry()
        
        for prereq_id in self._prerequisites:
            if prereq_id not in completed:
                try:
                    prereq_course = registry.get_course(prereq_id)
                    missing.append(prereq_course.title)
                except CourseNotFoundError:
                    missing.append(prereq_id)
        
        return missing
    
    # ---------- Completable Interface Implementation ----------
    
    def mark_complete(self, user: User) -> bool:
        """Mark the course as complete for a user."""
        if not isinstance(user, Student):
            return False
        
        progress = self.get_progress(user)
        if progress < 1.0:
            return False
        
        grade = self.calculate_grade(user)
        passed = grade >= 70.0
        
        if passed:
            user.add_completed_course(self._course_id)
        
        # Notify observers
        self.notify_observers("course_completed", {
            "student_name": user.name,
            "student_id": user.user_id,
            "course_title": self._title,
            "course_id": self._course_id,
            "instructor_name": self._instructor.name,
            "grade": grade,
            "passed": passed
        })
        
        return passed
    
    def get_progress(self, user: User) -> float:
        """Get completion progress (0.0 to 1.0) for a user."""
        registry = LearningPlatformRegistry()
        progress = registry.get_progress(user.user_id, self._course_id)
        
        if not progress or not self._content:
            return 0.0
        
        required_content = [c for c in self._content if c.is_required]
        if not required_content:
            return 1.0
        
        completed = sum(1 for c in required_content if c.check_completion(progress))
        return completed / len(required_content)
    
    def calculate_grade(self, user: User) -> float:
        """Calculate the overall grade for a user."""
        registry = LearningPlatformRegistry()
        progress = registry.get_progress(user.user_id, self._course_id)
        
        if not progress:
            return 0.0
        
        grades = []
        
        # Include quiz scores
        for content in self._content:
            if isinstance(content, Quiz):
                best_score = progress.get_best_quiz_score(content.content_id)
                if best_score > 0:
                    grades.append(best_score)
        
        # Include assignment scores
        for content in self._content:
            if isinstance(content, Assignment):
                score = progress.assignment_scores.get(content.content_id, 0)
                if score > 0:
                    # Convert to percentage
                    grades.append((score / content.max_points) * 100)
        
        return sum(grades) / len(grades) if grades else 0.0
    
    # ---------- Observable Interface Implementation ----------
    
    def add_observer(self, observer: Observer) -> None:
        """Add an observer to be notified of events."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        """Remove an observer from notifications."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        # Notify course-level observers
        for observer in self._observers:
            observer.update(event, data)
        
        # Also notify platform-level observers
        registry = LearningPlatformRegistry()
        registry.notify_all(event, data)
    
    # ---------- Reviewable Interface Implementation ----------
    
    def add_review(self, user: User, rating: int, comment: str) -> Review:
        """Add a review from a user."""
        review = Review(
            user_id=user.user_id,
            user_name=user.name,
            rating=rating,
            comment=comment
        )
        self._reviews.append(review)
        
        self.notify_observers("new_review", {
            "course_title": self._title,
            "course_id": self._course_id,
            "instructor_name": self._instructor.name,
            "rating": rating,
            "reviewer": user.name
        })
        
        return review
    
    def get_reviews(self) -> List[Review]:
        """Get all reviews for this course."""
        return self._reviews.copy()
    
    def get_average_rating(self) -> float:
        """Get the average rating across all reviews."""
        if not self._reviews:
            return 0.0
        return sum(r.rating for r in self._reviews) / len(self._reviews)
    
    # ---------- Abstract Methods for Subclasses ----------
    
    @abstractmethod
    def get_delivery_method(self) -> str:
        """Get the delivery method for this course type."""
        pass
    
    def __str__(self) -> str:
        return (f"[{self._course_type.name}] {self._title} by {self._instructor.name} "
                f"(${self._price:.2f}, {self._difficulty.name})")


class VideoCourse(Course):
    """Pre-recorded video course."""
    
    def __init__(self, title: str, description: str, instructor: Instructor,
                 price: float, difficulty: DifficultyLevel, total_hours: float):
        super().__init__(title, description, instructor, price, difficulty)
        self._course_type = CourseType.VIDEO
        self._total_hours = total_hours
        self._has_captions = True
        self._playback_speed_options = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    
    @property
    def total_hours(self) -> float:
        return self._total_hours
    
    def get_delivery_method(self) -> str:
        return "Self-paced video lessons with lifetime access"


class LiveCourse(Course):
    """Live instructor-led course."""
    
    def __init__(self, title: str, description: str, instructor: Instructor,
                 price: float, difficulty: DifficultyLevel,
                 start_date: datetime, end_date: datetime, max_students: int = 30):
        super().__init__(title, description, instructor, price, difficulty)
        self._course_type = CourseType.LIVE
        self._start_date = start_date
        self._end_date = end_date
        self._max_students = max_students
        self._schedule: List[Dict[str, Any]] = []
    
    @property
    def start_date(self) -> datetime:
        return self._start_date
    
    @property
    def end_date(self) -> datetime:
        return self._end_date
    
    def add_session(self, date: datetime, topic: str, duration_hours: float) -> None:
        """Add a live session to the schedule."""
        self._schedule.append({
            "date": date,
            "topic": topic,
            "duration_hours": duration_hours
        })
    
    def get_delivery_method(self) -> str:
        return f"Live sessions from {self._start_date.strftime('%b %d')} to {self._end_date.strftime('%b %d, %Y')}"


class InteractiveCourse(Course):
    """Interactive course with hands-on exercises."""
    
    def __init__(self, title: str, description: str, instructor: Instructor,
                 price: float, difficulty: DifficultyLevel, sandbox_type: str):
        super().__init__(title, description, instructor, price, difficulty)
        self._course_type = CourseType.INTERACTIVE
        self._sandbox_type = sandbox_type  # e.g., "python", "javascript", "sql"
        self._exercises_count = 0
    
    @property
    def sandbox_type(self) -> str:
        return self._sandbox_type
    
    def add_content(self, content: Content) -> None:
        super().add_content(content)
        if isinstance(content, (Quiz, Assignment, Project)):
            self._exercises_count += 1
    
    def get_delivery_method(self) -> str:
        return f"Interactive {self._sandbox_type} coding environment with {self._exercises_count} exercises"


class CertificationCourse(Course):
    """Course leading to a professional certification."""
    
    def __init__(self, title: str, description: str, instructor: Instructor,
                 price: float, difficulty: DifficultyLevel,
                 certification_name: str, validity_years: int = 2):
        super().__init__(title, description, instructor, price, difficulty)
        self._course_type = CourseType.CERTIFICATION
        self._certification_name = certification_name
        self._validity_years = validity_years
        self._passing_grade = 80.0  # Higher standard for certification
        self._proctored_exam = True
    
    @property
    def certification_name(self) -> str:
        return self._certification_name
    
    @property
    def validity_years(self) -> int:
        return self._validity_years
    
    def mark_complete(self, user: User) -> bool:
        """Certification courses require a higher passing grade."""
        if not isinstance(user, Student):
            return False
        
        grade = self.calculate_grade(user)
        passed = grade >= self._passing_grade
        
        if passed:
            user.add_completed_course(self._course_id)
        
        self.notify_observers("course_completed", {
            "student_name": user.name,
            "student_id": user.user_id,
            "course_title": self._title,
            "course_id": self._course_id,
            "instructor_name": self._instructor.name,
            "grade": grade,
            "passed": passed,
            "certification": self._certification_name if passed else None
        })
        
        return passed
    
    def get_delivery_method(self) -> str:
        return f"Certification prep with proctored exam. Certificate valid for {self._validity_years} years."


# =============================================================================
# SECTION 11: ENROLLMENT
# =============================================================================

@dataclass
class Enrollment:
    """Represents a student's enrollment in a course."""
    student: Student
    course: 'Course'
    enrolled_at: datetime = field(default_factory=datetime.now)
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        # Set default expiration for free tier
        if self.student.subscription.tier == SubscriptionTier.FREE:
            self.expires_at = self.enrolled_at + timedelta(days=30)
    
    def is_active(self) -> bool:
        """Check if the enrollment is currently active."""
        if self.status != EnrollmentStatus.ACTIVE:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            self.status = EnrollmentStatus.EXPIRED
            return False
        return True
    
    def calculate_refund_eligibility(self) -> Dict[str, Any]:
        """Calculate if the student is eligible for a refund."""
        days_enrolled = (datetime.now() - self.enrolled_at).days
        progress = self.course.get_progress(self.student)
        
        eligible = days_enrolled <= 7 and progress < 0.2
        refund_amount = self.course.price if eligible else 0.0
        
        return {
            "eligible": eligible,
            "refund_amount": refund_amount,
            "days_enrolled": days_enrolled,
            "progress_percent": progress * 100,
            "reason": "Eligible for full refund" if eligible else 
                      "Past refund window or too much progress"
        }


# =============================================================================
# SECTION 12: FACTORY PATTERN - Course and Content Factories
# =============================================================================

class CourseFactory:
    """Factory for creating different types of courses."""
    
    @staticmethod
    def create_course(course_type: CourseType, title: str, description: str,
                      instructor: Instructor, price: float,
                      difficulty: DifficultyLevel, **kwargs) -> Course:
        """
        Create a course of the specified type.
        
        Args:
            course_type: Type of course to create
            title: Course title
            description: Course description
            instructor: Course instructor
            price: Course price
            difficulty: Difficulty level
            **kwargs: Additional arguments specific to course type
        
        Returns:
            A Course instance of the appropriate type
        """
        if not instructor.is_approved:
            raise InstructorNotApprovedError(instructor.name)
        
        if course_type == CourseType.VIDEO:
            return VideoCourse(
                title=title,
                description=description,
                instructor=instructor,
                price=price,
                difficulty=difficulty,
                total_hours=kwargs.get("total_hours", 10.0)
            )
        
        elif course_type == CourseType.LIVE:
            return LiveCourse(
                title=title,
                description=description,
                instructor=instructor,
                price=price,
                difficulty=difficulty,
                start_date=kwargs.get("start_date", datetime.now()),
                end_date=kwargs.get("end_date", datetime.now() + timedelta(days=30)),
                max_students=kwargs.get("max_students", 30)
            )
        
        elif course_type == CourseType.INTERACTIVE:
            return InteractiveCourse(
                title=title,
                description=description,
                instructor=instructor,
                price=price,
                difficulty=difficulty,
                sandbox_type=kwargs.get("sandbox_type", "python")
            )
        
        elif course_type == CourseType.CERTIFICATION:
            return CertificationCourse(
                title=title,
                description=description,
                instructor=instructor,
                price=price,
                difficulty=difficulty,
                certification_name=kwargs.get("certification_name", "Professional Certificate"),
                validity_years=kwargs.get("validity_years", 2)
            )
        
        else:
            raise ValueError(f"Unknown course type: {course_type}")


class ContentFactory:
    """Factory for creating different types of content."""
    
    @staticmethod
    def create_content(content_type: ContentType, title: str, description: str,
                       order: int, **kwargs) -> Content:
        """
        Create content of the specified type.
        
        Args:
            content_type: Type of content to create
            title: Content title
            description: Content description
            order: Order in the course
            **kwargs: Additional arguments specific to content type
        
        Returns:
            A Content instance of the appropriate type
        """
        if content_type == ContentType.VIDEO:
            return VideoLesson(
                title=title,
                description=description,
                order=order,
                video_url=kwargs.get("video_url", "https://example.com/video"),
                duration_minutes=kwargs.get("duration_minutes", 10)
            )
        
        elif content_type == ContentType.TEXT:
            return TextLesson(
                title=title,
                description=description,
                order=order,
                content_text=kwargs.get("content_text", ""),
                reading_time_minutes=kwargs.get("reading_time_minutes", 5)
            )
        
        elif content_type == ContentType.QUIZ:
            return Quiz(
                title=title,
                description=description,
                order=order,
                questions=kwargs.get("questions", []),
                passing_score=kwargs.get("passing_score", 70.0)
            )
        
        elif content_type == ContentType.ASSIGNMENT:
            return Assignment(
                title=title,
                description=description,
                order=order,
                instructions=kwargs.get("instructions", ""),
                max_points=kwargs.get("max_points", 100),
                due_date=kwargs.get("due_date")
            )
        
        elif content_type == ContentType.PROJECT:
            return Project(
                title=title,
                description=description,
                order=order,
                requirements=kwargs.get("requirements", []),
                peer_review_required=kwargs.get("peer_review_required", True)
            )
        
        else:
            raise ValueError(f"Unknown content type: {content_type}")


# =============================================================================
# SECTION 13: ADAPTER PATTERN - Legacy Course Adapter
# =============================================================================

@dataclass
class LegacyCourseData:
    """Represents course data from a legacy LMS system (e.g., SCORM package)."""
    legacy_id: str
    course_name: str
    author_name: str
    author_email: str
    modules: List[Dict[str, Any]]  # Old format modules
    grading_scale: str  # "letter" or "percentage" or "pass_fail"
    total_points: int
    scorm_version: str = "1.2"


class LegacyCourseAdapter:
    """
    Adapter to convert legacy LMS course data to the new platform format.
    
    Implements the Adapter pattern to make legacy course data compatible
    with the new Course hierarchy.
    """
    
    def __init__(self, legacy_data: LegacyCourseData):
        self._legacy_data = legacy_data
        self._converted_content: List[Content] = []
    
    def adapt(self, registry: LearningPlatformRegistry) -> VideoCourse:
        """
        Convert legacy course data to a VideoCourse.
        
        Args:
            registry: Platform registry for finding/creating instructors
        
        Returns:
            A VideoCourse with converted content
        """
        # Find or create instructor
        instructor = self._find_or_create_instructor(registry)
        
        # Create the course
        course = VideoCourse(
            title=self._convert_title(),
            description=f"Migrated from legacy LMS (ID: {self._legacy_data.legacy_id})",
            instructor=instructor,
            price=self._estimate_price(),
            difficulty=self._detect_difficulty(),
            total_hours=self._calculate_total_hours()
        )
        
        # Convert and add content
        for i, module in enumerate(self._legacy_data.modules):
            content = self._convert_module(module, i + 1)
            course.add_content(content)
        
        return course
    
    def _find_or_create_instructor(self, registry: LearningPlatformRegistry) -> Instructor:
        """Find existing instructor or create a new one."""
        # Try to find existing instructor
        for user in registry.all_users:
            if isinstance(user, Instructor) and user.email == self._legacy_data.author_email:
                return user
        
        # Create new instructor
        instructor = Instructor(
            name=self._legacy_data.author_name,
            email=self._legacy_data.author_email,
            bio="Instructor migrated from legacy LMS"
        )
        instructor.approve()  # Auto-approve for migration
        registry.register_user(instructor)
        return instructor
    
    def _convert_title(self) -> str:
        """Convert legacy title to new format."""
        # Clean up legacy naming conventions
        title = self._legacy_data.course_name
        title = title.replace("_", " ").replace("-", " ")
        return title.title()
    
    def _estimate_price(self) -> float:
        """Estimate price based on content volume."""
        module_count = len(self._legacy_data.modules)
        base_price = 29.99
        return base_price + (module_count * 5.0)
    
    def _detect_difficulty(self) -> DifficultyLevel:
        """Detect difficulty from module names/content."""
        title_lower = self._legacy_data.course_name.lower()
        if "advanced" in title_lower or "expert" in title_lower:
            return DifficultyLevel.ADVANCED
        elif "intermediate" in title_lower:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER
    
    def _calculate_total_hours(self) -> float:
        """Calculate total course hours from modules."""
        total_minutes = 0
        for module in self._legacy_data.modules:
            total_minutes += module.get("duration_minutes", 30)
        return total_minutes / 60
    
    def _convert_module(self, module: Dict[str, Any], order: int) -> Content:
        """Convert a legacy module to new content format."""
        module_type = module.get("type", "text").lower()
        
        if module_type == "video":
            return VideoLesson(
                title=module.get("title", f"Module {order}"),
                description=module.get("description", ""),
                order=order,
                video_url=module.get("url", "https://legacy.example.com/video"),
                duration_minutes=module.get("duration_minutes", 15)
            )
        
        elif module_type == "quiz" or module_type == "assessment":
            # Convert legacy quiz format
            legacy_questions = module.get("questions", [])
            new_questions = self._convert_quiz_questions(legacy_questions)
            return Quiz(
                title=module.get("title", f"Quiz {order}"),
                description=module.get("description", ""),
                order=order,
                questions=new_questions,
                passing_score=self._convert_passing_score(module)
            )
        
        else:
            return TextLesson(
                title=module.get("title", f"Lesson {order}"),
                description=module.get("description", ""),
                order=order,
                content_text=module.get("content", ""),
                reading_time_minutes=module.get("duration_minutes", 10)
            )
    
    def _convert_quiz_questions(self, legacy_questions: List[Dict]) -> List[Dict[str, Any]]:
        """Convert legacy quiz questions to new format."""
        new_questions = []
        for q in legacy_questions:
            new_questions.append({
                "question": q.get("text", q.get("question", "")),
                "options": q.get("choices", q.get("options", [])),
                "correct_answer": q.get("answer", q.get("correct", 0))
            })
        return new_questions
    
    def _convert_passing_score(self, module: Dict[str, Any]) -> float:
        """Convert legacy grading to percentage passing score."""
        if self._legacy_data.grading_scale == "letter":
            # Convert letter grade requirement to percentage
            letter = module.get("passing_grade", "C")
            grade_map = {"A": 90, "B": 80, "C": 70, "D": 60, "F": 0}
            return float(grade_map.get(letter.upper(), 70))
        
        elif self._legacy_data.grading_scale == "pass_fail":
            return 60.0  # Pass = 60%
        
        else:
            return float(module.get("passing_score", 70))


# =============================================================================
# SECTION 14: LEARNING PROGRESS SYSTEM (Observable Implementation)
# =============================================================================

class LearningProgressSystem(Observable):
    """
    System for tracking and reporting learning progress.
    Implements Observable pattern to notify interested parties of progress events.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._registry = LearningPlatformRegistry()
    
    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        for observer in self._observers:
            observer.update(event, data)
    
    def complete_content(self, student: Student, course: Course, content: Content) -> bool:
        """
        Mark content as complete for a student.
        
        Args:
            student: The student completing the content
            course: The course containing the content
            content: The content being completed
        
        Returns:
            True if content was successfully marked complete
        """
        progress = self._registry.get_progress(student.user_id, course.course_id)
        if not progress:
            return False
        
        # Check if previous content is completed (sequential unlock)
        if not self._is_content_unlocked(course, content, progress):
            prev_content = self._get_previous_content(course, content)
            if prev_content:
                raise ContentLockedError(content.title, prev_content.title)
        
        progress.mark_content_complete(content.content_id)
        
        self.notify_observers("lesson_completed", {
            "student_name": student.name,
            "student_id": student.user_id,
            "course_title": course.title,
            "course_id": course.course_id,
            "content_title": content.title,
            "content_id": content.content_id
        })
        
        # Check if course is now complete
        if course.get_progress(student) >= 1.0:
            course.mark_complete(student)
        
        return True
    
    def attempt_quiz(self, student: Student, course: Course, quiz: Quiz,
                     answers: Dict[int, str]) -> Dict[str, Any]:
        """
        Process a quiz attempt.
        
        Args:
            student: The student taking the quiz
            course: The course containing the quiz
            quiz: The quiz being attempted
            answers: Student's answers (question_index -> answer)
        
        Returns:
            Dict with score, passed status, and attempt number
        """
        progress = self._registry.get_progress(student.user_id, course.course_id)
        if not progress:
            raise NotEnrolledError(course.title)
        
        # Check attempt limits
        attempts = progress.get_quiz_attempts(quiz.content_id)
        max_attempts = student.subscription.quiz_attempts_per_quiz
        
        if attempts >= max_attempts:
            raise QuizAttemptLimitError(quiz.title, max_attempts)
        
        # Grade the quiz
        score = quiz.grade_attempt(answers)
        passed = score >= quiz.passing_score
        
        # Record the attempt
        progress.record_quiz_attempt(quiz.content_id, score)
        
        self.notify_observers("quiz_attempted", {
            "student_name": student.name,
            "quiz_title": quiz.title,
            "score": score,
            "passed": passed,
            "attempt": attempts + 1
        })
        
        if passed:
            progress.mark_content_complete(quiz.content_id)
            self.notify_observers("quiz_passed", {
                "student_name": student.name,
                "student_id": student.user_id,
                "quiz_title": quiz.title,
                "score": score
            })
        
        return {
            "score": score,
            "passed": passed,
            "attempt": attempts + 1,
            "max_attempts": max_attempts
        }
    
    def submit_assignment(self, student: Student, course: Course, 
                          assignment: Assignment, submission: str) -> Dict[str, Any]:
        """
        Submit an assignment.
        
        Args:
            student: The student submitting
            course: The course containing the assignment
            assignment: The assignment being submitted
            submission: The submission content
        
        Returns:
            Dict with submission status
        """
        if assignment.is_past_due():
            raise AssignmentPastDueError(assignment.title, assignment.due_date)
        
        progress = self._registry.get_progress(student.user_id, course.course_id)
        if not progress:
            raise NotEnrolledError(course.title)
        
        # For demo, auto-grade with random score (in real system, instructor grades)
        import random
        score = random.randint(60, 100)
        progress.assignment_scores[assignment.content_id] = (score / 100) * assignment.max_points
        
        if score >= 70:
            progress.mark_content_complete(assignment.content_id)
        
        return {
            "submitted": True,
            "score": score,
            "points": progress.assignment_scores[assignment.content_id],
            "max_points": assignment.max_points
        }
    
    def _is_content_unlocked(self, course: Course, content: Content, progress: Progress) -> bool:
        """Check if content is unlocked based on sequential completion."""
        course_content = course.content
        for c in course_content:
            if c.order < content.order and c.is_required:
                if not c.check_completion(progress):
                    return False
        return True
    
    def _get_previous_content(self, course: Course, content: Content) -> Optional[Content]:
        """Get the previous required content in sequence."""
        course_content = sorted(course.content, key=lambda c: c.order)
        for c in reversed(course_content):
            if c.order < content.order and c.is_required:
                return c
        return None


# =============================================================================
# SECTION 15: MAIN DEMONSTRATION
# =============================================================================

def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


def main():
    """
    Main demonstration function showcasing all OOP concepts.
    """
    print("\n" + "=" * 70)
    print("  ONLINE COURSE PLATFORM - OOP DEMONSTRATION")
    print("  Complete Reference Implementation")
    print("=" * 70)
    
    # =========================================================================
    # SINGLETON PATTERN DEMONSTRATION
    # =========================================================================
    print_section("1. SINGLETON PATTERN - Platform Registry")
    
    # Get the singleton registry
    registry1 = LearningPlatformRegistry()
    registry2 = LearningPlatformRegistry()
    
    print(f"  Registry 1 ID: {id(registry1)}")
    print(f"  Registry 2 ID: {id(registry2)}")
    print(f"  Same instance? {registry1 is registry2}")
    
    # =========================================================================
    # USER HIERARCHY DEMONSTRATION
    # =========================================================================
    print_section("2. USER HIERARCHY - Different User Types")
    
    # Create admin
    admin = Admin("Sarah Admin", "sarah@platform.edu")
    registry1.register_user(admin)
    print(f"  Created: {admin}")
    print(f"  Permissions: {', '.join(list(admin.get_permissions())[:5])}...")
    
    # Create instructors
    print_subsection("Creating Instructors")
    instructor1 = Instructor(
        name="Dr. Python Expert",
        email="python@platform.edu",
        bio="20 years of Python development experience"
    )
    instructor2 = Instructor(
        name="Prof. Web Dev",
        email="webdev@platform.edu",
        bio="Full-stack developer and educator"
    )
    
    registry1.register_user(instructor1)
    registry1.register_user(instructor2)
    
    # Demonstrate instructor approval
    print(f"  {instructor1.name} approved? {instructor1.is_approved}")
    admin.approve_instructor(instructor1)
    admin.approve_instructor(instructor2)
    print(f"  {instructor1.name} approved? {instructor1.is_approved}")
    
    # Create teaching assistant
    ta = TeachingAssistant(
        name="Alex Helper",
        email="alex@platform.edu",
        assigned_instructor=instructor1
    )
    registry1.register_user(ta)
    print(f"  Created TA: {ta}")
    
    # Create students with different subscriptions
    print_subsection("Creating Students with Different Subscriptions")
    
    student_free = Student("Free Fred", "fred@student.edu")
    student_free.subscription = FreeTier(student_free)
    
    student_basic = Student("Basic Bob", "bob@student.edu")
    student_basic.subscription = BasicPlan(student_basic)
    
    student_pro = Student("Pro Paula", "paula@student.edu")
    student_pro.subscription = ProPlan(student_pro)
    
    student_enterprise = Student("Enterprise Emma", "emma@company.com")
    student_enterprise.subscription = EnterprisePlan(student_enterprise, team_size=20)
    
    for student in [student_free, student_basic, student_pro, student_enterprise]:
        registry1.register_user(student)
        print(f"  {student.name}: {student.subscription.tier.name} tier "
              f"(${student.subscription.monthly_price:.2f}/mo, "
              f"max {student.subscription.max_concurrent_courses} courses)")
    
    # =========================================================================
    # FACTORY PATTERN DEMONSTRATION
    # =========================================================================
    print_section("3. FACTORY PATTERN - Creating Courses and Content")
    
    # Create courses using factory
    print_subsection("Using CourseFactory")
    
    python_course = CourseFactory.create_course(
        course_type=CourseType.VIDEO,
        title="Python Fundamentals",
        description="Learn Python from scratch",
        instructor=instructor1,
        price=49.99,
        difficulty=DifficultyLevel.BEGINNER,
        total_hours=20.0
    )
    print(f"  Created: {python_course}")
    
    advanced_python = CourseFactory.create_course(
        course_type=CourseType.INTERACTIVE,
        title="Advanced Python Programming",
        description="Master advanced Python concepts",
        instructor=instructor1,
        price=99.99,
        difficulty=DifficultyLevel.ADVANCED,
        sandbox_type="python"
    )
    # Add prerequisite
    advanced_python.add_prerequisite(python_course.course_id)
    print(f"  Created: {advanced_python}")
    print(f"  Prerequisites: Python Fundamentals")
    
    web_course = CourseFactory.create_course(
        course_type=CourseType.LIVE,
        title="Full-Stack Web Development",
        description="Build modern web applications",
        instructor=instructor2,
        price=199.99,
        difficulty=DifficultyLevel.INTERMEDIATE,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=60),
        max_students=25
    )
    print(f"  Created: {web_course}")
    
    cert_course = CourseFactory.create_course(
        course_type=CourseType.CERTIFICATION,
        title="Python Professional Certification",
        description="Get certified in Python",
        instructor=instructor1,
        price=299.99,
        difficulty=DifficultyLevel.ADVANCED,
        certification_name="Python Professional Developer",
        validity_years=3
    )
    print(f"  Created: {cert_course}")
    
    # Create content using factory
    print_subsection("Using ContentFactory")
    
    # Add content to Python course
    content_items = [
        ContentFactory.create_content(
            ContentType.VIDEO,
            "Introduction to Python",
            "Getting started with Python",
            order=1,
            video_url="https://example.com/intro.mp4",
            duration_minutes=15
        ),
        ContentFactory.create_content(
            ContentType.TEXT,
            "Variables and Data Types",
            "Understanding Python data types",
            order=2,
            content_text="Python has several built-in data types...",
            reading_time_minutes=10
        ),
        ContentFactory.create_content(
            ContentType.QUIZ,
            "Data Types Quiz",
            "Test your knowledge of data types",
            order=3,
            questions=[
                {"question": "What type is 'hello'?", "options": ["int", "str", "float"], "correct_answer": "str"},
                {"question": "What type is 42?", "options": ["int", "str", "float"], "correct_answer": "int"},
                {"question": "What type is 3.14?", "options": ["int", "str", "float"], "correct_answer": "float"}
            ],
            passing_score=70.0
        ),
        ContentFactory.create_content(
            ContentType.ASSIGNMENT,
            "Build a Calculator",
            "Create a simple calculator program",
            order=4,
            instructions="Build a calculator that supports +, -, *, /",
            max_points=100,
            due_date=datetime.now() + timedelta(days=7)
        ),
        ContentFactory.create_content(
            ContentType.PROJECT,
            "Final Project: Data Analysis Tool",
            "Build a complete data analysis application",
            order=5,
            requirements=["Load CSV files", "Calculate statistics", "Generate reports"],
            peer_review_required=True
        )
    ]
    
    for content in content_items:
        python_course.add_content(content)
        print(f"  Added: {content}")
    
    # Add minimal content to other courses so they can be published
    print_subsection("Adding Content to Other Courses")
    
    # Advanced Python content
    advanced_python.add_content(ContentFactory.create_content(
        ContentType.VIDEO, "Advanced OOP", "Deep dive into OOP", order=1,
        video_url="https://example.com/adv1.mp4", duration_minutes=30
    ))
    advanced_python.add_content(ContentFactory.create_content(
        ContentType.QUIZ, "Advanced OOP Quiz", "Test advanced concepts", order=2,
        questions=[{"question": "What is metaclass?", "options": ["A", "B", "C"], "correct_answer": "A"}],
        passing_score=70.0
    ))
    print(f"  Added 2 content items to: {advanced_python.title}")
    
    # Web course content
    web_course.add_content(ContentFactory.create_content(
        ContentType.VIDEO, "HTML Basics", "Introduction to HTML", order=1,
        video_url="https://example.com/html.mp4", duration_minutes=25
    ))
    web_course.add_content(ContentFactory.create_content(
        ContentType.ASSIGNMENT, "Build a Website", "Create your first website", order=2,
        instructions="Build a simple portfolio website", max_points=100
    ))
    print(f"  Added 2 content items to: {web_course.title}")
    
    # Certification course content
    cert_course.add_content(ContentFactory.create_content(
        ContentType.TEXT, "Certification Overview", "What to expect", order=1,
        content_text="This certification covers...", reading_time_minutes=10
    ))
    cert_course.add_content(ContentFactory.create_content(
        ContentType.QUIZ, "Certification Exam", "Final certification exam", order=2,
        questions=[
            {"question": "What is Python?", "options": ["Language", "Snake", "Both"], "correct_answer": "Language"},
            {"question": "What is PEP8?", "options": ["Style", "Food", "Tool"], "correct_answer": "Style"}
        ],
        passing_score=80.0
    ))
    print(f"  Added 2 content items to: {cert_course.title}")
    
    # Publish courses
    python_course.publish()
    advanced_python.publish()
    web_course.publish()
    cert_course.publish()
    
    # Register courses
    for course in [python_course, advanced_python, web_course, cert_course]:
        registry1.register_course(course)
    
    # =========================================================================
    # ENROLLMENT AND EXCEPTION HANDLING
    # =========================================================================
    print_section("4. ENROLLMENT WITH EXCEPTION HANDLING")
    
    # Successful enrollment
    print_subsection("Successful Enrollments")
    
    python_course.enroll(student_pro)
    enrollment = registry1.create_enrollment(student_pro, python_course)
    print(f"  ✓ {student_pro.name} enrolled in {python_course.title}")
    
    python_course.enroll(student_basic)
    registry1.create_enrollment(student_basic, python_course)
    print(f"  ✓ {student_basic.name} enrolled in {python_course.title}")
    
    # Demonstrate exception handling
    print_subsection("Exception Handling Demonstrations")
    
    # Try to enroll again (AlreadyEnrolledError)
    try:
        python_course.enroll(student_pro)
    except AlreadyEnrolledError as e:
        print(f"  ✗ AlreadyEnrolledError: {e.message}")
    
    # Try to enroll in advanced course without prerequisite
    try:
        advanced_python.enroll(student_basic)
    except PrerequisiteNotMetError as e:
        print(f"  ✗ PrerequisiteNotMetError: {e.message}")
    
    # Try to create course with unapproved instructor
    try:
        unapproved = Instructor("New Guy", "new@platform.edu")
        registry1.register_user(unapproved)
        CourseFactory.create_course(
            CourseType.VIDEO,
            "Test Course",
            "A test",
            unapproved,
            29.99,
            DifficultyLevel.BEGINNER
        )
    except InstructorNotApprovedError as e:
        print(f"  ✗ InstructorNotApprovedError: {e.message}")
    
    # Try to access non-existent course
    try:
        registry1.get_course("nonexistent")
    except CourseNotFoundError as e:
        print(f"  ✗ CourseNotFoundError: {e.message}")
    
    # =========================================================================
    # SUBSCRIPTION TIER LIMITATIONS
    # =========================================================================
    print_section("5. SUBSCRIPTION TIER LIMITATIONS")
    
    print_subsection("Free Tier Limitations")
    print(f"  {student_free.name}'s subscription:")
    print(f"    - Max concurrent courses: {student_free.subscription.max_concurrent_courses}")
    print(f"    - Quiz attempts: {student_free.subscription.quiz_attempts_per_quiz}")
    print(f"    - Certificates: {student_free.subscription.has_certificates}")
    print(f"    - Downloadable resources: {student_free.subscription.has_downloadable_resources}")
    
    # Enroll free tier student
    python_course.enroll(student_free)
    registry1.create_enrollment(student_free, python_course)
    print(f"  {student_free.name} enrolled in Python Fundamentals")
    
    # Try to enroll in second course (should fail due to limit)
    try:
        web_course.enroll(student_free)
    except Exception as e:
        print(f"  ✗ Cannot enroll in second course: Subscription limit reached")
    
    print_subsection("Pro Tier Benefits")
    print(f"  {student_pro.name}'s subscription:")
    print(f"    - Max concurrent courses: {student_pro.subscription.max_concurrent_courses}")
    print(f"    - Quiz attempts: Unlimited")
    print(f"    - Certificates: {student_pro.subscription.has_certificates}")
    print(f"    - Priority support: {student_pro.subscription.can_access_feature('priority_support')}")
    
    # =========================================================================
    # PROGRESS TRACKING AND OBSERVER PATTERN
    # =========================================================================
    print_section("6. PROGRESS TRACKING WITH OBSERVER PATTERN")
    
    # Create progress system
    progress_system = LearningProgressSystem()
    
    print_subsection("Completing Content (with Notifications)")
    
    # Complete first video
    video_lesson = python_course.content[0]
    progress_system.complete_content(student_pro, python_course, video_lesson)
    
    # Complete text lesson
    text_lesson = python_course.content[1]
    progress_system.complete_content(student_pro, python_course, text_lesson)
    
    # Show progress
    progress = python_course.get_progress(student_pro)
    print(f"\n  Current progress: {progress * 100:.1f}%")
    
    # =========================================================================
    # QUIZ ATTEMPTS AND GRADING
    # =========================================================================
    print_section("7. QUIZ ATTEMPTS AND GRADING")
    
    quiz = python_course.content[2]  # Data Types Quiz
    
    print_subsection(f"Taking Quiz: {quiz.title}")
    
    # First attempt - wrong answers
    result1 = progress_system.attempt_quiz(
        student_pro, python_course, quiz,
        {0: "int", 1: "str", 2: "int"}  # All wrong
    )
    print(f"  Attempt 1: Score = {result1['score']:.1f}%, Passed = {result1['passed']}")
    
    # Second attempt - correct answers
    result2 = progress_system.attempt_quiz(
        student_pro, python_course, quiz,
        {0: "str", 1: "int", 2: "float"}  # All correct
    )
    print(f"  Attempt 2: Score = {result2['score']:.1f}%, Passed = {result2['passed']}")
    
    # Show free tier attempt limits
    print_subsection("Quiz Attempt Limits for Free Tier")
    
    # Complete prerequisites for free user
    free_progress = registry1.get_progress(student_free.user_id, python_course.course_id)
    free_progress.mark_content_complete(video_lesson.content_id)
    free_progress.mark_content_complete(text_lesson.content_id)
    
    for i in range(4):
        try:
            progress_system.attempt_quiz(
                student_free, python_course, quiz,
                {0: "int", 1: "str", 2: "int"}
            )
            print(f"  Free tier attempt {i+1}: Allowed")
        except QuizAttemptLimitError as e:
            print(f"  Free tier attempt {i+1}: ✗ {e.message}")
            break
    
    # =========================================================================
    # ASSIGNMENT SUBMISSION
    # =========================================================================
    print_section("8. ASSIGNMENT SUBMISSION")
    
    assignment = python_course.content[3]
    print_subsection(f"Submitting: {assignment.title}")
    
    result = progress_system.submit_assignment(
        student_pro, python_course, assignment,
        "def calculator(a, op, b): ..."  # Submission content
    )
    print(f"  Submitted: {result['submitted']}")
    print(f"  Score: {result['score']}% ({result['points']:.1f}/{result['max_points']} points)")
    
    # =========================================================================
    # COURSE COMPLETION AND CERTIFICATES
    # =========================================================================
    print_section("9. COURSE COMPLETION AND CERTIFICATES")
    
    # Complete remaining content for student_pro
    pro_progress = registry1.get_progress(student_pro.user_id, python_course.course_id)
    project = python_course.content[4]
    pro_progress.mark_content_complete(project.content_id)
    
    print_subsection("Checking Completion Status")
    final_progress = python_course.get_progress(student_pro)
    final_grade = python_course.calculate_grade(student_pro)
    print(f"  {student_pro.name}'s Progress: {final_progress * 100:.1f}%")
    print(f"  {student_pro.name}'s Grade: {final_grade:.1f}%")
    
    # Mark course complete (triggers certificate generation)
    print_subsection("Marking Course Complete (Observer Notifications)")
    if final_progress >= 1.0:
        python_course.mark_complete(student_pro)
    
    # =========================================================================
    # ADAPTER PATTERN - LEGACY COURSE MIGRATION
    # =========================================================================
    print_section("10. ADAPTER PATTERN - Legacy Course Migration")
    
    print_subsection("Original Legacy Course Data (SCORM format)")
    
    legacy_data = LegacyCourseData(
        legacy_id="SCORM_2019_JAVA_101",
        course_name="introduction_to_java_programming",
        author_name="Legacy Instructor",
        author_email="legacy@oldlms.edu",
        modules=[
            {"type": "video", "title": "Java Basics", "duration_minutes": 20,
             "url": "https://legacy.lms/java1.mp4"},
            {"type": "text", "title": "Variables in Java", "duration_minutes": 15,
             "content": "Java variables are strongly typed..."},
            {"type": "quiz", "title": "Java Basics Quiz", 
             "questions": [
                 {"text": "Is Java object-oriented?", "choices": ["Yes", "No"], "answer": "Yes"}
             ],
             "passing_grade": "C"}
        ],
        grading_scale="letter",
        total_points=100,
        scorm_version="1.2"
    )
    
    print(f"  Legacy ID: {legacy_data.legacy_id}")
    print(f"  Original Name: {legacy_data.course_name}")
    print(f"  SCORM Version: {legacy_data.scorm_version}")
    print(f"  Modules: {len(legacy_data.modules)}")
    
    print_subsection("Adapting to New Format")
    
    adapter = LegacyCourseAdapter(legacy_data)
    migrated_course = adapter.adapt(registry1)
    
    print(f"  Migrated Course: {migrated_course.title}")
    print(f"  Instructor: {migrated_course.instructor.name}")
    print(f"  Price: ${migrated_course.price:.2f}")
    print(f"  Content Items: {len(migrated_course.content)}")
    for content in migrated_course.content:
        print(f"    - {content}")
    
    registry1.register_course(migrated_course)
    
    # =========================================================================
    # REVIEWS AND RATINGS
    # =========================================================================
    print_section("11. REVIEWS AND RATINGS")
    
    print_subsection("Adding Course Reviews")
    
    python_course.add_review(student_pro, 5, "Excellent course! Very comprehensive.")
    python_course.add_review(student_basic, 4, "Good content, learned a lot.")
    
    reviews = python_course.get_reviews()
    avg_rating = python_course.get_average_rating()
    
    print(f"  Total Reviews: {len(reviews)}")
    for review in reviews:
        print(f"    - {review.user_name}: {'★' * review.rating} - \"{review.comment}\"")
    print(f"  Average Rating: {avg_rating:.1f}/5.0")
    
    # =========================================================================
    # INSTRUCTOR REVENUE
    # =========================================================================
    print_section("12. INSTRUCTOR REVENUE CALCULATION")
    
    print_subsection("Revenue Share Model (50%)")
    
    # Calculate instructor earnings
    enrolled_in_python = python_course.enrolled_count
    python_revenue = python_course.price * enrolled_in_python
    instructor_share = python_revenue * 0.5
    
    print(f"  Course: {python_course.title}")
    print(f"  Price: ${python_course.price:.2f}")
    print(f"  Enrollments: {enrolled_in_python}")
    print(f"  Total Revenue: ${python_revenue:.2f}")
    print(f"  Instructor Share (50%): ${instructor_share:.2f}")
    print(f"  {instructor1.name}'s Total Earnings: ${instructor1.total_revenue:.2f}")
    
    # =========================================================================
    # REFUND ELIGIBILITY
    # =========================================================================
    print_section("13. REFUND POLICY CHECK")
    
    print_subsection("Checking Refund Eligibility")
    
    refund_info = enrollment.calculate_refund_eligibility()
    print(f"  Student: {student_pro.name}")
    print(f"  Course: {python_course.title}")
    print(f"  Days Enrolled: {refund_info['days_enrolled']}")
    print(f"  Progress: {refund_info['progress_percent']:.1f}%")
    print(f"  Eligible for Refund: {refund_info['eligible']}")
    print(f"  Reason: {refund_info['reason']}")
    
    # =========================================================================
    # CONTENT LOCKING DEMONSTRATION
    # =========================================================================
    print_section("14. SEQUENTIAL CONTENT UNLOCKING")
    
    print_subsection("Attempting to Skip Content")
    
    # Create a new student who hasn't completed anything
    new_student = Student("New Student", "new@student.edu")
    new_student.subscription = ProPlan(new_student)
    registry1.register_user(new_student)
    python_course.enroll(new_student)
    registry1.create_enrollment(new_student, python_course)
    
    # Try to jump to quiz without completing video and text
    try:
        quiz = python_course.content[2]
        progress_system.complete_content(new_student, python_course, quiz)
    except ContentLockedError as e:
        print(f"  ✗ {e.message}")
    
    # Complete in order
    print_subsection("Completing Content in Order")
    for i, content in enumerate(python_course.content[:3]):
        try:
            if isinstance(content, Quiz):
                progress_system.attempt_quiz(
                    new_student, python_course, content,
                    {0: "str", 1: "int", 2: "float"}
                )
            else:
                progress_system.complete_content(new_student, python_course, content)
            print(f"  ✓ Completed: {content.title}")
        except ContentLockedError as e:
            print(f"  ✗ Locked: {content.title}")
    
    # =========================================================================
    # ANALYTICS SUMMARY
    # =========================================================================
    print_section("15. ANALYTICS DASHBOARD SUMMARY")
    
    analytics = registry1.get_analytics_summary()
    print(f"  Total Enrollments: {analytics['metrics']['total_enrollments']}")
    print(f"  Total Completions: {analytics['metrics']['total_completions']}")
    print(f"  Total Quiz Attempts: {analytics['metrics']['total_quiz_attempts']}")
    print(f"  Total Certificates Issued: {analytics['metrics']['total_certificates']}")
    print(f"  Total Events Recorded: {analytics['total_events']}")
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print_section("16. PLATFORM SUMMARY")
    
    print(f"\n  Total Users: {len(registry1.all_users)}")
    print(f"  Total Courses: {len(registry1.all_courses)}")
    
    print("\n  Users by Role:")
    role_counts = {}
    for user in registry1.all_users:
        role = user.role.name
        role_counts[role] = role_counts.get(role, 0) + 1
    for role, count in role_counts.items():
        print(f"    - {role}: {count}")
    
    print("\n  Courses by Type:")
    type_counts = {}
    for course in registry1.all_courses:
        ctype = course.course_type.name
        type_counts[ctype] = type_counts.get(ctype, 0) + 1
    for ctype, count in type_counts.items():
        print(f"    - {ctype}: {count}")
    
    print("\n" + "=" * 70)
    print("  OOP CONCEPTS DEMONSTRATED:")
    print("=" * 70)
    print("""
  ✓ Class Hierarchies (Course, User, Content, Subscription)
  ✓ Abstract Base Classes (ABC) for interfaces
  ✓ Encapsulation (private attributes, properties, validation)
  ✓ Custom Exception Hierarchy (14 exception classes)
  ✓ Factory Pattern (CourseFactory, ContentFactory)
  ✓ Adapter Pattern (LegacyCourseAdapter)
  ✓ Observer Pattern (StudentNotifier, InstructorNotifier, etc.)
  ✓ Singleton Pattern (LearningPlatformRegistry with metaclass)
  ✓ Enums for type safety (7 enum classes)
  ✓ Business rules (prerequisites, sequential unlock, refunds, etc.)
  ✓ Composition and aggregation
  ✓ Multiple inheritance through interfaces
  ✓ Polymorphism (different course/content types)
""")
    print("=" * 70)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
