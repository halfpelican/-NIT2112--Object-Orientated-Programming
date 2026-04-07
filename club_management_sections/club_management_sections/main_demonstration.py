"""Executable entry point that runs the club management demonstration."""

from pathlib import Path
import sys

# Allow importing the original monolithic script from the parent folder.
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from club import Club
from constants import EventStatus, Permission, ClubType
from event_states import EventState
from events import Event, Workshop, SocialGathering, Fundraiser, Competition
from exceptions import (
    ClubManagementError, MemberNotFoundError, PermissionDeniedError,
    InsufficientFundsError, InvalidEventStateError, UnauthorizedApproverError
)
from factory import ClubFactory
from financial import Budget
from observer_pattern import Observer, Observable
from members import (
    Member, StandardMember, ExecutiveCommitteeMember,
    President, Treasurer, Secretary, EventCoordinator
)
from observer_implementations import AttendanceTracker, EngagementAnalytics, NotificationService
from registry import ClubRegistry
from resources import Resource, Venue, Equipment, ResourceManager


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

def main():
    """Demonstrate the Club Management System functionality."""
    
    print("=" * 70)
    print("   UNICLUB STUDENT CLUB MANAGEMENT SYSTEM - DEMONSTRATION")
    print("=" * 70)
    
    # =========================================================================
    # 1. SINGLETON PATTERN - Club Registry
    # =========================================================================
    print("\n" + "=" * 60)
    print("1. SINGLETON PATTERN - Club Registry")
    print("=" * 60)
    
    registry1 = ClubRegistry()
    registry2 = ClubRegistry()
    
    print(f"Registry 1 ID: {id(registry1)}")
    print(f"Registry 2 ID: {id(registry2)}")
    print(f"Same instance: {registry1 is registry2}")
    
    # Add global observers
    attendance_tracker = AttendanceTracker()
    analytics = EngagementAnalytics()
    notifications = NotificationService()
    
    registry1.add_global_observer(attendance_tracker)
    registry1.add_global_observer(analytics)
    registry1.add_global_observer(notifications)
    
    # =========================================================================
    # 2. FACTORY PATTERN - Club Creation
    # =========================================================================
    print("\n" + "=" * 60)
    print("2. FACTORY PATTERN - Club Creation")
    print("=" * 60)
    
    ai_club = ClubFactory.create_club("academic", "AI Research Society", 5000.0)
    sports_club = ClubFactory.create_club("sports", "Tennis Club", 4000.0, equipment_budget=1500.0)
    
    registry1.register_club(ai_club)
    registry1.register_club(sports_club)
    
    print(f"Created: {ai_club}")
    print(f"Created: {sports_club}")
    print(f"Sports Club Budget: ${sports_club.budget.balance:.2f}")
    
    # =========================================================================
    # 3. MEMBER HIERARCHY - Polymorphism
    # =========================================================================
    print("\n" + "=" * 60)
    print("3. MEMBER HIERARCHY - Inheritance & Polymorphism")
    print("=" * 60)
    
    # Create members for AI Club
    president = President("P001", "Alice Chen", "alice@uni.edu")
    treasurer = Treasurer("T001", "Bob Smith", "bob@uni.edu")
    secretary = Secretary("S001", "Carol White", "carol@uni.edu")
    coordinator = EventCoordinator("E001", "David Lee", "david@uni.edu")
    member1 = StandardMember("M001", "Eve Johnson", "eve@uni.edu")
    member2 = StandardMember("M002", "Frank Brown", "frank@uni.edu")
    
    # Add to club
    for member in [president, treasurer, secretary, coordinator, member1, member2]:
        ai_club.add_member(member)
    
    print("\nMembers Added (with Observer notifications):")
    print(f"\nExecutives: {len(ai_club.get_executives())}")
    
    # Demonstrate polymorphism
    print("\nRole Permissions (Polymorphism):")
    print("-" * 50)
    for member in [president, treasurer, member1]:
        perms = list(member.get_permissions())
        print(f"  {member.role}: {', '.join(perms[:4])}...")
    
    # =========================================================================
    # 4. EVENT HIERARCHY & STATE PATTERN
    # =========================================================================
    print("\n" + "=" * 60)
    print("4. EVENT HIERARCHY & STATE PATTERN - Approval Workflow")
    print("=" * 60)
    
    # Create a workshop event
    workshop = Workshop(
        event_id="EVT001",
        title="Introduction to Machine Learning",
        description="Hands-on ML workshop for beginners",
        proposed_by="M001",
        estimated_cost=200.0,
        topic="Machine Learning",
        instructor="Dr. Smith",
        max_participants=25
    )
    
    print(f"\n--- Proposing Event ---")
    ai_club.propose_event(workshop, "M001")
    print(f"Event Status: {workshop.status}")
    
    print(f"\n--- Submitting for Approval ---")
    workshop.submit_for_approval()
    print(f"Event Status: {workshop.status}")
    print(f"Required Approver: {workshop._state.get_required_approver_role()}")
    
    print(f"\n--- Budget Review (Treasurer) ---")
    ai_club.process_event_approval("EVT001", "T001", approve=True)
    print(f"Event Status: {workshop.status}")
    print(f"Required Approver: {workshop._state.get_required_approver_role()}")
    
    print(f"\n--- Resource Check (Coordinator) ---")
    ai_club.process_event_approval("EVT001", "E001", approve=True)
    print(f"Event Status: {workshop.status}")
    print(f"Required Approver: {workshop._state.get_required_approver_role()}")
    
    print(f"\n--- Final Approval (President) ---")
    ai_club.process_event_approval("EVT001", "P001", approve=True)
    print(f"Event Status: {workshop.status}")
    
    # =========================================================================
    # 5. FINANCIAL MANAGEMENT
    # =========================================================================
    print("\n" + "=" * 60)
    print("5. FINANCIAL MANAGEMENT - Budget Tracking")
    print("=" * 60)
    
    print(f"\nBudget before event completion:")
    print(f"  Balance: ${ai_club.budget.balance:.2f}")
    print(f"  Reserved: ${ai_club.budget.total_reserved:.2f}")
    print(f"  Available: ${ai_club.budget.available_balance:.2f}")
    
    # Schedule and complete the event
    workshop.record_attendance("M001", "organizer")
    workshop.record_attendance("M002", "attendee")
    
    ai_club.complete_event("EVT001", actual_cost=180.0)
    
    print(f"\nBudget after event completion:")
    print(f"  Balance: ${ai_club.budget.balance:.2f}")
    
    # =========================================================================
    # 6. CUSTOM EXCEPTIONS
    # =========================================================================
    print("\n" + "=" * 60)
    print("6. CUSTOM EXCEPTION HANDLING")
    print("=" * 60)
    
    print("\n--- Insufficient Funds ---")
    expensive_event = SocialGathering(
        event_id="EVT002",
        title="Grand Gala",
        description="Annual celebration",
        proposed_by="M001",
        estimated_cost=10000.0,
        theme="Masquerade",
        expected_attendance=200
    )
    ai_club.propose_event(expensive_event, "M001")
    expensive_event.submit_for_approval()
    
    try:
        ai_club.process_event_approval("EVT002", "T001", approve=True)
    except InsufficientFundsError as e:
        print(f"  Caught: {e.message}")
    
    print("\n--- Permission Denied ---")
    try:
        # Standard member tries to approve
        workshop2 = Workshop(
            event_id="EVT003",
            title="Python Workshop",
            description="Learn Python",
            proposed_by="M002",
            estimated_cost=50.0,
            topic="Python",
            instructor="John",
            max_participants=20
        )
        ai_club.propose_event(workshop2, "M002")
        workshop2.submit_for_approval()
        workshop2.approve(member1)  # Standard member trying to approve
    except (PermissionDeniedError, AttributeError) as e:
        print(f"  Caught: StandardMember cannot approve events")
    
    print("\n--- Invalid State Transition ---")
    try:
        # Try to approve already completed event
        workshop.approve(president)
    except InvalidEventStateError as e:
        print(f"  Caught: {e.message}")
    
    print("\n--- Unauthorized Approver ---")
    try:
        # Secretary tries to approve budget
        workshop3 = Workshop(
            event_id="EVT004",
            title="Writing Workshop",
            description="Learn writing",
            proposed_by="M001",
            estimated_cost=75.0,
            topic="Writing",
            instructor="Jane",
            max_participants=15
        )
        ai_club.propose_event(workshop3, "M001")
        workshop3.submit_for_approval()
        workshop3.approve(secretary)  # Secretary trying to approve budget
    except UnauthorizedApproverError as e:
        print(f"  Caught: {e.message}")
    
    # =========================================================================
    # 7. OBSERVER PATTERN - Attendance & Notifications
    # =========================================================================
    print("\n" + "=" * 60)
    print("7. OBSERVER PATTERN - Attendance Tracking")
    print("=" * 60)
    
    # Create and complete another event
    competition = Competition(
        event_id="EVT005",
        title="Coding Competition",
        description="Annual coding challenge",
        proposed_by="E001",
        estimated_cost=100.0,
        competition_type="Hackathon",
        prize_pool=500.0,
        registration_fee=10.0
    )
    
    ai_club.propose_event(competition, "E001")
    competition.submit_for_approval()
    ai_club.process_event_approval("EVT005", "T001", approve=True)
    ai_club.process_event_approval("EVT005", "E001", approve=True)
    ai_club.process_event_approval("EVT005", "P001", approve=True)
    
    # Record attendance (observers will be notified)
    print("\n--- Recording Attendance ---")
    competition.register_participant("M001")
    competition.register_participant("M002")
    
    ai_club.complete_event("EVT005")
    
    # =========================================================================
    # 8. REGISTRY STATISTICS
    # =========================================================================
    print("\n" + "=" * 60)
    print("8. REGISTRY STATISTICS")
    print("=" * 60)
    
    stats = registry1.get_statistics()
    print(f"\nClub Registry Summary:")
    print(f"  Total Clubs: {stats['total_clubs']}")
    print(f"  Total Members: {stats['total_members']}")
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Total Budget: ${stats['total_budget']:.2f}")
    
    # =========================================================================
    # 9. CLUB REPORT
    # =========================================================================
    print("\n" + "=" * 60)
    print("9. CLUB REPORT")
    print("=" * 60)
    
    print(ai_club.get_club_report())
    
    # =========================================================================
    # 10. FINANCIAL REPORT
    # =========================================================================
    print("\n" + "=" * 60)
    print("10. FINANCIAL REPORT")
    print("=" * 60)
    
    print(ai_club.budget.get_financial_report())
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("   OOP CONCEPTS DEMONSTRATED")
    print("=" * 60)
    print("""
    [OK] Encapsulation
      - Private attributes (_member_id, _balance)
      - Properties with validation
      - Protected data access
    
    [OK] Inheritance
    - Member hierarchy (StandardMember, ExecutiveMember -> President, Treasurer)
      - Event hierarchy (Workshop, SocialGathering, Fundraiser, Competition)
      - Resource hierarchy (Venue, Equipment)
    
    [OK] Polymorphism
      - get_permissions() varies by member type
      - calculate_total_cost() varies by event type
      - process_approval() varies by state
    
    [OK] Abstraction
      - Approvable interface (submit_for_approval, approve, reject)
      - Trackable interface (record_attendance, get_attendance_list)
      - Observable interface (add_observer, notify_observers)
    
    [OK] State Pattern
      - EventState classes manage approval workflow
    - Transitions: PROPOSED -> BUDGET_REVIEW -> RESOURCE_CHECK -> APPROVED
    
    [OK] Factory Pattern
      - ClubFactory.create_club() with type-specific configuration
    
    [OK] Observer Pattern
      - AttendanceTracker, EngagementAnalytics, NotificationService
    
    [OK] Singleton Pattern
      - ClubRegistry using SingletonMeta metaclass
    
    [OK] Custom Exceptions
      - Full hierarchy from ClubManagementError
      - Specific exceptions with context data
    """)
    
    print("=" * 60)
    print("   DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

