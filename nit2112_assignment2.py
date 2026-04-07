"""Inheritance-based scaffold for club membership roles.

The design uses a single ``Member`` base class with specialised subclasses for
standard and executive roles. This makes the role hierarchy explicit and keeps
shared member behaviour in one place.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Optional


@dataclass
class Member:
	"""Base class for all club members."""

	member_id: str
	full_name: str
	email: str
	role_name: ClassVar[str] = "Member"
	permissions: ClassVar[frozenset[str]] = frozenset()

	def can(self, permission: str) -> bool:
		"""Return True when this member has the given permission."""

		return permission in self.permissions

	def role_names(self) -> list[str]:
		"""Return the role label for this member."""

		return [self.role_name]

	def can_approve_events(self) -> bool:
		return self.can("approve_events")

	def can_manage_budget(self) -> bool:
		return self.can("manage_budget")

	def can_record_minutes(self) -> bool:
		return self.can("record_minutes")

	def is_executive(self) -> bool:
		"""Return True when the member has executive permissions."""

		return bool(self.permissions)

	def describe(self) -> str:
		"""Return a human-readable description of the member."""

		return f"{self.full_name} ({self.role_name})"


@dataclass
class StandardMember(Member):
	"""Default member type for a student club participant."""

	role_name: ClassVar[str] = "Standard Member"
	permissions: ClassVar[frozenset[str]] = frozenset()


@dataclass
class ExecutiveMember(Member):
	"""Base class for executive member types."""

	role_name: ClassVar[str] = "Executive Member"
	permissions: ClassVar[frozenset[str]] = frozenset()


@dataclass
class President(ExecutiveMember):
	"""Member responsible for approvals and club leadership."""

	role_name: ClassVar[str] = "President"
	permissions: ClassVar[frozenset[str]] = frozenset(
		{"approve_events", "manage_members", "represent_club"}
	)


@dataclass
class Treasurer(ExecutiveMember):
	"""Member responsible for budgeting and spending approvals."""

	role_name: ClassVar[str] = "Treasurer"
	permissions: ClassVar[frozenset[str]] = frozenset({"manage_budget", "approve_spending"})


@dataclass
class Secretary(ExecutiveMember):
	"""Member responsible for records, agendas, and notices."""

	role_name: ClassVar[str] = "Secretary"
	permissions: ClassVar[frozenset[str]] = frozenset(
		{"record_minutes", "manage_agenda", "send_notices"}
	)


class EventStatus(Enum):
	"""Lifecycle states for a club event."""

	DRAFT = "draft"
	PROPOSED = "proposed"
	APPROVED = "approved"
	SCHEDULED = "scheduled"
	IN_PROGRESS = "in_progress"
	COMPLETED = "completed"
	CANCELLED = "cancelled"


@dataclass
class Event:
	"""A club event that moves through a clear lifecycle."""

	event_id: str
	title: str
	description: str
	organiser: Member
	status: EventStatus = EventStatus.DRAFT
	approved_by: Optional[Member] = None
	scheduled_date: Optional[str] = None
	venue: Optional[str] = None

	def propose(self) -> None:
		"""Move the event from draft to proposed."""

		if self.status is not EventStatus.DRAFT:
			raise ValueError("Only draft events can be proposed.")
		self.status = EventStatus.PROPOSED

	def approve(self, approver: Member) -> None:
		"""Approve the event using an executive member with approval permission."""

		if self.status not in {EventStatus.PROPOSED, EventStatus.DRAFT}:
			raise ValueError("Only draft or proposed events can be approved.")
		if not approver.can_approve_events():
			raise PermissionError("This member cannot approve events.")
		self.status = EventStatus.APPROVED
		self.approved_by = approver

	def schedule(self, scheduled_date: str, venue: str) -> None:
		"""Schedule the event after approval."""

		if self.status is not EventStatus.APPROVED:
			raise ValueError("Only approved events can be scheduled.")
		self.status = EventStatus.SCHEDULED
		self.scheduled_date = scheduled_date
		self.venue = venue

	def start(self) -> None:
		"""Mark the event as in progress."""

		if self.status is not EventStatus.SCHEDULED:
			raise ValueError("Only scheduled events can be started.")
		self.status = EventStatus.IN_PROGRESS

	def complete(self) -> None:
		"""Mark the event as completed."""

		if self.status is not EventStatus.IN_PROGRESS:
			raise ValueError("Only in-progress events can be completed.")
		self.status = EventStatus.COMPLETED

	def cancel(self) -> None:
		"""Cancel the event at any point before completion."""

		if self.status is EventStatus.COMPLETED:
			raise ValueError("Completed events cannot be cancelled.")
		self.status = EventStatus.CANCELLED


@dataclass
class Club:
	"""Container for club members and their assigned roles."""

	name: str
	members: list[Member] = field(default_factory=list)
	events: list[Event] = field(default_factory=list)

	def add_member(self, member: Member) -> None:
		"""Add a member when they are not already in the club."""

		if self.find_member(member.member_id) is None:
			self.members.append(member)

	def remove_member(self, member_id: str) -> None:
		"""Remove a member from the club by their identifier."""

		self.members = [member for member in self.members if member.member_id != member_id]

	def find_member(self, member_id: str) -> Optional[Member]:
		"""Find a member by identifier, or return None when not found."""

		for member in self.members:
			if member.member_id == member_id:
				return member
		return None

	def assign_role(self, member_id: str, role: Member) -> None:
		"""Replace a member with a specialised role-based subclass."""

		for index, member in enumerate(self.members):
			if member.member_id == member_id:
				self.members[index] = role
				return
		raise ValueError(f"Member '{member_id}' does not exist in {self.name}.")

	def members_with_permission(self, permission: str) -> list[Member]:
		"""Return all members who can perform a given action."""

		return [member for member in self.members if member.can(permission)]

	def executive_members(self) -> list[Member]:
		"""Return members who hold at least one executive role."""

		executive_role_types: tuple[type[Member], ...] = (
			ExecutiveMember,
			President,
			Treasurer,
			Secretary,
		)
		return [
			member
			for member in self.members
			if isinstance(member, executive_role_types) and member.is_executive()
		]

	def add_event(self, event: Event) -> None:
		"""Add an event to the club if it has not already been recorded."""

		if self.find_event(event.event_id) is None:
			self.events.append(event)

	def find_event(self, event_id: str) -> Optional[Event]:
		"""Find an event by identifier, or return None when not found."""

		for event in self.events:
			if event.event_id == event_id:
				return event
		return None

	def propose_event(
		self,
		event_id: str,
		title: str,
		description: str,
		organiser_id: str,
	) -> Event:
		"""Create and propose a new event owned by a club member."""

		organiser = self.find_member(organiser_id)
		if organiser is None:
			raise ValueError(f"Member '{organiser_id}' does not exist in {self.name}.")

		event = Event(
			event_id=event_id,
			title=title,
			description=description,
			organiser=organiser,
		)
		event.propose()
		self.add_event(event)
		return event

	def approve_event(self, event_id: str, approver_id: str) -> None:
		"""Approve an event using an executive member."""

		event = self.find_event(event_id)
		approver = self.find_member(approver_id)
		if event is None:
			raise ValueError(f"Event '{event_id}' does not exist in {self.name}.")
		if approver is None:
			raise ValueError(f"Member '{approver_id}' does not exist in {self.name}.")
		event.approve(approver)

	def schedule_event(self, event_id: str, scheduled_date: str, venue: str) -> None:
		"""Schedule an approved event."""

		event = self.find_event(event_id)
		if event is None:
			raise ValueError(f"Event '{event_id}' does not exist in {self.name}.")
		event.schedule(scheduled_date, venue)

	def start_event(self, event_id: str) -> None:
		"""Start a scheduled event."""

		event = self.find_event(event_id)
		if event is None:
			raise ValueError(f"Event '{event_id}' does not exist in {self.name}.")
		event.start()

	def complete_event(self, event_id: str) -> None:
		"""Complete an in-progress event."""

		event = self.find_event(event_id)
		if event is None:
			raise ValueError(f"Event '{event_id}' does not exist in {self.name}.")
		event.complete()

	def cancel_event(self, event_id: str) -> None:
		"""Cancel an event before it is completed."""

		event = self.find_event(event_id)
		if event is None:
			raise ValueError(f"Event '{event_id}' does not exist in {self.name}.")
		event.cancel()

	def events_by_status(self, status: EventStatus) -> list[Event]:
		"""Return all events currently in the given lifecycle state."""

		return [event for event in self.events if event.status is status]


def create_standard_member(member_id: str, full_name: str, email: str) -> Member:
	"""Factory helper for a standard student member."""

	return StandardMember(member_id=member_id, full_name=full_name, email=email)


def create_president(member_id: str, full_name: str, email: str) -> Member:
	"""Factory helper for a president member."""

	return President(member_id=member_id, full_name=full_name, email=email)


def create_treasurer(member_id: str, full_name: str, email: str) -> Member:
	"""Factory helper for a treasurer member."""

	return Treasurer(member_id=member_id, full_name=full_name, email=email)


def create_secretary(member_id: str, full_name: str, email: str) -> Member:
	"""Factory helper for a secretary member."""

	return Secretary(member_id=member_id, full_name=full_name, email=email)


def create_executive_member(
	member_id: str,
	full_name: str,
	email: str,
	role_type: type[ExecutiveMember] = ExecutiveMember,
) -> Member:
	"""Factory helper for a member with an executive subclass."""

	return role_type(member_id=member_id, full_name=full_name, email=email)


if __name__ == "__main__":
	club = Club(name="Robotics Club")

	alice = create_standard_member("S001", "Alice Chen", "alice@example.com")
	ben = create_president("S002", "Ben Patel", "ben@example.com")
	chloe = create_treasurer("S003", "Chloe Singh", "chloe@example.com")
	dan = create_secretary("S004", "Dan Lopez", "dan@example.com")

	club.add_member(alice)
	club.add_member(ben)
	club.add_member(chloe)
	club.add_member(dan)

	workshop = club.propose_event(
		"E001",
		"Intro to Robotics",
		"A beginner workshop covering basic robotics concepts.",
		organiser_id="S001",
	)
	club.approve_event("E001", "S002")
	club.schedule_event("E001", "2026-04-15", "Lab 3")

	print(f"Club: {club.name}")
	for member in club.members:
		print(f"- {member.describe()}")

	print(f"Executive members: {[member.full_name for member in club.executive_members()]}")
	print(f"Can Ben manage budget? {ben.can_manage_budget()}")
	print(f"Event status: {workshop.title} -> {workshop.status.value}")
