#!/usr/bin/env python3
"""
Healthcare Clinic Management System - Complete OOP Reference Implementation

This module demonstrates all major Object-Oriented Programming concepts including:
- Abstract Base Classes (ABC) and class hierarchies
- Interfaces and multiple inheritance
- Encapsulation with properties and access control
- Custom exception hierarchies
- Design Patterns: Factory, Adapter, Observer, Singleton
- Enums for type safety
- Business rule implementation

Author: OOP Teaching Reference
Version: 1.0
"""

from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from enum import Enum, auto
from typing import List, Dict, Optional, Any, Callable, Set
from dataclasses import dataclass, field
import uuid
import re


# =============================================================================
# SECTION 1: ENUMERATIONS
# =============================================================================

class PatientType(Enum):
    """Types of patients in the clinic system."""
    OUTPATIENT = auto()
    INPATIENT = auto()
    EMERGENCY = auto()


class AppointmentStatus(Enum):
    """Status states for appointments."""
    SCHEDULED = auto()
    CONFIRMED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELLED = auto()
    NO_SHOW = auto()


class Specialization(Enum):
    """Medical specializations available at the clinic."""
    GENERAL = "General Practice"
    CARDIOLOGY = "Cardiology"
    DERMATOLOGY = "Dermatology"
    ORTHOPEDICS = "Orthopedics"
    PEDIATRICS = "Pediatrics"
    NEUROLOGY = "Neurology"


class InsuranceType(Enum):
    """Types of insurance coverage."""
    NONE = ("No Insurance", 0.0)
    BASIC = ("Basic Plan", 0.5)
    STANDARD = ("Standard Plan", 0.7)
    PREMIUM = ("Premium Plan", 0.9)
    GOVERNMENT = ("Government Coverage", 0.85)

    def __init__(self, description: str, coverage_rate: float):
        self.description = description
        self.coverage_rate = coverage_rate


class Priority(Enum):
    """Priority levels for patient care."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    EMERGENCY = 5


class RoomType(Enum):
    """Types of rooms for inpatients."""
    GENERAL_WARD = ("General Ward", 100.0)
    SEMI_PRIVATE = ("Semi-Private Room", 250.0)
    PRIVATE = ("Private Room", 500.0)
    ICU = ("Intensive Care Unit", 1500.0)

    def __init__(self, description: str, daily_rate: float):
        self.description = description
        self.daily_rate = daily_rate


# =============================================================================
# SECTION 2: CUSTOM EXCEPTIONS HIERARCHY
# =============================================================================

class ClinicException(Exception):
    """Base exception for all clinic-related errors."""
    
    def __init__(self, message: str, error_code: str = "CLINIC_ERROR"):
        self.message = message
        self.error_code = error_code
        self.timestamp = datetime.now()
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.error_code}] {self.message} (at {self.timestamp})"


class PatientException(ClinicException):
    """Base exception for patient-related errors."""
    
    def __init__(self, message: str, patient_id: str = None):
        self.patient_id = patient_id
        super().__init__(message, "PATIENT_ERROR")


class PatientNotFoundError(PatientException):
    """Raised when a patient cannot be found in the system."""
    
    def __init__(self, patient_id: str):
        super().__init__(f"Patient with ID '{patient_id}' not found", patient_id)
        self.error_code = "PATIENT_NOT_FOUND"


class DuplicatePatientError(PatientException):
    """Raised when attempting to register a patient that already exists."""
    
    def __init__(self, patient_id: str):
        super().__init__(f"Patient with ID '{patient_id}' already exists", patient_id)
        self.error_code = "DUPLICATE_PATIENT"


class AppointmentException(ClinicException):
    """Base exception for appointment-related errors."""
    
    def __init__(self, message: str, appointment_id: str = None):
        self.appointment_id = appointment_id
        super().__init__(message, "APPOINTMENT_ERROR")


class SlotNotAvailableError(AppointmentException):
    """Raised when a requested time slot is not available."""
    
    def __init__(self, slot_time: datetime, doctor_name: str = None):
        self.slot_time = slot_time
        self.doctor_name = doctor_name
        message = f"Time slot {slot_time} is not available"
        if doctor_name:
            message += f" for Dr. {doctor_name}"
        super().__init__(message)
        self.error_code = "SLOT_NOT_AVAILABLE"


class AppointmentConflictError(AppointmentException):
    """Raised when an appointment conflicts with an existing one."""
    
    def __init__(self, existing_appointment_id: str, new_slot: datetime):
        self.existing_appointment_id = existing_appointment_id
        self.new_slot = new_slot
        super().__init__(
            f"Appointment conflicts with existing appointment {existing_appointment_id}"
        )
        self.error_code = "APPOINTMENT_CONFLICT"


class DoctorNotAvailableError(AppointmentException):
    """Raised when a doctor is not available for appointment."""
    
    def __init__(self, doctor_id: str, reason: str = "unavailable"):
        self.doctor_id = doctor_id
        self.reason = reason
        super().__init__(f"Doctor {doctor_id} is {reason}")
        self.error_code = "DOCTOR_NOT_AVAILABLE"


class BillingException(ClinicException):
    """Base exception for billing-related errors."""
    
    def __init__(self, message: str, amount: float = None):
        self.amount = amount
        super().__init__(message, "BILLING_ERROR")


class InsuranceNotValidError(BillingException):
    """Raised when insurance information is invalid or expired."""
    
    def __init__(self, insurance_id: str, reason: str = "invalid"):
        self.insurance_id = insurance_id
        self.reason = reason
        super().__init__(f"Insurance '{insurance_id}' is {reason}")
        self.error_code = "INSURANCE_INVALID"


class PaymentFailedError(BillingException):
    """Raised when a payment transaction fails."""
    
    def __init__(self, amount: float, reason: str = "declined"):
        super().__init__(f"Payment of ${amount:.2f} failed: {reason}", amount)
        self.error_code = "PAYMENT_FAILED"


class MedicalRecordException(ClinicException):
    """Base exception for medical record-related errors."""
    
    def __init__(self, message: str, record_id: str = None):
        self.record_id = record_id
        super().__init__(message, "RECORD_ERROR")


class UnauthorizedAccessError(MedicalRecordException):
    """Raised when unauthorized access to medical records is attempted."""
    
    def __init__(self, accessor_id: str, record_id: str):
        self.accessor_id = accessor_id
        super().__init__(
            f"User '{accessor_id}' is not authorized to access record '{record_id}'",
            record_id
        )
        self.error_code = "UNAUTHORIZED_ACCESS"


class ReferralRequiredError(AppointmentException):
    """Raised when a specialist appointment requires a referral."""
    
    def __init__(self, specialization: Specialization):
        self.specialization = specialization
        super().__init__(
            f"Referral from general practitioner required for {specialization.value}"
        )
        self.error_code = "REFERRAL_REQUIRED"


class MedicationInteractionError(MedicalRecordException):
    """Raised when medication interactions are detected."""
    
    def __init__(self, medication1: str, medication2: str):
        self.medication1 = medication1
        self.medication2 = medication2
        super().__init__(
            f"Dangerous interaction detected between {medication1} and {medication2}"
        )
        self.error_code = "MEDICATION_INTERACTION"


# =============================================================================
# SECTION 3: INTERFACES (Abstract Base Classes)
# =============================================================================

class Billable(ABC):
    """Interface for entities that can be billed."""
    
    @abstractmethod
    def calculate_bill(self) -> float:
        """Calculate the total bill amount."""
        pass
    
    @abstractmethod
    def apply_insurance(self, insurance_type: InsuranceType) -> float:
        """Apply insurance coverage and return the amount to be paid."""
        pass
    
    @abstractmethod
    def get_bill_breakdown(self) -> Dict[str, float]:
        """Get a detailed breakdown of all charges."""
        pass


class Schedulable(ABC):
    """Interface for entities that can be scheduled."""
    
    @abstractmethod
    def get_available_slots(self, date: date) -> List[datetime]:
        """Get all available time slots for a given date."""
        pass
    
    @abstractmethod
    def book_slot(self, slot: datetime, patient_id: str) -> str:
        """Book a specific time slot and return appointment ID."""
        pass
    
    @abstractmethod
    def cancel_slot(self, appointment_id: str) -> bool:
        """Cancel a booked slot and return success status."""
        pass


class Observable(ABC):
    """Interface for observable entities (Observer Pattern)."""
    
    @abstractmethod
    def add_observer(self, observer: 'Observer') -> None:
        """Add an observer to receive notifications."""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: 'Observer') -> None:
        """Remove an observer from the notification list."""
        pass
    
    @abstractmethod
    def notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        pass


class Observer(ABC):
    """Interface for observer entities (Observer Pattern)."""
    
    @abstractmethod
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Receive and process an update notification."""
        pass


class MedicalRecordHolder(ABC):
    """Interface for entities that can hold medical records."""
    
    @abstractmethod
    def add_record(self, record: 'MedicalRecord', authorized_by: str) -> str:
        """Add a medical record and return record ID."""
        pass
    
    @abstractmethod
    def get_records(self, accessor_id: str) -> List['MedicalRecord']:
        """Get all medical records (with access control)."""
        pass
    
    @abstractmethod
    def get_history(self, record_type: str = None) -> List['MedicalRecord']:
        """Get medical history, optionally filtered by type."""
        pass


# =============================================================================
# SECTION 4: DATA CLASSES
# =============================================================================

@dataclass
class ContactInfo:
    """Contact information for patients and staff."""
    phone: str
    email: str
    address: str
    emergency_contact: str = ""
    emergency_phone: str = ""


@dataclass
class InsuranceInfo:
    """Insurance information for patients."""
    insurance_type: InsuranceType
    policy_number: str
    provider: str
    expiry_date: date
    is_active: bool = True
    
    def is_valid(self) -> bool:
        """Check if insurance is currently valid."""
        return self.is_active and self.expiry_date >= date.today()
    
    def get_coverage_rate(self) -> float:
        """Get the coverage rate for this insurance."""
        if not self.is_valid():
            return 0.0
        return self.insurance_type.coverage_rate


@dataclass
class MedicalRecord:
    """A single medical record entry."""
    record_id: str
    record_type: str  # "diagnosis", "prescription", "test_result", "procedure"
    description: str
    created_by: str
    created_at: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.record_id:
            self.record_id = str(uuid.uuid4())[:8]


@dataclass
class Prescription:
    """Prescription information."""
    prescription_id: str
    medication_name: str
    dosage: str
    frequency: str
    duration_days: int
    prescribed_by: str
    prescribed_at: datetime
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.prescription_id:
            self.prescription_id = f"RX-{str(uuid.uuid4())[:6].upper()}"


@dataclass
class TimeSlot:
    """Represents a schedulable time slot."""
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    appointment_id: Optional[str] = None
    
    @property
    def duration_minutes(self) -> int:
        """Get duration in minutes."""
        return int((self.end_time - self.start_time).total_seconds() / 60)


# =============================================================================
# SECTION 5: SINGLETON PATTERN - Clinic Registry
# =============================================================================

class SingletonMeta(type):
    """
    Metaclass implementing the Singleton pattern.
    
    Ensures only one instance of a class exists throughout the application.
    Thread-safe implementation for clinic registry.
    """
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
    @classmethod
    def reset_instance(mcs, cls):
        """Reset the singleton instance (useful for testing)."""
        if cls in mcs._instances:
            del mcs._instances[cls]


class ClinicRegistry(metaclass=SingletonMeta):
    """
    Central registry for all clinic entities.
    
    Implements Singleton pattern to ensure a single source of truth
    for patients, staff, and appointments across the application.
    """
    
    def __init__(self):
        self._patients: Dict[str, 'Patient'] = {}
        self._staff: Dict[str, 'MedicalStaff'] = {}
        self._appointments: Dict[str, 'Appointment'] = {}
        self._rooms: Dict[str, 'Room'] = {}
        self._referrals: Dict[str, List[str]] = {}  # patient_id -> [specialist_ids]
        print("✓ ClinicRegistry initialized (Singleton)")
    
    # Patient Management
    def register_patient(self, patient: 'Patient') -> str:
        """Register a new patient in the system."""
        if patient.patient_id in self._patients:
            raise DuplicatePatientError(patient.patient_id)
        self._patients[patient.patient_id] = patient
        return patient.patient_id
    
    def get_patient(self, patient_id: str) -> 'Patient':
        """Retrieve a patient by ID."""
        if patient_id not in self._patients:
            raise PatientNotFoundError(patient_id)
        return self._patients[patient_id]
    
    def get_all_patients(self) -> List['Patient']:
        """Get all registered patients."""
        return list(self._patients.values())
    
    # Staff Management
    def register_staff(self, staff: 'MedicalStaff') -> str:
        """Register a staff member."""
        self._staff[staff.staff_id] = staff
        return staff.staff_id
    
    def get_staff(self, staff_id: str) -> 'MedicalStaff':
        """Retrieve a staff member by ID."""
        if staff_id not in self._staff:
            raise DoctorNotAvailableError(staff_id, "not registered")
        return self._staff[staff_id]
    
    def get_doctors_by_specialization(self, spec: Specialization) -> List['Doctor']:
        """Get all doctors with a specific specialization."""
        return [
            s for s in self._staff.values()
            if isinstance(s, Doctor) and s.specialization == spec
        ]
    
    def get_all_staff(self) -> List['MedicalStaff']:
        """Get all registered staff members."""
        return list(self._staff.values())
    
    # Appointment Management
    def add_appointment(self, appointment: 'Appointment') -> str:
        """Add an appointment to the registry."""
        self._appointments[appointment.appointment_id] = appointment
        return appointment.appointment_id
    
    def get_appointment(self, appointment_id: str) -> 'Appointment':
        """Retrieve an appointment by ID."""
        if appointment_id not in self._appointments:
            raise AppointmentException(f"Appointment {appointment_id} not found")
        return self._appointments[appointment_id]
    
    def get_patient_appointments(self, patient_id: str) -> List['Appointment']:
        """Get all appointments for a specific patient."""
        return [
            apt for apt in self._appointments.values()
            if apt.patient_id == patient_id
        ]
    
    def get_doctor_appointments(self, doctor_id: str, day: date = None) -> List['Appointment']:
        """Get all appointments for a specific doctor."""
        appointments = [
            apt for apt in self._appointments.values()
            if apt.doctor_id == doctor_id
        ]
        if day:
            appointments = [
                apt for apt in appointments
                if apt.scheduled_time.date() == day
            ]
        return appointments
    
    # Referral Management
    def add_referral(self, patient_id: str, specialist_id: str, referred_by: str) -> None:
        """Add a referral for a patient to see a specialist."""
        if patient_id not in self._referrals:
            self._referrals[patient_id] = []
        self._referrals[patient_id].append(specialist_id)
        print(f"  → Referral added: Patient {patient_id} can now see specialist {specialist_id}")
    
    def has_referral(self, patient_id: str, specialist_id: str) -> bool:
        """Check if a patient has a referral for a specific specialist."""
        return specialist_id in self._referrals.get(patient_id, [])
    
    # Room Management
    def add_room(self, room: 'Room') -> None:
        """Add a room to the registry."""
        self._rooms[room.room_number] = room
    
    def get_available_room(self, room_type: RoomType) -> Optional['Room']:
        """Get an available room of the specified type."""
        for room in self._rooms.values():
            if room.room_type == room_type and room.is_available:
                return room
        return None
    
    def get_statistics(self) -> Dict[str, int]:
        """Get clinic statistics."""
        return {
            "total_patients": len(self._patients),
            "total_staff": len(self._staff),
            "total_appointments": len(self._appointments),
            "active_appointments": len([
                a for a in self._appointments.values()
                if a.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
            ])
        }


# =============================================================================
# SECTION 6: OBSERVER PATTERN - Notification System
# =============================================================================

class AppointmentNotificationSystem(Observable):
    """
    Central notification system for appointment events.
    
    Implements the Observable interface to notify various observers
    (SMS, Email, Portal) about appointment-related events.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._event_log: List[Dict[str, Any]] = []
    
    def add_observer(self, observer: Observer) -> None:
        """Add an observer to receive notifications."""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"  → Observer added: {observer.__class__.__name__}")
    
    def remove_observer(self, observer: Observer) -> None:
        """Remove an observer from the notification list."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        event_record = {
            "event": event,
            "data": data,
            "timestamp": datetime.now(),
            "notified_count": len(self._observers)
        }
        self._event_log.append(event_record)
        
        for observer in self._observers:
            observer.update(event, data)
    
    def get_event_log(self) -> List[Dict[str, Any]]:
        """Get the history of all notification events."""
        return self._event_log.copy()


class SMSNotifier(Observer):
    """Observer that sends SMS notifications."""
    
    def __init__(self, sms_gateway: str = "MockSMSGateway"):
        self.sms_gateway = sms_gateway
        self.sent_messages: List[Dict[str, Any]] = []
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Process notification and send SMS."""
        message = self._format_message(event, data)
        phone = data.get("patient_phone", "Unknown")
        self.sent_messages.append({
            "to": phone,
            "message": message,
            "sent_at": datetime.now()
        })
        print(f"    📱 SMS to {phone}: {message}")
    
    def _format_message(self, event: str, data: Dict[str, Any]) -> str:
        """Format the notification message for SMS."""
        if event == "appointment_booked":
            return f"Appointment confirmed for {data.get('date', 'N/A')} at {data.get('time', 'N/A')} with Dr. {data.get('doctor', 'N/A')}"
        elif event == "appointment_cancelled":
            return f"Your appointment on {data.get('date', 'N/A')} has been cancelled"
        elif event == "appointment_reminder":
            return f"Reminder: Appointment tomorrow at {data.get('time', 'N/A')} with Dr. {data.get('doctor', 'N/A')}"
        elif event == "appointment_rescheduled":
            return f"Appointment rescheduled to {data.get('new_date', 'N/A')} at {data.get('new_time', 'N/A')}"
        return f"Clinic notification: {event}"


class EmailNotifier(Observer):
    """Observer that sends email notifications."""
    
    def __init__(self, smtp_server: str = "smtp.clinic.local"):
        self.smtp_server = smtp_server
        self.sent_emails: List[Dict[str, Any]] = []
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Process notification and send email."""
        email = data.get("patient_email", "unknown@clinic.local")
        subject, body = self._format_email(event, data)
        self.sent_emails.append({
            "to": email,
            "subject": subject,
            "body": body,
            "sent_at": datetime.now()
        })
        print(f"    📧 Email to {email}: {subject}")
    
    def _format_email(self, event: str, data: Dict[str, Any]) -> tuple:
        """Format the notification as an email."""
        if event == "appointment_booked":
            subject = "Appointment Confirmation"
            body = f"""
            Dear {data.get('patient_name', 'Patient')},
            
            Your appointment has been confirmed:
            Date: {data.get('date', 'N/A')}
            Time: {data.get('time', 'N/A')}
            Doctor: Dr. {data.get('doctor', 'N/A')}
            Type: {data.get('appointment_type', 'Consultation')}
            
            Please arrive 15 minutes early.
            """
        elif event == "appointment_cancelled":
            subject = "Appointment Cancellation"
            body = f"Your appointment on {data.get('date', 'N/A')} has been cancelled."
        elif event == "appointment_reminder":
            subject = "Appointment Reminder - Tomorrow"
            body = f"This is a reminder of your appointment tomorrow at {data.get('time', 'N/A')}."
        else:
            subject = f"Clinic Notification: {event}"
            body = str(data)
        return subject, body


class PatientPortalNotifier(Observer):
    """Observer that sends notifications to the patient portal."""
    
    def __init__(self):
        self.portal_notifications: List[Dict[str, Any]] = []
    
    def update(self, event: str, data: Dict[str, Any]) -> None:
        """Process notification and add to patient portal."""
        patient_id = data.get("patient_id", "Unknown")
        notification = {
            "patient_id": patient_id,
            "event": event,
            "message": self._format_notification(event, data),
            "read": False,
            "created_at": datetime.now()
        }
        self.portal_notifications.append(notification)
        print(f"    🌐 Portal notification for patient {patient_id}: {event}")
    
    def _format_notification(self, event: str, data: Dict[str, Any]) -> str:
        """Format the notification for the portal."""
        event_messages = {
            "appointment_booked": "New appointment scheduled",
            "appointment_cancelled": "Appointment cancelled",
            "appointment_reminder": "Upcoming appointment reminder",
            "appointment_rescheduled": "Appointment has been rescheduled"
        }
        return event_messages.get(event, f"Notification: {event}")
    
    def get_unread_notifications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all unread notifications for a patient."""
        return [
            n for n in self.portal_notifications
            if n["patient_id"] == patient_id and not n["read"]
        ]


# =============================================================================
# SECTION 7: STAFF HIERARCHY
# =============================================================================

class MedicalStaff(Schedulable):
    """
    Abstract base class for all medical staff members.
    
    Demonstrates:
    - Abstract base class implementation
    - Encapsulation with private/protected attributes
    - Property decorators with validation
    """
    
    def __init__(
        self,
        name: str,
        staff_id: str = None,
        contact: ContactInfo = None,
        hire_date: date = None
    ):
        self._staff_id = staff_id or f"STF-{str(uuid.uuid4())[:6].upper()}"
        self._name = name
        self._contact = contact
        self._hire_date = hire_date or date.today()
        self._is_active = True
        self._schedule: Dict[date, List[TimeSlot]] = {}
        self._max_daily_patients = 20
        self._working_hours = (9, 17)  # 9 AM to 5 PM
    
    # --- Properties with Encapsulation ---
    
    @property
    def staff_id(self) -> str:
        """Get the staff ID (read-only)."""
        return self._staff_id
    
    @property
    def name(self) -> str:
        """Get the staff member's name."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set the staff member's name with validation."""
        if not value or len(value) < 2:
            raise ValueError("Name must be at least 2 characters")
        self._name = value
    
    @property
    def is_active(self) -> bool:
        """Check if staff member is currently active."""
        return self._is_active
    
    @property
    def working_hours(self) -> tuple:
        """Get working hours as (start_hour, end_hour)."""
        return self._working_hours
    
    # --- Abstract Methods ---
    
    @abstractmethod
    def get_consultation_fee(self) -> float:
        """Get the consultation fee for this staff member."""
        pass
    
    @abstractmethod
    def get_role(self) -> str:
        """Get the role description of this staff member."""
        pass
    
    # --- Schedulable Interface Implementation ---
    
    def get_available_slots(self, target_date: date) -> List[datetime]:
        """Get all available time slots for a given date."""
        available = []
        start_hour, end_hour = self._working_hours
        
        # Generate 30-minute slots during working hours
        current = datetime.combine(target_date, datetime.min.time().replace(hour=start_hour))
        end = datetime.combine(target_date, datetime.min.time().replace(hour=end_hour))
        
        while current < end:
            if self._is_slot_available(current):
                available.append(current)
            current += timedelta(minutes=30)
        
        return available
    
    def _is_slot_available(self, slot: datetime) -> bool:
        """Check if a specific slot is available."""
        day_schedule = self._schedule.get(slot.date(), [])
        for booked_slot in day_schedule:
            if booked_slot.start_time == slot and not booked_slot.is_available:
                return False
        
        # Check daily patient limit
        booked_count = len([s for s in day_schedule if not s.is_available])
        return booked_count < self._max_daily_patients
    
    def book_slot(self, slot: datetime, patient_id: str) -> str:
        """Book a specific time slot and return appointment ID."""
        if not self._is_slot_available(slot):
            raise SlotNotAvailableError(slot, self._name)
        
        if slot.date() not in self._schedule:
            self._schedule[slot.date()] = []
        
        appointment_id = f"APT-{str(uuid.uuid4())[:8].upper()}"
        time_slot = TimeSlot(
            start_time=slot,
            end_time=slot + timedelta(minutes=30),
            is_available=False,
            appointment_id=appointment_id
        )
        self._schedule[slot.date()].append(time_slot)
        return appointment_id
    
    def cancel_slot(self, appointment_id: str) -> bool:
        """Cancel a booked slot and return success status."""
        for day_slots in self._schedule.values():
            for slot in day_slots:
                if slot.appointment_id == appointment_id:
                    slot.is_available = True
                    slot.appointment_id = None
                    return True
        return False
    
    def get_daily_patient_count(self, target_date: date) -> int:
        """Get the number of patients scheduled for a day."""
        if target_date not in self._schedule:
            return 0
        return len([s for s in self._schedule[target_date] if not s.is_available])
    
    def __str__(self) -> str:
        return f"{self.get_role()} {self._name} (ID: {self._staff_id})"


class Doctor(MedicalStaff):
    """
    Doctor class representing physicians at the clinic.
    
    Extends MedicalStaff with specialization, consultation fees,
    and additional doctor-specific functionality.
    """
    
    def __init__(
        self,
        name: str,
        specialization: Specialization = Specialization.GENERAL,
        staff_id: str = None,
        contact: ContactInfo = None,
        license_number: str = None,
        consultation_fee: float = 150.0
    ):
        super().__init__(name, staff_id, contact)
        self._specialization = specialization
        self._license_number = license_number or f"LIC-{str(uuid.uuid4())[:8].upper()}"
        self._consultation_fee = consultation_fee
        self._patients_treated: List[str] = []
        
        # Specialists have higher fees and see fewer patients
        if specialization != Specialization.GENERAL:
            self._consultation_fee *= 1.5
            self._max_daily_patients = 15
    
    @property
    def specialization(self) -> Specialization:
        """Get the doctor's specialization."""
        return self._specialization
    
    @property
    def license_number(self) -> str:
        """Get the doctor's license number."""
        return self._license_number
    
    def get_consultation_fee(self) -> float:
        """Get the consultation fee for this doctor."""
        return self._consultation_fee
    
    def get_role(self) -> str:
        """Get the role description of this doctor."""
        return f"Doctor ({self._specialization.value})"
    
    def can_treat_without_referral(self) -> bool:
        """Check if this doctor can treat patients without a referral."""
        return self._specialization == Specialization.GENERAL
    
    def prescribe_medication(
        self,
        patient: 'Patient',
        medication_name: str,
        dosage: str,
        frequency: str,
        duration_days: int
    ) -> Prescription:
        """Create a prescription for a patient."""
        # Check for medication interactions
        patient.check_medication_interactions(medication_name)
        
        prescription = Prescription(
            prescription_id=None,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            duration_days=duration_days,
            prescribed_by=self._staff_id,
            prescribed_at=datetime.now()
        )
        
        # Add to patient's records
        patient.add_prescription(prescription)
        return prescription
    
    def __str__(self) -> str:
        return f"Dr. {self._name} - {self._specialization.value}"


class Specialist(Doctor):
    """
    Specialist doctor requiring referrals for consultations.
    
    Examples: Cardiologist, Dermatologist, Neurologist
    """
    
    def __init__(
        self,
        name: str,
        specialization: Specialization,
        staff_id: str = None,
        contact: ContactInfo = None,
        sub_specialization: str = None
    ):
        if specialization == Specialization.GENERAL:
            raise ValueError("Specialists cannot have GENERAL specialization")
        
        super().__init__(name, specialization, staff_id, contact)
        self._sub_specialization = sub_specialization
        self._consultation_fee *= 1.3  # Additional specialist premium
        self._max_daily_patients = 10  # Specialists see fewer patients
    
    def requires_referral(self) -> bool:
        """Specialists always require referrals."""
        return True
    
    def get_role(self) -> str:
        """Get the role description of this specialist."""
        role = f"Specialist ({self._specialization.value})"
        if self._sub_specialization:
            role += f" - {self._sub_specialization}"
        return role
    
    def book_slot(self, slot: datetime, patient_id: str) -> str:
        """Book a slot, checking for referral first."""
        registry = ClinicRegistry()
        if not registry.has_referral(patient_id, self._staff_id):
            raise ReferralRequiredError(self._specialization)
        return super().book_slot(slot, patient_id)


class Nurse(MedicalStaff):
    """
    Nurse class for nursing staff.
    
    Handles patient care, vitals monitoring, and assisting doctors.
    """
    
    def __init__(
        self,
        name: str,
        staff_id: str = None,
        contact: ContactInfo = None,
        certification: str = "RN"
    ):
        super().__init__(name, staff_id, contact)
        self._certification = certification
        self._assigned_patients: List[str] = []
        self._consultation_fee = 50.0  # Lower fee for nurse consultations
    
    @property
    def certification(self) -> str:
        """Get the nurse's certification type."""
        return self._certification
    
    def get_consultation_fee(self) -> float:
        """Get the consultation fee for nurse services."""
        return self._consultation_fee
    
    def get_role(self) -> str:
        """Get the role description of this nurse."""
        return f"Nurse ({self._certification})"
    
    def assign_patient(self, patient_id: str) -> None:
        """Assign a patient to this nurse."""
        if patient_id not in self._assigned_patients:
            self._assigned_patients.append(patient_id)
    
    def record_vitals(
        self,
        patient: 'Patient',
        blood_pressure: str,
        heart_rate: int,
        temperature: float,
        weight: float
    ) -> MedicalRecord:
        """Record patient vitals."""
        record = MedicalRecord(
            record_id=None,
            record_type="vitals",
            description="Vital signs recorded",
            created_by=self._staff_id,
            created_at=datetime.now(),
            details={
                "blood_pressure": blood_pressure,
                "heart_rate": heart_rate,
                "temperature": temperature,
                "weight": weight
            }
        )
        patient.add_record(record, self._staff_id)
        return record


# =============================================================================
# SECTION 8: PATIENT HIERARCHY
# =============================================================================

class Patient(Billable, MedicalRecordHolder):
    """
    Abstract base class for all patient types.
    
    Demonstrates:
    - Multiple interface inheritance
    - Encapsulation of sensitive medical data
    - Access control for medical records
    """
    
    # Class-level medication interactions database
    MEDICATION_INTERACTIONS = {
        "warfarin": ["aspirin", "ibuprofen", "vitamin_e"],
        "aspirin": ["warfarin", "ibuprofen"],
        "metformin": ["alcohol", "contrast_dye"],
        "lisinopril": ["potassium", "nsaids"],
    }
    
    def __init__(
        self,
        name: str,
        date_of_birth: date,
        contact: ContactInfo,
        patient_id: str = None,
        insurance: InsuranceInfo = None
    ):
        self._patient_id = patient_id or f"PAT-{str(uuid.uuid4())[:8].upper()}"
        self._name = name
        self._date_of_birth = date_of_birth
        self._contact = contact
        self._insurance = insurance
        self._medical_history: List[MedicalRecord] = []
        self._prescriptions: List[Prescription] = []
        self._current_medications: Set[str] = set()
        self._authorized_accessors: Set[str] = set()
        self._charges: List[Dict[str, float]] = []
        self._priority = Priority.NORMAL
    
    # --- Properties with Encapsulation ---
    
    @property
    def patient_id(self) -> str:
        """Get the patient ID (read-only)."""
        return self._patient_id
    
    @property
    def name(self) -> str:
        """Get the patient's name."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set the patient's name with validation."""
        if not value or len(value) < 2:
            raise ValueError("Name must be at least 2 characters")
        self._name = value
    
    @property
    def age(self) -> int:
        """Calculate and return the patient's age."""
        today = date.today()
        return today.year - self._date_of_birth.year - (
            (today.month, today.day) < (self._date_of_birth.month, self._date_of_birth.day)
        )
    
    @property
    def contact(self) -> ContactInfo:
        """Get the patient's contact information."""
        return self._contact
    
    @property
    def insurance(self) -> Optional[InsuranceInfo]:
        """Get the patient's insurance information."""
        return self._insurance
    
    @property
    def priority(self) -> Priority:
        """Get the patient's priority level."""
        return self._priority
    
    # --- Abstract Methods ---
    
    @abstractmethod
    def get_patient_type(self) -> PatientType:
        """Get the type of patient."""
        pass
    
    @abstractmethod
    def get_base_visit_charge(self) -> float:
        """Get the base charge for a visit."""
        pass
    
    # --- Billable Interface Implementation ---
    
    def calculate_bill(self) -> float:
        """Calculate the total bill amount."""
        total = sum(charge["amount"] for charge in self._charges)
        return total
    
    def apply_insurance(self, insurance_type: InsuranceType = None) -> float:
        """Apply insurance coverage and return the amount to be paid."""
        total = self.calculate_bill()
        
        if insurance_type is None and self._insurance:
            insurance_type = self._insurance.insurance_type
        
        if insurance_type is None or insurance_type == InsuranceType.NONE:
            # No insurance: apply 15% surcharge
            return total * 1.15
        
        if self._insurance and not self._insurance.is_valid():
            raise InsuranceNotValidError(
                self._insurance.policy_number,
                "expired"
            )
        
        coverage_rate = insurance_type.coverage_rate
        patient_responsibility = total * (1 - coverage_rate)
        return patient_responsibility
    
    def get_bill_breakdown(self) -> Dict[str, float]:
        """Get a detailed breakdown of all charges."""
        breakdown = {}
        for charge in self._charges:
            category = charge.get("category", "Other")
            if category not in breakdown:
                breakdown[category] = 0.0
            breakdown[category] += charge["amount"]
        breakdown["Total"] = self.calculate_bill()
        return breakdown
    
    def add_charge(self, amount: float, description: str, category: str = "General") -> None:
        """Add a charge to the patient's bill."""
        self._charges.append({
            "amount": amount,
            "description": description,
            "category": category,
            "timestamp": datetime.now()
        })
    
    # --- MedicalRecordHolder Interface Implementation ---
    
    def add_record(self, record: MedicalRecord, authorized_by: str) -> str:
        """Add a medical record."""
        self._authorized_accessors.add(authorized_by)
        self._medical_history.append(record)
        return record.record_id
    
    def get_records(self, accessor_id: str) -> List[MedicalRecord]:
        """Get all medical records (with access control)."""
        if accessor_id not in self._authorized_accessors:
            # Allow patient to access their own records
            if accessor_id != self._patient_id:
                raise UnauthorizedAccessError(accessor_id, self._patient_id)
        return self._medical_history.copy()
    
    def get_history(self, record_type: str = None) -> List[MedicalRecord]:
        """Get medical history, optionally filtered by type."""
        if record_type:
            return [r for r in self._medical_history if r.record_type == record_type]
        return self._medical_history.copy()
    
    def authorize_accessor(self, accessor_id: str) -> None:
        """Authorize a staff member to access records."""
        self._authorized_accessors.add(accessor_id)
    
    # --- Prescription Management ---
    
    def add_prescription(self, prescription: Prescription) -> None:
        """Add a prescription and track current medications."""
        self._prescriptions.append(prescription)
        self._current_medications.add(prescription.medication_name.lower())
    
    def get_current_medications(self) -> Set[str]:
        """Get set of current medications."""
        return self._current_medications.copy()
    
    def check_medication_interactions(self, new_medication: str) -> None:
        """Check for dangerous medication interactions."""
        new_med_lower = new_medication.lower()
        interactions = self.MEDICATION_INTERACTIONS.get(new_med_lower, [])
        
        for current_med in self._current_medications:
            if current_med in interactions:
                raise MedicationInteractionError(new_medication, current_med)
            # Check reverse interaction
            if new_med_lower in self.MEDICATION_INTERACTIONS.get(current_med, []):
                raise MedicationInteractionError(current_med, new_medication)
    
    def __str__(self) -> str:
        return f"{self._name} (ID: {self._patient_id}, Type: {self.get_patient_type().name})"


class OutPatient(Patient):
    """
    Outpatient - visits clinic but doesn't stay overnight.
    
    Lower base charges, scheduled appointments only.
    """
    
    def __init__(
        self,
        name: str,
        date_of_birth: date,
        contact: ContactInfo,
        patient_id: str = None,
        insurance: InsuranceInfo = None
    ):
        super().__init__(name, date_of_birth, contact, patient_id, insurance)
        self._visit_history: List[datetime] = []
        self._priority = Priority.NORMAL
    
    def get_patient_type(self) -> PatientType:
        """Get the type of patient."""
        return PatientType.OUTPATIENT
    
    def get_base_visit_charge(self) -> float:
        """Get the base charge for an outpatient visit."""
        return 75.0
    
    def record_visit(self, visit_time: datetime = None) -> None:
        """Record a clinic visit."""
        self._visit_history.append(visit_time or datetime.now())
    
    def get_visit_count(self) -> int:
        """Get the total number of visits."""
        return len(self._visit_history)


class InPatient(Patient):
    """
    Inpatient - admitted to the clinic/hospital.
    
    Room assignment, daily charges, extended care.
    """
    
    def __init__(
        self,
        name: str,
        date_of_birth: date,
        contact: ContactInfo,
        patient_id: str = None,
        insurance: InsuranceInfo = None,
        room_type: RoomType = RoomType.GENERAL_WARD
    ):
        super().__init__(name, date_of_birth, contact, patient_id, insurance)
        self._room_type = room_type
        self._room_number: Optional[str] = None
        self._admission_date: Optional[datetime] = None
        self._discharge_date: Optional[datetime] = None
        self._assigned_nurse: Optional[str] = None
        self._priority = Priority.HIGH
    
    @property
    def room_type(self) -> RoomType:
        """Get the assigned room type."""
        return self._room_type
    
    @property
    def room_number(self) -> Optional[str]:
        """Get the assigned room number."""
        return self._room_number
    
    @property
    def days_admitted(self) -> int:
        """Calculate days admitted."""
        if not self._admission_date:
            return 0
        end_date = self._discharge_date or datetime.now()
        return max(1, (end_date - self._admission_date).days)
    
    def get_patient_type(self) -> PatientType:
        """Get the type of patient."""
        return PatientType.INPATIENT
    
    def get_base_visit_charge(self) -> float:
        """Get the base charge (admission fee)."""
        return 500.0
    
    def admit(self, room_number: str) -> None:
        """Admit the patient to a room."""
        self._room_number = room_number
        self._admission_date = datetime.now()
        self.add_charge(self.get_base_visit_charge(), "Admission Fee", "Admission")
    
    def discharge(self) -> float:
        """Discharge the patient and calculate final charges."""
        self._discharge_date = datetime.now()
        room_charges = self._room_type.daily_rate * self.days_admitted
        self.add_charge(room_charges, f"Room charges ({self.days_admitted} days)", "Room")
        return self.calculate_bill()
    
    def assign_nurse(self, nurse_id: str) -> None:
        """Assign a nurse to this patient."""
        self._assigned_nurse = nurse_id


class EmergencyPatient(Patient):
    """
    Emergency patient - arrives through emergency department.
    
    Highest priority, premium charges, immediate attention.
    """
    
    def __init__(
        self,
        name: str,
        date_of_birth: date,
        contact: ContactInfo,
        patient_id: str = None,
        insurance: InsuranceInfo = None,
        emergency_description: str = ""
    ):
        super().__init__(name, date_of_birth, contact, patient_id, insurance)
        self._emergency_description = emergency_description
        self._arrival_time = datetime.now()
        self._triage_level: int = 1  # 1=Most urgent, 5=Least urgent
        self._priority = Priority.EMERGENCY
        self._is_stabilized = False
    
    @property
    def triage_level(self) -> int:
        """Get the triage level (1-5)."""
        return self._triage_level
    
    @triage_level.setter
    def triage_level(self, level: int) -> None:
        """Set triage level with validation."""
        if not 1 <= level <= 5:
            raise ValueError("Triage level must be between 1 and 5")
        self._triage_level = level
        # Update priority based on triage
        priority_map = {1: Priority.EMERGENCY, 2: Priority.URGENT, 3: Priority.HIGH, 4: Priority.NORMAL, 5: Priority.LOW}
        self._priority = priority_map[level]
    
    def get_patient_type(self) -> PatientType:
        """Get the type of patient."""
        return PatientType.EMERGENCY
    
    def get_base_visit_charge(self) -> float:
        """Get the base charge for emergency visit (premium rate)."""
        base = 350.0
        # Higher triage urgency = higher charge
        urgency_multiplier = {1: 3.0, 2: 2.5, 3: 2.0, 4: 1.5, 5: 1.0}
        return base * urgency_multiplier[self._triage_level]
    
    def stabilize(self) -> None:
        """Mark patient as stabilized."""
        self._is_stabilized = True
        self.add_charge(200.0, "Emergency Stabilization", "Emergency")
    
    def convert_to_inpatient(self, room_type: RoomType = RoomType.GENERAL_WARD) -> InPatient:
        """Convert emergency patient to inpatient for admission."""
        inpatient = InPatient(
            name=self._name,
            date_of_birth=self._date_of_birth,
            contact=self._contact,
            patient_id=self._patient_id,
            insurance=self._insurance,
            room_type=room_type
        )
        # Transfer medical history
        for record in self._medical_history:
            inpatient._medical_history.append(record)
        for prescription in self._prescriptions:
            inpatient._prescriptions.append(prescription)
        inpatient._current_medications = self._current_medications.copy()
        inpatient._charges = self._charges.copy()
        return inpatient


# =============================================================================
# SECTION 9: APPOINTMENT HIERARCHY
# =============================================================================

class Appointment(Billable):
    """
    Abstract base class for all appointment types.
    """
    
    def __init__(
        self,
        patient_id: str,
        doctor_id: str,
        scheduled_time: datetime,
        appointment_id: str = None
    ):
        self._appointment_id = appointment_id or f"APT-{str(uuid.uuid4())[:8].upper()}"
        self._patient_id = patient_id
        self._doctor_id = doctor_id
        self._scheduled_time = scheduled_time
        self._status = AppointmentStatus.SCHEDULED
        self._notes: List[str] = []
        self._charges: List[Dict[str, float]] = []
        self._created_at = datetime.now()
    
    @property
    def appointment_id(self) -> str:
        """Get the appointment ID."""
        return self._appointment_id
    
    @property
    def patient_id(self) -> str:
        """Get the patient ID."""
        return self._patient_id
    
    @property
    def doctor_id(self) -> str:
        """Get the doctor ID."""
        return self._doctor_id
    
    @property
    def scheduled_time(self) -> datetime:
        """Get the scheduled time."""
        return self._scheduled_time
    
    @property
    def status(self) -> AppointmentStatus:
        """Get the appointment status."""
        return self._status
    
    @status.setter
    def status(self, new_status: AppointmentStatus) -> None:
        """Set the appointment status."""
        self._status = new_status
    
    @abstractmethod
    def get_duration_minutes(self) -> int:
        """Get the duration of this appointment type in minutes."""
        pass
    
    @abstractmethod
    def get_appointment_type(self) -> str:
        """Get the type name of this appointment."""
        pass
    
    @abstractmethod
    def get_base_fee(self) -> float:
        """Get the base fee for this appointment type."""
        pass
    
    # --- Billable Interface ---
    
    def calculate_bill(self) -> float:
        """Calculate total bill for appointment."""
        return self.get_base_fee() + sum(c["amount"] for c in self._charges)
    
    def apply_insurance(self, insurance_type: InsuranceType) -> float:
        """Apply insurance and return patient responsibility."""
        total = self.calculate_bill()
        if insurance_type == InsuranceType.NONE:
            return total * 1.15  # Surcharge for uninsured
        return total * (1 - insurance_type.coverage_rate)
    
    def get_bill_breakdown(self) -> Dict[str, float]:
        """Get detailed breakdown of charges."""
        breakdown = {"Base Fee": self.get_base_fee()}
        for charge in self._charges:
            category = charge.get("category", "Additional")
            if category not in breakdown:
                breakdown[category] = 0.0
            breakdown[category] += charge["amount"]
        breakdown["Total"] = self.calculate_bill()
        return breakdown
    
    def add_charge(self, amount: float, description: str, category: str = "Additional") -> None:
        """Add an additional charge to this appointment."""
        self._charges.append({
            "amount": amount,
            "description": description,
            "category": category
        })
    
    def add_note(self, note: str) -> None:
        """Add a note to the appointment."""
        self._notes.append(f"[{datetime.now()}] {note}")
    
    def confirm(self) -> None:
        """Confirm the appointment."""
        self._status = AppointmentStatus.CONFIRMED
    
    def start(self) -> None:
        """Start the appointment."""
        self._status = AppointmentStatus.IN_PROGRESS
    
    def complete(self) -> None:
        """Complete the appointment."""
        self._status = AppointmentStatus.COMPLETED
    
    def cancel(self, reason: str = "") -> None:
        """Cancel the appointment."""
        self._status = AppointmentStatus.CANCELLED
        if reason:
            self.add_note(f"Cancelled: {reason}")
    
    def reschedule(self, new_time: datetime) -> None:
        """Reschedule the appointment."""
        old_time = self._scheduled_time
        self._scheduled_time = new_time
        self.add_note(f"Rescheduled from {old_time} to {new_time}")
    
    def __str__(self) -> str:
        return f"{self.get_appointment_type()} - {self._scheduled_time} (Status: {self._status.name})"


class ConsultationAppointment(Appointment):
    """Standard consultation appointment with a doctor."""
    
    def __init__(
        self,
        patient_id: str,
        doctor_id: str,
        scheduled_time: datetime,
        reason: str = "",
        appointment_id: str = None
    ):
        super().__init__(patient_id, doctor_id, scheduled_time, appointment_id)
        self._reason = reason
    
    def get_duration_minutes(self) -> int:
        """Consultations are 30 minutes."""
        return 30
    
    def get_appointment_type(self) -> str:
        return "Consultation"
    
    def get_base_fee(self) -> float:
        return 150.0


class FollowUpAppointment(Appointment):
    """Follow-up appointment after initial consultation."""
    
    def __init__(
        self,
        patient_id: str,
        doctor_id: str,
        scheduled_time: datetime,
        original_appointment_id: str,
        appointment_id: str = None
    ):
        super().__init__(patient_id, doctor_id, scheduled_time, appointment_id)
        self._original_appointment_id = original_appointment_id
    
    def get_duration_minutes(self) -> int:
        """Follow-ups are 15 minutes."""
        return 15
    
    def get_appointment_type(self) -> str:
        return "Follow-Up"
    
    def get_base_fee(self) -> float:
        """Follow-ups are discounted."""
        return 75.0


class ProcedureAppointment(Appointment):
    """Appointment for medical procedures."""
    
    def __init__(
        self,
        patient_id: str,
        doctor_id: str,
        scheduled_time: datetime,
        procedure_name: str,
        estimated_duration: int = 60,
        requires_anesthesia: bool = False,
        appointment_id: str = None
    ):
        super().__init__(patient_id, doctor_id, scheduled_time, appointment_id)
        self._procedure_name = procedure_name
        self._estimated_duration = estimated_duration
        self._requires_anesthesia = requires_anesthesia
        
        if requires_anesthesia:
            self.add_charge(300.0, "Anesthesia", "Procedure")
    
    @property
    def procedure_name(self) -> str:
        """Get the procedure name."""
        return self._procedure_name
    
    def get_duration_minutes(self) -> int:
        """Procedures have variable duration."""
        return self._estimated_duration
    
    def get_appointment_type(self) -> str:
        return f"Procedure ({self._procedure_name})"
    
    def get_base_fee(self) -> float:
        """Procedure fees are based on complexity/duration."""
        base = 500.0
        duration_factor = self._estimated_duration / 60  # Per hour
        return base * duration_factor


# =============================================================================
# SECTION 10: FACTORY PATTERN
# =============================================================================

class PatientFactory:
    """
    Factory for creating Patient instances.
    
    Demonstrates the Factory Pattern by centralizing patient creation
    and ensuring proper initialization based on patient type.
    """
    
    @staticmethod
    def create_patient(
        patient_type: PatientType,
        name: str,
        date_of_birth: date,
        contact: ContactInfo,
        insurance: InsuranceInfo = None,
        **kwargs
    ) -> Patient:
        """
        Create a patient of the specified type.
        
        Args:
            patient_type: Type of patient to create
            name: Patient's full name
            date_of_birth: Patient's date of birth
            contact: Contact information
            insurance: Optional insurance information
            **kwargs: Additional arguments specific to patient type
        
        Returns:
            Patient instance of the specified type
        
        Raises:
            ValueError: If patient_type is not recognized
        """
        if patient_type == PatientType.OUTPATIENT:
            return OutPatient(
                name=name,
                date_of_birth=date_of_birth,
                contact=contact,
                insurance=insurance
            )
        
        elif patient_type == PatientType.INPATIENT:
            room_type = kwargs.get("room_type", RoomType.GENERAL_WARD)
            return InPatient(
                name=name,
                date_of_birth=date_of_birth,
                contact=contact,
                insurance=insurance,
                room_type=room_type
            )
        
        elif patient_type == PatientType.EMERGENCY:
            emergency_description = kwargs.get("emergency_description", "")
            return EmergencyPatient(
                name=name,
                date_of_birth=date_of_birth,
                contact=contact,
                insurance=insurance,
                emergency_description=emergency_description
            )
        
        else:
            raise ValueError(f"Unknown patient type: {patient_type}")


class AppointmentFactory:
    """
    Factory for creating Appointment instances.
    
    Handles the complexity of creating different appointment types
    with proper validation and initialization.
    """
    
    def __init__(self, notification_system: AppointmentNotificationSystem = None):
        self._notification_system = notification_system
    
    def create_appointment(
        self,
        appointment_type: str,
        patient: Patient,
        doctor: Doctor,
        scheduled_time: datetime,
        **kwargs
    ) -> Appointment:
        """
        Create an appointment of the specified type.
        
        Args:
            appointment_type: "consultation", "follow_up", or "procedure"
            patient: Patient for the appointment
            doctor: Doctor for the appointment
            scheduled_time: When the appointment is scheduled
            **kwargs: Additional arguments specific to appointment type
        
        Returns:
            Appointment instance of the specified type
        """
        # Check if slot is available
        if scheduled_time not in doctor.get_available_slots(scheduled_time.date()):
            raise SlotNotAvailableError(scheduled_time, doctor.name)
        
        # Check for specialist referral requirement
        if isinstance(doctor, Specialist):
            registry = ClinicRegistry()
            if not registry.has_referral(patient.patient_id, doctor.staff_id):
                raise ReferralRequiredError(doctor.specialization)
        
        # Create the appropriate appointment type
        if appointment_type == "consultation":
            appointment = ConsultationAppointment(
                patient_id=patient.patient_id,
                doctor_id=doctor.staff_id,
                scheduled_time=scheduled_time,
                reason=kwargs.get("reason", "")
            )
        
        elif appointment_type == "follow_up":
            original_id = kwargs.get("original_appointment_id")
            if not original_id:
                raise ValueError("Follow-up appointments require original_appointment_id")
            appointment = FollowUpAppointment(
                patient_id=patient.patient_id,
                doctor_id=doctor.staff_id,
                scheduled_time=scheduled_time,
                original_appointment_id=original_id
            )
        
        elif appointment_type == "procedure":
            procedure_name = kwargs.get("procedure_name", "General Procedure")
            appointment = ProcedureAppointment(
                patient_id=patient.patient_id,
                doctor_id=doctor.staff_id,
                scheduled_time=scheduled_time,
                procedure_name=procedure_name,
                estimated_duration=kwargs.get("duration", 60),
                requires_anesthesia=kwargs.get("requires_anesthesia", False)
            )
        
        else:
            raise ValueError(f"Unknown appointment type: {appointment_type}")
        
        # Book the slot with the doctor
        doctor.book_slot(scheduled_time, patient.patient_id)
        
        # Add to registry
        registry = ClinicRegistry()
        registry.add_appointment(appointment)
        
        # Notify observers
        if self._notification_system:
            self._notification_system.notify_observers("appointment_booked", {
                "patient_id": patient.patient_id,
                "patient_name": patient.name,
                "patient_email": patient.contact.email,
                "patient_phone": patient.contact.phone,
                "doctor": doctor.name,
                "date": scheduled_time.strftime("%Y-%m-%d"),
                "time": scheduled_time.strftime("%H:%M"),
                "appointment_type": appointment.get_appointment_type()
            })
        
        return appointment


# =============================================================================
# SECTION 11: ADAPTER PATTERN
# =============================================================================

@dataclass
class LegacyPatientRecord:
    """
    Represents a patient record from the legacy system.
    
    Uses different field names, date formats, and structures
    than the modern system.
    """
    patient_nm: str  # Legacy: "patient_nm" vs modern "name"
    dob: str  # Legacy format: "MM/DD/YYYY"
    ssn: str  # Social Security Number
    ins_code: str  # Legacy insurance code: "B", "S", "P", "G", "N"
    ins_num: str  # Insurance policy number
    addr_line1: str
    addr_line2: str
    phone_num: str  # Legacy format: "(XXX) XXX-XXXX"
    emerg_contact_nm: str
    emerg_contact_ph: str
    med_hist: List[Dict[str, str]]  # Legacy medical history format


class LegacyPatientRecordAdapter:
    """
    Adapter to convert legacy patient records to the modern format.
    
    Demonstrates the Adapter Pattern by wrapping legacy data structures
    and providing a compatible interface for the new system.
    """
    
    # Mapping of legacy insurance codes to modern InsuranceType
    INSURANCE_CODE_MAP = {
        "N": InsuranceType.NONE,
        "B": InsuranceType.BASIC,
        "S": InsuranceType.STANDARD,
        "P": InsuranceType.PREMIUM,
        "G": InsuranceType.GOVERNMENT
    }
    
    def __init__(self, legacy_record: LegacyPatientRecord):
        """
        Initialize adapter with a legacy record.
        
        Args:
            legacy_record: The legacy patient record to adapt
        """
        self._legacy = legacy_record
    
    def get_name(self) -> str:
        """Convert legacy patient_nm to name."""
        return self._legacy.patient_nm
    
    def get_date_of_birth(self) -> date:
        """Convert legacy dob format (MM/DD/YYYY) to date object."""
        try:
            return datetime.strptime(self._legacy.dob, "%m/%d/%Y").date()
        except ValueError:
            # Try alternative formats
            for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"]:
                try:
                    return datetime.strptime(self._legacy.dob, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse date: {self._legacy.dob}")
    
    def get_phone(self) -> str:
        """
        Convert legacy phone format "(XXX) XXX-XXXX" to modern format.
        Modern format: "XXX-XXX-XXXX"
        """
        # Remove all non-numeric characters
        digits = re.sub(r'\D', '', self._legacy.phone_num)
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        return self._legacy.phone_num
    
    def get_contact_info(self) -> ContactInfo:
        """Build ContactInfo from legacy fields."""
        address = self._legacy.addr_line1
        if self._legacy.addr_line2:
            address += f", {self._legacy.addr_line2}"
        
        return ContactInfo(
            phone=self.get_phone(),
            email=f"{self._legacy.patient_nm.lower().replace(' ', '.')}@legacy.import",
            address=address,
            emergency_contact=self._legacy.emerg_contact_nm,
            emergency_phone=self._legacy.emerg_contact_ph
        )
    
    def get_insurance_info(self) -> Optional[InsuranceInfo]:
        """Convert legacy insurance code to InsuranceInfo."""
        ins_type = self.INSURANCE_CODE_MAP.get(
            self._legacy.ins_code.upper(),
            InsuranceType.NONE
        )
        
        if ins_type == InsuranceType.NONE:
            return None
        
        return InsuranceInfo(
            insurance_type=ins_type,
            policy_number=self._legacy.ins_num,
            provider="Legacy Import",
            expiry_date=date.today() + timedelta(days=365),  # Default 1 year
            is_active=True
        )
    
    def get_medical_history(self) -> List[MedicalRecord]:
        """Convert legacy medical history to MedicalRecord objects."""
        records = []
        for legacy_entry in self._legacy.med_hist:
            record = MedicalRecord(
                record_id=None,
                record_type=legacy_entry.get("type", "note"),
                description=legacy_entry.get("desc", "Imported from legacy system"),
                created_by="LEGACY_IMPORT",
                created_at=datetime.now(),
                details={"legacy_data": legacy_entry}
            )
            records.append(record)
        return records
    
    def to_patient(self, patient_type: PatientType = PatientType.OUTPATIENT) -> Patient:
        """
        Convert the legacy record to a modern Patient object.
        
        Args:
            patient_type: Type of patient to create (default: OUTPATIENT)
        
        Returns:
            Patient object with data from the legacy record
        """
        patient = PatientFactory.create_patient(
            patient_type=patient_type,
            name=self.get_name(),
            date_of_birth=self.get_date_of_birth(),
            contact=self.get_contact_info(),
            insurance=self.get_insurance_info()
        )
        
        # Import medical history
        for record in self.get_medical_history():
            patient._medical_history.append(record)
            patient._authorized_accessors.add("LEGACY_IMPORT")
        
        return patient


class LegacySystemImporter:
    """
    Utility class to import multiple records from legacy system.
    
    Uses the LegacyPatientRecordAdapter for each record.
    """
    
    def __init__(self, registry: ClinicRegistry):
        self._registry = registry
        self._import_log: List[Dict[str, Any]] = []
    
    def import_records(self, legacy_records: List[LegacyPatientRecord]) -> List[Patient]:
        """
        Import multiple legacy records into the modern system.
        
        Returns list of successfully imported patients.
        """
        imported = []
        
        for legacy in legacy_records:
            try:
                adapter = LegacyPatientRecordAdapter(legacy)
                patient = adapter.to_patient()
                self._registry.register_patient(patient)
                imported.append(patient)
                
                self._import_log.append({
                    "legacy_name": legacy.patient_nm,
                    "new_id": patient.patient_id,
                    "status": "success",
                    "timestamp": datetime.now()
                })
                
            except Exception as e:
                self._import_log.append({
                    "legacy_name": legacy.patient_nm,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now()
                })
        
        return imported
    
    def get_import_log(self) -> List[Dict[str, Any]]:
        """Get the log of all import attempts."""
        return self._import_log.copy()


# =============================================================================
# SECTION 12: ROOM CLASS
# =============================================================================

class Room:
    """Represents a clinic room for inpatients."""
    
    def __init__(self, room_number: str, room_type: RoomType, floor: int = 1):
        self._room_number = room_number
        self._room_type = room_type
        self._floor = floor
        self._is_available = True
        self._current_patient_id: Optional[str] = None
        self._cleaning_required = False
    
    @property
    def room_number(self) -> str:
        return self._room_number
    
    @property
    def room_type(self) -> RoomType:
        return self._room_type
    
    @property
    def is_available(self) -> bool:
        return self._is_available and not self._cleaning_required
    
    @property
    def daily_rate(self) -> float:
        return self._room_type.daily_rate
    
    def assign_patient(self, patient_id: str) -> None:
        """Assign a patient to this room."""
        if not self.is_available:
            raise ValueError(f"Room {self._room_number} is not available")
        self._current_patient_id = patient_id
        self._is_available = False
    
    def release(self) -> None:
        """Release the room when patient is discharged."""
        self._current_patient_id = None
        self._cleaning_required = True
    
    def mark_cleaned(self) -> None:
        """Mark room as cleaned and available."""
        self._cleaning_required = False
        self._is_available = True
    
    def __str__(self) -> str:
        status = "Available" if self.is_available else "Occupied"
        return f"Room {self._room_number} ({self._room_type.description}) - {status}"


# =============================================================================
# SECTION 13: BILLING SERVICE
# =============================================================================

class BillingService:
    """
    Service class for handling billing operations.
    
    Centralizes billing logic and payment processing.
    """
    
    def __init__(self):
        self._invoices: Dict[str, Dict[str, Any]] = {}
        self._payments: List[Dict[str, Any]] = []
    
    def generate_invoice(
        self,
        patient: Patient,
        appointments: List[Appointment] = None
    ) -> Dict[str, Any]:
        """Generate an invoice for a patient."""
        invoice_id = f"INV-{str(uuid.uuid4())[:8].upper()}"
        
        # Collect all charges
        items = []
        
        # Patient base charges
        for charge in patient._charges:
            items.append({
                "description": charge["description"],
                "amount": charge["amount"],
                "category": charge["category"]
            })
        
        # Appointment charges
        if appointments:
            for apt in appointments:
                items.append({
                    "description": f"{apt.get_appointment_type()} - {apt.scheduled_time.date()}",
                    "amount": apt.calculate_bill(),
                    "category": "Appointments"
                })
        
        subtotal = sum(item["amount"] for item in items)
        
        # Apply insurance
        insurance_discount = 0.0
        if patient.insurance and patient.insurance.is_valid():
            insurance_discount = subtotal * patient.insurance.get_coverage_rate()
        
        # Calculate out-of-pocket surcharge if no insurance
        surcharge = 0.0
        if not patient.insurance or not patient.insurance.is_valid():
            surcharge = subtotal * 0.15
        
        total = subtotal - insurance_discount + surcharge
        
        invoice = {
            "invoice_id": invoice_id,
            "patient_id": patient.patient_id,
            "patient_name": patient.name,
            "items": items,
            "subtotal": subtotal,
            "insurance_discount": insurance_discount,
            "surcharge": surcharge,
            "total": total,
            "generated_at": datetime.now(),
            "status": "pending"
        }
        
        self._invoices[invoice_id] = invoice
        return invoice
    
    def process_payment(
        self,
        invoice_id: str,
        amount: float,
        payment_method: str = "card"
    ) -> bool:
        """Process a payment for an invoice."""
        if invoice_id not in self._invoices:
            raise BillingException(f"Invoice {invoice_id} not found")
        
        invoice = self._invoices[invoice_id]
        
        if amount < invoice["total"]:
            raise PaymentFailedError(amount, "insufficient amount")
        
        payment = {
            "payment_id": f"PAY-{str(uuid.uuid4())[:8].upper()}",
            "invoice_id": invoice_id,
            "amount": amount,
            "method": payment_method,
            "processed_at": datetime.now(),
            "status": "completed"
        }
        
        self._payments.append(payment)
        invoice["status"] = "paid"
        
        return True
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get an invoice by ID."""
        if invoice_id not in self._invoices:
            raise BillingException(f"Invoice {invoice_id} not found")
        return self._invoices[invoice_id]
    
    def get_patient_balance(self, patient_id: str) -> float:
        """Get the outstanding balance for a patient."""
        balance = 0.0
        for invoice in self._invoices.values():
            if invoice["patient_id"] == patient_id and invoice["status"] == "pending":
                balance += invoice["total"]
        return balance


# =============================================================================
# SECTION 14: MAIN DEMONSTRATION
# =============================================================================

def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


def main():
    """
    Main demonstration function.
    
    Showcases all OOP concepts implemented in this healthcare clinic system.
    """
    
    print_section("HEALTHCARE CLINIC MANAGEMENT SYSTEM")
    print("Demonstrating OOP Concepts: Classes, Inheritance, Interfaces,")
    print("Encapsulation, Factory, Adapter, Observer, and Singleton Patterns")
    
    # =========================================================================
    # 1. SINGLETON PATTERN DEMONSTRATION
    # =========================================================================
    print_section("1. SINGLETON PATTERN - ClinicRegistry")
    
    # Reset singleton for clean demo
    SingletonMeta.reset_instance(ClinicRegistry)
    
    registry1 = ClinicRegistry()
    registry2 = ClinicRegistry()
    
    print(f"Registry 1 ID: {id(registry1)}")
    print(f"Registry 2 ID: {id(registry2)}")
    print(f"Same instance? {registry1 is registry2}")
    
    # =========================================================================
    # 2. STAFF HIERARCHY DEMONSTRATION
    # =========================================================================
    print_section("2. STAFF HIERARCHY - MedicalStaff, Doctor, Specialist, Nurse")
    
    # Create staff members
    print_subsection("Creating Staff Members")
    
    dr_smith = Doctor(
        name="John Smith",
        specialization=Specialization.GENERAL,
        contact=ContactInfo("555-0101", "dr.smith@clinic.com", "123 Medical Ave"),
        consultation_fee=150.0
    )
    registry1.register_staff(dr_smith)
    print(f"✓ Registered: {dr_smith}")
    
    dr_jones = Specialist(
        name="Sarah Jones",
        specialization=Specialization.CARDIOLOGY,
        contact=ContactInfo("555-0102", "dr.jones@clinic.com", "123 Medical Ave"),
        sub_specialization="Interventional Cardiology"
    )
    registry1.register_staff(dr_jones)
    print(f"✓ Registered: {dr_jones}")
    
    dr_chen = Specialist(
        name="Wei Chen",
        specialization=Specialization.DERMATOLOGY,
        contact=ContactInfo("555-0103", "dr.chen@clinic.com", "123 Medical Ave")
    )
    registry1.register_staff(dr_chen)
    print(f"✓ Registered: {dr_chen}")
    
    nurse_wilson = Nurse(
        name="Mary Wilson",
        contact=ContactInfo("555-0201", "m.wilson@clinic.com", "123 Medical Ave"),
        certification="RN"
    )
    registry1.register_staff(nurse_wilson)
    print(f"✓ Registered: {nurse_wilson}")
    
    print_subsection("Staff Consultation Fees (Polymorphism)")
    for staff in registry1.get_all_staff():
        print(f"  {staff.name} ({staff.get_role()}): ${staff.get_consultation_fee():.2f}")
    
    # =========================================================================
    # 3. OBSERVER PATTERN DEMONSTRATION
    # =========================================================================
    print_section("3. OBSERVER PATTERN - Notification System")
    
    # Create notification system and observers
    notification_system = AppointmentNotificationSystem()
    
    sms_notifier = SMSNotifier()
    email_notifier = EmailNotifier()
    portal_notifier = PatientPortalNotifier()
    
    print_subsection("Registering Observers")
    notification_system.add_observer(sms_notifier)
    notification_system.add_observer(email_notifier)
    notification_system.add_observer(portal_notifier)
    
    # =========================================================================
    # 4. FACTORY PATTERN DEMONSTRATION
    # =========================================================================
    print_section("4. FACTORY PATTERN - Patient and Appointment Creation")
    
    print_subsection("Creating Patients Using PatientFactory")
    
    # Create patients using factory
    alice_contact = ContactInfo(
        phone="555-1001",
        email="alice@email.com",
        address="456 Oak Street",
        emergency_contact="Bob Brown",
        emergency_phone="555-1002"
    )
    alice_insurance = InsuranceInfo(
        insurance_type=InsuranceType.PREMIUM,
        policy_number="PREM-12345",
        provider="HealthFirst",
        expiry_date=date.today() + timedelta(days=365)
    )
    
    alice = PatientFactory.create_patient(
        patient_type=PatientType.OUTPATIENT,
        name="Alice Brown",
        date_of_birth=date(1985, 3, 15),
        contact=alice_contact,
        insurance=alice_insurance
    )
    registry1.register_patient(alice)
    print(f"✓ Created: {alice}")
    
    bob_contact = ContactInfo(
        phone="555-2001",
        email="bob@email.com",
        address="789 Pine Road"
    )
    bob_insurance = InsuranceInfo(
        insurance_type=InsuranceType.BASIC,
        policy_number="BASIC-67890",
        provider="BudgetHealth",
        expiry_date=date.today() + timedelta(days=180)
    )
    
    bob = PatientFactory.create_patient(
        patient_type=PatientType.INPATIENT,
        name="Bob Johnson",
        date_of_birth=date(1970, 8, 22),
        contact=bob_contact,
        insurance=bob_insurance,
        room_type=RoomType.PRIVATE
    )
    registry1.register_patient(bob)
    print(f"✓ Created: {bob}")
    
    # Emergency patient (no insurance)
    charlie_contact = ContactInfo(
        phone="555-3001",
        email="charlie@email.com",
        address="321 Elm Drive"
    )
    
    charlie = PatientFactory.create_patient(
        patient_type=PatientType.EMERGENCY,
        name="Charlie Davis",
        date_of_birth=date(1995, 11, 30),
        contact=charlie_contact,
        insurance=None,
        emergency_description="Chest pain and shortness of breath"
    )
    registry1.register_patient(charlie)
    print(f"✓ Created: {charlie}")
    
    print_subsection("Patient Properties (Encapsulation)")
    print(f"  Alice's age: {alice.age} years")
    print(f"  Alice's insurance: {alice.insurance.insurance_type.description}")
    print(f"  Bob's room type: {bob.room_type.description}")
    print(f"  Charlie's priority: {charlie.priority.name}")
    
    # =========================================================================
    # 5. APPOINTMENT FACTORY WITH OBSERVER NOTIFICATIONS
    # =========================================================================
    print_section("5. APPOINTMENT BOOKING WITH NOTIFICATIONS")
    
    appointment_factory = AppointmentFactory(notification_system)
    
    print_subsection("Booking Consultation Appointment")
    tomorrow = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    consultation = appointment_factory.create_appointment(
        appointment_type="consultation",
        patient=alice,
        doctor=dr_smith,
        scheduled_time=tomorrow,
        reason="Annual checkup"
    )
    print(f"✓ Created: {consultation}")
    
    print_subsection("Booking Procedure Appointment")
    procedure_time = tomorrow.replace(hour=14)
    
    procedure = appointment_factory.create_appointment(
        appointment_type="procedure",
        patient=bob,
        doctor=dr_smith,
        scheduled_time=procedure_time,
        procedure_name="Minor surgery",
        duration=90,
        requires_anesthesia=True
    )
    print(f"✓ Created: {procedure}")
    
    # =========================================================================
    # 6. REFERRAL SYSTEM AND SPECIALIST BOOKING
    # =========================================================================
    print_section("6. REFERRAL SYSTEM FOR SPECIALISTS")
    
    print_subsection("Attempting Specialist Booking Without Referral")
    try:
        specialist_time = tomorrow.replace(hour=11)
        bad_appointment = appointment_factory.create_appointment(
            appointment_type="consultation",
            patient=alice,
            doctor=dr_jones,  # Cardiologist - requires referral
            scheduled_time=specialist_time
        )
    except ReferralRequiredError as e:
        print(f"✗ Exception caught: {e}")
    
    print_subsection("Adding Referral and Booking Successfully")
    registry1.add_referral(
        patient_id=alice.patient_id,
        specialist_id=dr_jones.staff_id,
        referred_by=dr_smith.staff_id
    )
    
    cardio_appointment = appointment_factory.create_appointment(
        appointment_type="consultation",
        patient=alice,
        doctor=dr_jones,
        scheduled_time=specialist_time,
        reason="Heart palpitations - referred by Dr. Smith"
    )
    print(f"✓ Created: {cardio_appointment}")
    
    # =========================================================================
    # 7. MEDICAL RECORDS AND ACCESS CONTROL
    # =========================================================================
    print_section("7. MEDICAL RECORDS WITH ACCESS CONTROL")
    
    print_subsection("Nurse Recording Vitals")
    nurse_wilson.assign_patient(alice.patient_id)
    vitals_record = nurse_wilson.record_vitals(
        patient=alice,
        blood_pressure="120/80",
        heart_rate=72,
        temperature=98.6,
        weight=145.5
    )
    print(f"✓ Vitals recorded: {vitals_record.record_id}")
    
    print_subsection("Doctor Adding Diagnosis")
    diagnosis_record = MedicalRecord(
        record_id=None,
        record_type="diagnosis",
        description="Mild anxiety, recommended lifestyle changes",
        created_by=dr_smith.staff_id,
        created_at=datetime.now(),
        details={"condition": "Anxiety", "severity": "Mild"}
    )
    alice.add_record(diagnosis_record, dr_smith.staff_id)
    print(f"✓ Diagnosis added: {diagnosis_record.record_id}")
    
    print_subsection("Testing Access Control")
    # Authorized access
    try:
        records = alice.get_records(dr_smith.staff_id)
        print(f"✓ Dr. Smith accessed {len(records)} records")
    except UnauthorizedAccessError as e:
        print(f"✗ {e}")
    
    # Unauthorized access attempt
    try:
        records = alice.get_records("UNAUTHORIZED_USER")
        print(f"✓ Unauthorized user accessed records")
    except UnauthorizedAccessError as e:
        print(f"✗ Access denied: {e.error_code}")
    
    # Patient accessing own records
    records = alice.get_records(alice.patient_id)
    print(f"✓ Patient accessed own {len(records)} records")
    
    # =========================================================================
    # 8. PRESCRIPTION AND MEDICATION INTERACTIONS
    # =========================================================================
    print_section("8. PRESCRIPTION SYSTEM WITH INTERACTION CHECKS")
    
    print_subsection("Prescribing First Medication")
    prescription1 = dr_smith.prescribe_medication(
        patient=alice,
        medication_name="Lisinopril",
        dosage="10mg",
        frequency="Once daily",
        duration_days=30
    )
    print(f"✓ Prescribed: {prescription1.medication_name} - {prescription1.dosage}")
    
    print_subsection("Checking for Medication Interactions")
    try:
        # Attempting to prescribe interacting medication
        prescription2 = dr_smith.prescribe_medication(
            patient=alice,
            medication_name="Potassium",
            dosage="20mEq",
            frequency="Twice daily",
            duration_days=14
        )
    except MedicationInteractionError as e:
        print(f"✗ Interaction detected: {e.message}")
    
    # Safe medication
    prescription3 = dr_smith.prescribe_medication(
        patient=alice,
        medication_name="Vitamin D",
        dosage="2000 IU",
        frequency="Once daily",
        duration_days=90
    )
    print(f"✓ Prescribed: {prescription3.medication_name} (no interactions)")
    
    print(f"  Current medications: {alice.get_current_medications()}")
    
    # =========================================================================
    # 9. ADAPTER PATTERN - LEGACY DATA IMPORT
    # =========================================================================
    print_section("9. ADAPTER PATTERN - Legacy System Import")
    
    print_subsection("Legacy Record Format")
    legacy_record = LegacyPatientRecord(
        patient_nm="David Wilson",
        dob="06/15/1982",
        ssn="123-45-6789",
        ins_code="S",
        ins_num="STD-999888",
        addr_line1="100 Legacy Lane",
        addr_line2="Apt 5B",
        phone_num="(555) 444-3333",
        emerg_contact_nm="Jane Wilson",
        emerg_contact_ph="555-444-3334",
        med_hist=[
            {"type": "diagnosis", "desc": "Type 2 Diabetes - 2019"},
            {"type": "procedure", "desc": "Appendectomy - 2015"},
            {"type": "allergy", "desc": "Penicillin allergy"}
        ]
    )
    
    print(f"  Legacy name field: patient_nm = '{legacy_record.patient_nm}'")
    print(f"  Legacy date format: dob = '{legacy_record.dob}'")
    print(f"  Legacy phone format: phone_num = '{legacy_record.phone_num}'")
    print(f"  Legacy insurance code: ins_code = '{legacy_record.ins_code}'")
    
    print_subsection("Adapting to Modern Format")
    adapter = LegacyPatientRecordAdapter(legacy_record)
    
    print(f"  Adapted name: {adapter.get_name()}")
    print(f"  Adapted DOB: {adapter.get_date_of_birth()}")
    print(f"  Adapted phone: {adapter.get_phone()}")
    print(f"  Adapted insurance: {adapter.get_insurance_info().insurance_type.description}")
    
    print_subsection("Creating Modern Patient from Legacy")
    david = adapter.to_patient()
    registry1.register_patient(david)
    print(f"✓ Imported: {david}")
    print(f"  Medical history records: {len(david.get_history())}")
    
    # Batch import demonstration
    print_subsection("Batch Import with LegacySystemImporter")
    legacy_records = [
        LegacyPatientRecord(
            patient_nm="Eva Martinez",
            dob="03/22/1990",
            ssn="234-56-7890",
            ins_code="P",
            ins_num="PREM-111222",
            addr_line1="200 Import Street",
            addr_line2="",
            phone_num="(555) 222-1111",
            emerg_contact_nm="Carlos Martinez",
            emerg_contact_ph="555-222-1112",
            med_hist=[]
        ),
        LegacyPatientRecord(
            patient_nm="Frank Thompson",
            dob="12/01/1975",
            ssn="345-67-8901",
            ins_code="G",
            ins_num="GOV-333444",
            addr_line1="300 Legacy Road",
            addr_line2="Suite 100",
            phone_num="(555) 333-2222",
            emerg_contact_nm="Linda Thompson",
            emerg_contact_ph="555-333-2223",
            med_hist=[{"type": "note", "desc": "Regular checkups recommended"}]
        )
    ]
    
    importer = LegacySystemImporter(registry1)
    imported_patients = importer.import_records(legacy_records)
    print(f"✓ Imported {len(imported_patients)} patients from legacy system")
    for log_entry in importer.get_import_log():
        status = "✓" if log_entry["status"] == "success" else "✗"
        print(f"  {status} {log_entry['legacy_name']} -> {log_entry.get('new_id', 'FAILED')}")
    
    # =========================================================================
    # 10. INPATIENT MANAGEMENT
    # =========================================================================
    print_section("10. INPATIENT MANAGEMENT")
    
    print_subsection("Room Setup")
    rooms = [
        Room("101", RoomType.GENERAL_WARD, floor=1),
        Room("201", RoomType.SEMI_PRIVATE, floor=2),
        Room("301", RoomType.PRIVATE, floor=3),
        Room("ICU-1", RoomType.ICU, floor=1)
    ]
    for room in rooms:
        registry1.add_room(room)
        print(f"  {room}")
    
    print_subsection("Admitting InPatient")
    available_room = registry1.get_available_room(RoomType.PRIVATE)
    if available_room:
        bob.admit(available_room.room_number)
        available_room.assign_patient(bob.patient_id)
        print(f"✓ {bob.name} admitted to {available_room}")
    
    print_subsection("Adding InPatient Charges")
    bob.add_charge(200.0, "Lab work", "Laboratory")
    bob.add_charge(150.0, "X-Ray", "Radiology")
    bob.add_charge(75.0, "Medications", "Pharmacy")
    
    print(f"  Current charges: ${bob.calculate_bill():.2f}")
    print(f"  Days admitted: {bob.days_admitted}")
    
    # =========================================================================
    # 11. EMERGENCY PATIENT WORKFLOW
    # =========================================================================
    print_section("11. EMERGENCY PATIENT WORKFLOW")
    
    print_subsection("Emergency Triage")
    print(f"  Patient: {charlie.name}")
    print(f"  Initial priority: {charlie.priority.name}")
    
    charlie.triage_level = 2  # Urgent
    print(f"  After triage (level 2): {charlie.priority.name}")
    
    print_subsection("Emergency Stabilization")
    charlie.stabilize()
    print(f"✓ Patient stabilized")
    print(f"  Base emergency charge: ${charlie.get_base_visit_charge():.2f}")
    
    print_subsection("Converting to InPatient")
    charlie_inpatient = charlie.convert_to_inpatient(RoomType.ICU)
    icu_room = registry1.get_available_room(RoomType.ICU)
    if icu_room:
        charlie_inpatient.admit(icu_room.room_number)
        icu_room.assign_patient(charlie_inpatient.patient_id)
        print(f"✓ Converted and admitted to {icu_room}")
    
    # =========================================================================
    # 12. BILLING DEMONSTRATION
    # =========================================================================
    print_section("12. BILLING SYSTEM")
    
    billing_service = BillingService()
    
    print_subsection("Generating Invoice for Alice (Premium Insurance)")
    alice.add_charge(alice.get_base_visit_charge(), "Office Visit", "Visit")
    alice_appointments = registry1.get_patient_appointments(alice.patient_id)
    alice_invoice = billing_service.generate_invoice(alice, alice_appointments)
    
    print(f"  Invoice ID: {alice_invoice['invoice_id']}")
    print(f"  Subtotal: ${alice_invoice['subtotal']:.2f}")
    print(f"  Insurance Discount ({alice.insurance.insurance_type.description}): -${alice_invoice['insurance_discount']:.2f}")
    print(f"  Total Due: ${alice_invoice['total']:.2f}")
    
    print_subsection("Generating Invoice for Charlie (No Insurance)")
    charlie.add_charge(charlie.get_base_visit_charge(), "Emergency Visit", "Emergency")
    charlie_invoice = billing_service.generate_invoice(charlie)
    
    print(f"  Invoice ID: {charlie_invoice['invoice_id']}")
    print(f"  Subtotal: ${charlie_invoice['subtotal']:.2f}")
    print(f"  Surcharge (No Insurance): +${charlie_invoice['surcharge']:.2f}")
    print(f"  Total Due: ${charlie_invoice['total']:.2f}")
    
    print_subsection("Processing Payment")
    try:
        billing_service.process_payment(
            alice_invoice['invoice_id'],
            alice_invoice['total'],
            payment_method="credit_card"
        )
        print(f"✓ Payment processed for Alice's invoice")
    except PaymentFailedError as e:
        print(f"✗ Payment failed: {e}")
    
    # =========================================================================
    # 13. EXCEPTION HANDLING DEMONSTRATION
    # =========================================================================
    print_section("13. CUSTOM EXCEPTION HANDLING")
    
    print_subsection("Testing Various Exception Types")
    
    # PatientNotFoundError
    try:
        registry1.get_patient("INVALID-ID")
    except PatientNotFoundError as e:
        print(f"✗ {e.error_code}: {e.message}")
    
    # DuplicatePatientError
    try:
        registry1.register_patient(alice)  # Already registered
    except DuplicatePatientError as e:
        print(f"✗ {e.error_code}: {e.message}")
    
    # SlotNotAvailableError
    try:
        # Try to book same slot twice
        booked_slot = tomorrow.replace(hour=10)
        dr_smith.book_slot(booked_slot, "TEST-PATIENT")
    except SlotNotAvailableError as e:
        print(f"✗ {e.error_code}: {e.message}")
    
    # InsuranceNotValidError
    try:
        expired_insurance = InsuranceInfo(
            insurance_type=InsuranceType.STANDARD,
            policy_number="EXP-12345",
            provider="ExpiredCare",
            expiry_date=date.today() - timedelta(days=30)
        )
        if not expired_insurance.is_valid():
            raise InsuranceNotValidError(expired_insurance.policy_number, "expired")
    except InsuranceNotValidError as e:
        print(f"✗ {e.error_code}: {e.message}")
    
    # =========================================================================
    # 14. STATISTICS AND SUMMARY
    # =========================================================================
    print_section("14. CLINIC STATISTICS")
    
    stats = registry1.get_statistics()
    print(f"  Total Patients: {stats['total_patients']}")
    print(f"  Total Staff: {stats['total_staff']}")
    print(f"  Total Appointments: {stats['total_appointments']}")
    print(f"  Active Appointments: {stats['active_appointments']}")
    
    print_subsection("Notification System Log")
    event_log = notification_system.get_event_log()
    print(f"  Total notifications sent: {len(event_log)}")
    for event in event_log:
        print(f"    - {event['event']}: notified {event['notified_count']} observers")
    
    print_subsection("All Registered Patients")
    for patient in registry1.get_all_patients():
        ins_status = "Insured" if patient.insurance and patient.insurance.is_valid() else "Uninsured"
        print(f"    {patient.patient_id}: {patient.name} ({patient.get_patient_type().name}, {ins_status})")
    
    print_section("DEMONSTRATION COMPLETE")
    print("\nThis healthcare clinic system demonstrates:")
    print("  ✓ Abstract Base Classes (Patient, MedicalStaff, Appointment)")
    print("  ✓ Class Hierarchies (Doctor→Specialist, Patient→OutPatient/InPatient/Emergency)")
    print("  ✓ Interfaces (Billable, Schedulable, Observable, MedicalRecordHolder)")
    print("  ✓ Encapsulation (private attributes, properties, access control)")
    print("  ✓ Custom Exception Hierarchy (ClinicException and subclasses)")
    print("  ✓ Factory Pattern (PatientFactory, AppointmentFactory)")
    print("  ✓ Adapter Pattern (LegacyPatientRecordAdapter)")
    print("  ✓ Observer Pattern (AppointmentNotificationSystem)")
    print("  ✓ Singleton Pattern (ClinicRegistry with SingletonMeta)")
    print("  ✓ Enums for type safety (PatientType, AppointmentStatus, etc.)")
    print("  ✓ Business rules (referrals, medication interactions, billing)")


if __name__ == "__main__":
    main()
