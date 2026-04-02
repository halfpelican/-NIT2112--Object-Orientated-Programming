"""
Banking/ATM System - Complete OOP Reference Implementation
==========================================================

A comprehensive demonstration of Object-Oriented Programming concepts
for a Banking and ATM System.

OOP Concepts Demonstrated:
- Class hierarchies with ABC (Abstract Base Classes)
- Multiple interfaces (Transactable, InterestBearing, Observable, Auditable)
- Encapsulation with properties and validation
- Custom exception hierarchy
- Design Patterns: Factory, Adapter, Observer, Singleton

Author: NIT2112 Course Materials
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
import random
import hashlib


# =============================================================================
# ENUMS
# =============================================================================

class AccountType(Enum):
    """Types of bank accounts available."""
    SAVINGS = auto()
    CHECKING = auto()
    MONEY_MARKET = auto()
    CERTIFICATE_OF_DEPOSIT = auto()


class TransactionType(Enum):
    """Types of transactions that can be performed."""
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    TRANSFER = auto()
    BILL_PAYMENT = auto()
    LOAN_PAYMENT = auto()
    INTEREST = auto()
    FEE = auto()
    REFUND = auto()


class TransactionStatus(Enum):
    """Status of a transaction."""
    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()
    REVERSED = auto()
    FLAGGED = auto()


class CustomerType(Enum):
    """Types of bank customers."""
    INDIVIDUAL = auto()
    JOINT = auto()
    BUSINESS = auto()
    VIP = auto()


class CardStatus(Enum):
    """Status of a bank card."""
    ACTIVE = auto()
    BLOCKED = auto()
    EXPIRED = auto()
    LOST = auto()
    STOLEN = auto()


class ATMOperation(Enum):
    """Operations available at an ATM."""
    BALANCE_INQUIRY = auto()
    WITHDRAWAL = auto()
    DEPOSIT = auto()
    TRANSFER = auto()
    PIN_CHANGE = auto()
    MINI_STATEMENT = auto()


class AlertType(Enum):
    """Types of alerts for notifications."""
    LOW_BALANCE = auto()
    LARGE_TRANSACTION = auto()
    SUSPICIOUS_ACTIVITY = auto()
    DAILY_SUMMARY = auto()
    LOGIN_ATTEMPT = auto()
    CARD_BLOCKED = auto()


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class BankingException(Exception):
    """Base exception for all banking-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()


class AccountException(BankingException):
    """Base exception for account-related errors."""
    pass


class AccountNotFoundError(AccountException):
    """Raised when an account cannot be found."""
    
    def __init__(self, account_number: str):
        super().__init__(
            f"Account '{account_number}' not found",
            {"account_number": account_number}
        )


class AccountClosedError(AccountException):
    """Raised when trying to operate on a closed account."""
    
    def __init__(self, account_number: str):
        super().__init__(
            f"Account '{account_number}' is closed",
            {"account_number": account_number}
        )


class InsufficientFundsError(AccountException):
    """Raised when account has insufficient funds."""
    
    def __init__(self, account_number: str, requested: float, available: float):
        super().__init__(
            f"Insufficient funds: requested ${requested:.2f}, available ${available:.2f}",
            {"account_number": account_number, "requested": requested, "available": available}
        )


class MinimumBalanceViolationError(AccountException):
    """Raised when transaction would violate minimum balance requirement."""
    
    def __init__(self, account_number: str, minimum: float, resulting: float):
        super().__init__(
            f"Transaction would result in balance ${resulting:.2f}, below minimum ${minimum:.2f}",
            {"account_number": account_number, "minimum": minimum, "resulting": resulting}
        )


class TransactionException(BankingException):
    """Base exception for transaction-related errors."""
    pass


class DailyLimitExceededError(TransactionException):
    """Raised when daily transaction limit is exceeded."""
    
    def __init__(self, limit: float, attempted: float, used: float):
        super().__init__(
            f"Daily limit ${limit:.2f} exceeded. Used: ${used:.2f}, Attempted: ${attempted:.2f}",
            {"limit": limit, "attempted": attempted, "used": used}
        )


class InvalidAmountError(TransactionException):
    """Raised when transaction amount is invalid."""
    
    def __init__(self, amount: float, reason: str):
        super().__init__(
            f"Invalid amount ${amount:.2f}: {reason}",
            {"amount": amount, "reason": reason}
        )


class TransferToSameAccountError(TransactionException):
    """Raised when trying to transfer to the same account."""
    
    def __init__(self, account_number: str):
        super().__init__(
            f"Cannot transfer to the same account '{account_number}'",
            {"account_number": account_number}
        )


class TransactionPendingError(TransactionException):
    """Raised when a transaction is still pending."""
    
    def __init__(self, transaction_id: str):
        super().__init__(
            f"Transaction '{transaction_id}' is still pending",
            {"transaction_id": transaction_id}
        )


class AuthenticationException(BankingException):
    """Base exception for authentication-related errors."""
    pass


class InvalidPINError(AuthenticationException):
    """Raised when an invalid PIN is entered."""
    
    def __init__(self, attempts_remaining: int):
        super().__init__(
            f"Invalid PIN. {attempts_remaining} attempts remaining",
            {"attempts_remaining": attempts_remaining}
        )


class CardBlockedError(AuthenticationException):
    """Raised when a card is blocked."""
    
    def __init__(self, card_number: str, reason: str):
        super().__init__(
            f"Card ending in {card_number[-4:]} is blocked: {reason}",
            {"card_number_last4": card_number[-4:], "reason": reason}
        )


class SessionExpiredError(AuthenticationException):
    """Raised when a session has expired."""
    
    def __init__(self, session_id: str):
        super().__init__(
            f"Session '{session_id}' has expired",
            {"session_id": session_id}
        )


class ATMException(BankingException):
    """Base exception for ATM-related errors."""
    pass


class InsufficientCashError(ATMException):
    """Raised when ATM has insufficient cash."""
    
    def __init__(self, requested: float, available: float):
        super().__init__(
            f"ATM has insufficient cash. Requested: ${requested:.2f}",
            {"requested": requested, "available": available}
        )


class CardRetainedError(ATMException):
    """Raised when a card is retained by the ATM."""
    
    def __init__(self, card_number: str, reason: str):
        super().__init__(
            f"Card retained by ATM: {reason}",
            {"card_number_last4": card_number[-4:], "reason": reason}
        )


class WithdrawalLimitError(TransactionException):
    """Raised when withdrawal limit is exceeded."""
    
    def __init__(self, limit: float, requested: float):
        super().__init__(
            f"Withdrawal limit ${limit:.2f} exceeded. Requested: ${requested:.2f}",
            {"limit": limit, "requested": requested}
        )


# =============================================================================
# INTERFACES (Abstract Base Classes)
# =============================================================================

class Transactable(ABC):
    """Interface for objects that can process transactions."""
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the transaction."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the transaction before execution."""
        pass
    
    @abstractmethod
    def rollback(self) -> bool:
        """Rollback the transaction if needed."""
        pass


class InterestBearing(ABC):
    """Interface for accounts that earn interest."""
    
    @abstractmethod
    def calculate_interest(self) -> float:
        """Calculate interest for the current period."""
        pass
    
    @abstractmethod
    def apply_interest(self) -> float:
        """Apply calculated interest to the account."""
        pass
    
    @abstractmethod
    def get_apy(self) -> float:
        """Get the Annual Percentage Yield."""
        pass


class Observer(ABC):
    """Observer interface for the Observer pattern."""
    
    @abstractmethod
    def update(self, event_type: AlertType, data: Dict[str, Any]) -> None:
        """Receive notification of an event."""
        pass


class Observable(ABC):
    """Interface for objects that can be observed."""
    
    @abstractmethod
    def add_observer(self, observer: Observer) -> None:
        """Add an observer."""
        pass
    
    @abstractmethod
    def remove_observer(self, observer: Observer) -> None:
        """Remove an observer."""
        pass
    
    @abstractmethod
    def notify_observers(self, event_type: AlertType, data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        pass


class Auditable(ABC):
    """Interface for objects that maintain audit trails."""
    
    @abstractmethod
    def log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log an action for audit purposes."""
        pass
    
    @abstractmethod
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get the audit trail."""
        pass
    
    @abstractmethod
    def generate_report(self, start_date: date, end_date: date) -> str:
        """Generate an audit report for a date range."""
        pass


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AuditEntry:
    """Represents a single audit log entry."""
    timestamp: datetime
    action: str
    actor: str
    details: Dict[str, Any]
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.action} by {self.actor}"


@dataclass
class TransactionRecord:
    """Represents a completed transaction record."""
    transaction_id: str
    transaction_type: TransactionType
    amount: float
    timestamp: datetime
    status: TransactionStatus
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    description: str = ""
    balance_after: float = 0.0


# =============================================================================
# CUSTOMER HIERARCHY
# =============================================================================

class Customer(ABC):
    """Abstract base class for bank customers."""
    
    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        phone: str,
        address: str
    ):
        self._customer_id = customer_id
        self._name = name
        self._email = email
        self._phone = phone
        self._address = address
        self._accounts: List[str] = []
        self._created_date = datetime.now()
        self._is_active = True
    
    @property
    def customer_id(self) -> str:
        return self._customer_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def accounts(self) -> List[str]:
        return self._accounts.copy()
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @abstractmethod
    def get_customer_type(self) -> CustomerType:
        """Return the customer type."""
        pass
    
    @abstractmethod
    def get_daily_withdrawal_limit(self) -> float:
        """Return the daily withdrawal limit for this customer type."""
        pass
    
    @abstractmethod
    def get_transaction_fee_waiver(self) -> bool:
        """Return whether transaction fees are waived."""
        pass
    
    @abstractmethod
    def get_overdraft_limit(self) -> float:
        """Return the overdraft limit for this customer."""
        pass
    
    def add_account(self, account_number: str) -> None:
        """Add an account to this customer."""
        if account_number not in self._accounts:
            self._accounts.append(account_number)
    
    def remove_account(self, account_number: str) -> None:
        """Remove an account from this customer."""
        if account_number in self._accounts:
            self._accounts.remove(account_number)
    
    def __str__(self) -> str:
        return f"{self.get_customer_type().name} Customer: {self._name} ({self._customer_id})"


class IndividualCustomer(Customer):
    """Individual (personal) bank customer."""
    
    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        phone: str,
        address: str,
        date_of_birth: date,
        ssn_last4: str
    ):
        super().__init__(customer_id, name, email, phone, address)
        self._date_of_birth = date_of_birth
        self._ssn_last4 = ssn_last4
    
    def get_customer_type(self) -> CustomerType:
        return CustomerType.INDIVIDUAL
    
    def get_daily_withdrawal_limit(self) -> float:
        return 500.0
    
    def get_transaction_fee_waiver(self) -> bool:
        return False
    
    def get_overdraft_limit(self) -> float:
        return 100.0


class JointCustomer(Customer):
    """Joint account customer (two account holders)."""
    
    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        phone: str,
        address: str,
        secondary_holder_name: str,
        secondary_holder_email: str
    ):
        super().__init__(customer_id, name, email, phone, address)
        self._secondary_holder_name = secondary_holder_name
        self._secondary_holder_email = secondary_holder_email
    
    @property
    def secondary_holder(self) -> str:
        return self._secondary_holder_name
    
    def get_customer_type(self) -> CustomerType:
        return CustomerType.JOINT
    
    def get_daily_withdrawal_limit(self) -> float:
        return 750.0
    
    def get_transaction_fee_waiver(self) -> bool:
        return False
    
    def get_overdraft_limit(self) -> float:
        return 200.0


class BusinessCustomer(Customer):
    """Business/corporate bank customer."""
    
    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        phone: str,
        address: str,
        business_name: str,
        tax_id: str,
        business_type: str
    ):
        super().__init__(customer_id, name, email, phone, address)
        self._business_name = business_name
        self._tax_id = tax_id
        self._business_type = business_type
    
    @property
    def business_name(self) -> str:
        return self._business_name
    
    def get_customer_type(self) -> CustomerType:
        return CustomerType.BUSINESS
    
    def get_daily_withdrawal_limit(self) -> float:
        return 1000.0
    
    def get_transaction_fee_waiver(self) -> bool:
        return False
    
    def get_overdraft_limit(self) -> float:
        return 500.0


class VIPCustomer(Customer):
    """VIP/premium bank customer with enhanced privileges."""
    
    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        phone: str,
        address: str,
        relationship_manager: str,
        vip_tier: str = "Gold"
    ):
        super().__init__(customer_id, name, email, phone, address)
        self._relationship_manager = relationship_manager
        self._vip_tier = vip_tier
    
    @property
    def relationship_manager(self) -> str:
        return self._relationship_manager
    
    @property
    def vip_tier(self) -> str:
        return self._vip_tier
    
    def get_customer_type(self) -> CustomerType:
        return CustomerType.VIP
    
    def get_daily_withdrawal_limit(self) -> float:
        limits = {"Gold": 2500.0, "Platinum": 5000.0, "Diamond": 10000.0}
        return limits.get(self._vip_tier, 2500.0)
    
    def get_transaction_fee_waiver(self) -> bool:
        return True
    
    def get_overdraft_limit(self) -> float:
        limits = {"Gold": 1000.0, "Platinum": 2500.0, "Diamond": 5000.0}
        return limits.get(self._vip_tier, 1000.0)


# =============================================================================
# ACCOUNT HIERARCHY
# =============================================================================

class Account(InterestBearing, Observable, Auditable):
    """Abstract base class for bank accounts."""
    
    def __init__(
        self,
        account_number: str,
        customer_id: str,
        initial_balance: float = 0.0
    ):
        self._account_number = account_number
        self._customer_id = customer_id
        self._balance = initial_balance
        self._is_active = True
        self._created_date = datetime.now()
        self._transactions: List[TransactionRecord] = []
        self._observers: List[Observer] = []
        self._audit_trail: List[AuditEntry] = []
        self._daily_withdrawals: Dict[date, float] = {}
        self._monthly_withdrawals: int = 0
        self._last_interest_date = datetime.now()
        
        self.log_action("ACCOUNT_CREATED", {
            "initial_balance": initial_balance,
            "account_type": self.get_account_type().name
        })
    
    @property
    def account_number(self) -> str:
        return self._account_number
    
    @property
    def customer_id(self) -> str:
        return self._customer_id
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def transactions(self) -> List[TransactionRecord]:
        return self._transactions.copy()
    
    @abstractmethod
    def get_account_type(self) -> AccountType:
        """Return the account type."""
        pass
    
    @abstractmethod
    def get_minimum_balance(self) -> float:
        """Return the minimum balance requirement."""
        pass
    
    @abstractmethod
    def get_monthly_withdrawal_limit(self) -> Optional[int]:
        """Return monthly withdrawal limit (None if unlimited)."""
        pass
    
    @abstractmethod
    def get_withdrawal_fee(self) -> float:
        """Return fee for excess withdrawals."""
        pass
    
    def deposit(self, amount: float, description: str = "Deposit") -> TransactionRecord:
        """Deposit funds into the account."""
        if amount <= 0:
            raise InvalidAmountError(amount, "Deposit amount must be positive")
        
        if not self._is_active:
            raise AccountClosedError(self._account_number)
        
        self._balance += amount
        
        record = TransactionRecord(
            transaction_id=self._generate_transaction_id(),
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            timestamp=datetime.now(),
            status=TransactionStatus.COMPLETED,
            to_account=self._account_number,
            description=description,
            balance_after=self._balance
        )
        self._transactions.append(record)
        
        self.log_action("DEPOSIT", {"amount": amount, "new_balance": self._balance})
        
        # Notify observers for large deposits
        if amount >= 10000:
            self.notify_observers(AlertType.LARGE_TRANSACTION, {
                "type": "deposit",
                "amount": amount,
                "account": self._account_number
            })
        
        return record
    
    def withdraw(self, amount: float, description: str = "Withdrawal") -> TransactionRecord:
        """Withdraw funds from the account."""
        if amount <= 0:
            raise InvalidAmountError(amount, "Withdrawal amount must be positive")
        
        if not self._is_active:
            raise AccountClosedError(self._account_number)
        
        # Check minimum balance
        if self._balance - amount < self.get_minimum_balance():
            raise MinimumBalanceViolationError(
                self._account_number,
                self.get_minimum_balance(),
                self._balance - amount
            )
        
        # Check monthly withdrawal limits
        monthly_limit = self.get_monthly_withdrawal_limit()
        if monthly_limit is not None:
            if self._monthly_withdrawals >= monthly_limit:
                fee = self.get_withdrawal_fee()
                if fee > 0:
                    amount += fee  # Add fee to withdrawal
        
        if amount > self._balance:
            raise InsufficientFundsError(self._account_number, amount, self._balance)
        
        self._balance -= amount
        self._monthly_withdrawals += 1
        
        # Track daily withdrawals
        today = date.today()
        self._daily_withdrawals[today] = self._daily_withdrawals.get(today, 0) + amount
        
        record = TransactionRecord(
            transaction_id=self._generate_transaction_id(),
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            timestamp=datetime.now(),
            status=TransactionStatus.COMPLETED,
            from_account=self._account_number,
            description=description,
            balance_after=self._balance
        )
        self._transactions.append(record)
        
        self.log_action("WITHDRAWAL", {"amount": amount, "new_balance": self._balance})
        
        # Check for low balance alert
        if self._balance < 100:
            self.notify_observers(AlertType.LOW_BALANCE, {
                "balance": self._balance,
                "account": self._account_number
            })
        
        # Notify for large withdrawals
        if amount >= 10000:
            self.notify_observers(AlertType.LARGE_TRANSACTION, {
                "type": "withdrawal",
                "amount": amount,
                "account": self._account_number
            })
        
        return record
    
    def get_daily_withdrawal_total(self) -> float:
        """Get total withdrawals for today."""
        return self._daily_withdrawals.get(date.today(), 0)
    
    def reset_monthly_withdrawals(self) -> None:
        """Reset monthly withdrawal counter (called at month start)."""
        self._monthly_withdrawals = 0
    
    def close_account(self) -> float:
        """Close the account and return remaining balance."""
        remaining = self._balance
        self._balance = 0
        self._is_active = False
        self.log_action("ACCOUNT_CLOSED", {"final_balance": remaining})
        return remaining
    
    # Observable implementation
    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event_type: AlertType, data: Dict[str, Any]) -> None:
        for observer in self._observers:
            observer.update(event_type, data)
    
    # Auditable implementation
    def log_action(self, action: str, details: Dict[str, Any]) -> None:
        entry = AuditEntry(
            timestamp=datetime.now(),
            action=action,
            actor=self._customer_id,
            details=details
        )
        self._audit_trail.append(entry)
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "action": e.action,
                "actor": e.actor,
                "details": e.details
            }
            for e in self._audit_trail
        ]
    
    def generate_report(self, start_date: date, end_date: date) -> str:
        """Generate account statement for date range."""
        lines = [
            f"Account Statement: {self._account_number}",
            f"Period: {start_date} to {end_date}",
            f"Account Type: {self.get_account_type().name}",
            "-" * 50
        ]
        
        for txn in self._transactions:
            if start_date <= txn.timestamp.date() <= end_date:
                lines.append(
                    f"{txn.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                    f"{txn.transaction_type.name:12} | "
                    f"${txn.amount:>10.2f} | "
                    f"Balance: ${txn.balance_after:>10.2f}"
                )
        
        lines.append("-" * 50)
        lines.append(f"Current Balance: ${self._balance:.2f}")
        
        return "\n".join(lines)
    
    def _generate_transaction_id(self) -> str:
        """Generate a unique transaction ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        random_part = random.randint(1000, 9999)
        return f"TXN{timestamp}{random_part}"
    
    def __str__(self) -> str:
        return (f"{self.get_account_type().name} Account {self._account_number}: "
                f"${self._balance:.2f}")


class SavingsAccount(Account):
    """Savings account with interest and withdrawal limits."""
    
    INTEREST_RATE = 0.005  # 0.5% APY
    MONTHLY_WITHDRAWAL_LIMIT = 6
    MINIMUM_BALANCE = 100.0
    EXCESS_WITHDRAWAL_FEE = 10.0
    
    def get_account_type(self) -> AccountType:
        return AccountType.SAVINGS
    
    def get_minimum_balance(self) -> float:
        return self.MINIMUM_BALANCE
    
    def get_monthly_withdrawal_limit(self) -> Optional[int]:
        return self.MONTHLY_WITHDRAWAL_LIMIT
    
    def get_withdrawal_fee(self) -> float:
        return self.EXCESS_WITHDRAWAL_FEE
    
    # InterestBearing implementation
    def calculate_interest(self) -> float:
        """Calculate daily interest."""
        daily_rate = self.INTEREST_RATE / 365
        return self._balance * daily_rate
    
    def apply_interest(self) -> float:
        """Apply monthly interest to the account."""
        # Calculate days since last interest application
        days = (datetime.now() - self._last_interest_date).days
        if days < 30:
            return 0.0
        
        monthly_rate = self.INTEREST_RATE / 12
        interest = self._balance * monthly_rate
        
        if interest > 0:
            self._balance += interest
            self._last_interest_date = datetime.now()
            
            record = TransactionRecord(
                transaction_id=self._generate_transaction_id(),
                transaction_type=TransactionType.INTEREST,
                amount=interest,
                timestamp=datetime.now(),
                status=TransactionStatus.COMPLETED,
                to_account=self._account_number,
                description="Monthly interest credit",
                balance_after=self._balance
            )
            self._transactions.append(record)
            self.log_action("INTEREST_APPLIED", {"amount": interest})
        
        return interest
    
    def get_apy(self) -> float:
        return self.INTEREST_RATE


class CheckingAccount(Account):
    """Checking account with unlimited transactions."""
    
    MINIMUM_BALANCE = 0.0
    OVERDRAFT_FEE = 25.0
    
    def __init__(
        self,
        account_number: str,
        customer_id: str,
        initial_balance: float = 0.0,
        overdraft_protection: bool = False,
        linked_savings: Optional[str] = None
    ):
        super().__init__(account_number, customer_id, initial_balance)
        self._overdraft_protection = overdraft_protection
        self._linked_savings = linked_savings
        self._overdraft_count = 0
    
    @property
    def has_overdraft_protection(self) -> bool:
        return self._overdraft_protection
    
    def get_account_type(self) -> AccountType:
        return AccountType.CHECKING
    
    def get_minimum_balance(self) -> float:
        return self.MINIMUM_BALANCE
    
    def get_monthly_withdrawal_limit(self) -> Optional[int]:
        return None  # Unlimited
    
    def get_withdrawal_fee(self) -> float:
        return 0.0  # No excess withdrawal fee
    
    def withdraw(self, amount: float, description: str = "Withdrawal") -> TransactionRecord:
        """Withdraw with overdraft handling."""
        if amount > self._balance:
            if self._overdraft_protection and self._linked_savings:
                # Try to cover from linked savings (simplified)
                shortfall = amount - self._balance
                self.log_action("OVERDRAFT_PROTECTION_TRIGGERED", {
                    "shortfall": shortfall,
                    "linked_account": self._linked_savings
                })
            else:
                # Apply overdraft fee
                self._overdraft_count += 1
                fee_record = TransactionRecord(
                    transaction_id=self._generate_transaction_id(),
                    transaction_type=TransactionType.FEE,
                    amount=self.OVERDRAFT_FEE,
                    timestamp=datetime.now(),
                    status=TransactionStatus.COMPLETED,
                    from_account=self._account_number,
                    description="Overdraft fee",
                    balance_after=self._balance - self.OVERDRAFT_FEE
                )
                self._transactions.append(fee_record)
                self._balance -= self.OVERDRAFT_FEE
                self.log_action("OVERDRAFT_FEE", {"fee": self.OVERDRAFT_FEE})
        
        return super().withdraw(amount, description)
    
    # InterestBearing implementation (checking typically has no interest)
    def calculate_interest(self) -> float:
        return 0.0
    
    def apply_interest(self) -> float:
        return 0.0
    
    def get_apy(self) -> float:
        return 0.0


class MoneyMarketAccount(Account):
    """Money market account with higher interest but restrictions."""
    
    INTEREST_RATE = 0.02  # 2.0% APY
    MINIMUM_BALANCE = 2500.0
    MONTHLY_WITHDRAWAL_LIMIT = 3
    EXCESS_WITHDRAWAL_FEE = 15.0
    
    def get_account_type(self) -> AccountType:
        return AccountType.MONEY_MARKET
    
    def get_minimum_balance(self) -> float:
        return self.MINIMUM_BALANCE
    
    def get_monthly_withdrawal_limit(self) -> Optional[int]:
        return self.MONTHLY_WITHDRAWAL_LIMIT
    
    def get_withdrawal_fee(self) -> float:
        return self.EXCESS_WITHDRAWAL_FEE
    
    def calculate_interest(self) -> float:
        daily_rate = self.INTEREST_RATE / 365
        return self._balance * daily_rate
    
    def apply_interest(self) -> float:
        days = (datetime.now() - self._last_interest_date).days
        if days < 30:
            return 0.0
        
        monthly_rate = self.INTEREST_RATE / 12
        interest = self._balance * monthly_rate
        
        if interest > 0:
            self._balance += interest
            self._last_interest_date = datetime.now()
            
            record = TransactionRecord(
                transaction_id=self._generate_transaction_id(),
                transaction_type=TransactionType.INTEREST,
                amount=interest,
                timestamp=datetime.now(),
                status=TransactionStatus.COMPLETED,
                to_account=self._account_number,
                description="Monthly interest credit",
                balance_after=self._balance
            )
            self._transactions.append(record)
        
        return interest
    
    def get_apy(self) -> float:
        return self.INTEREST_RATE


class CertificateOfDeposit(Account):
    """Certificate of Deposit with fixed term and early withdrawal penalty."""
    
    MINIMUM_BALANCE = 1000.0
    EARLY_WITHDRAWAL_PENALTY_DAYS = 90
    
    TERM_RATES = {
        6: 0.03,   # 6 months: 3% APY
        12: 0.035, # 12 months: 3.5% APY
        24: 0.04,  # 24 months: 4% APY
        36: 0.045, # 36 months: 4.5% APY
        60: 0.05,  # 60 months: 5% APY
    }
    
    def __init__(
        self,
        account_number: str,
        customer_id: str,
        initial_balance: float,
        term_months: int = 12
    ):
        if initial_balance < self.MINIMUM_BALANCE:
            raise InvalidAmountError(
                initial_balance,
                f"CD requires minimum ${self.MINIMUM_BALANCE}"
            )
        
        super().__init__(account_number, customer_id, initial_balance)
        self._term_months = term_months
        self._maturity_date = datetime.now() + timedelta(days=term_months * 30)
        self._interest_rate = self.TERM_RATES.get(term_months, 0.035)
    
    @property
    def maturity_date(self) -> datetime:
        return self._maturity_date
    
    @property
    def term_months(self) -> int:
        return self._term_months
    
    def is_mature(self) -> bool:
        """Check if the CD has matured."""
        return datetime.now() >= self._maturity_date
    
    def get_account_type(self) -> AccountType:
        return AccountType.CERTIFICATE_OF_DEPOSIT
    
    def get_minimum_balance(self) -> float:
        return self.MINIMUM_BALANCE
    
    def get_monthly_withdrawal_limit(self) -> Optional[int]:
        return 0  # No withdrawals allowed (except with penalty)
    
    def get_withdrawal_fee(self) -> float:
        return 0.0
    
    def withdraw(self, amount: float, description: str = "Withdrawal") -> TransactionRecord:
        """Withdraw with early withdrawal penalty if not mature."""
        if not self.is_mature():
            # Calculate penalty (90 days of interest)
            daily_rate = self._interest_rate / 365
            penalty = self._balance * daily_rate * self.EARLY_WITHDRAWAL_PENALTY_DAYS
            
            self.log_action("EARLY_WITHDRAWAL_PENALTY", {
                "penalty": penalty,
                "days_penalty": self.EARLY_WITHDRAWAL_PENALTY_DAYS
            })
            
            # Apply penalty first
            self._balance -= penalty
            
            penalty_record = TransactionRecord(
                transaction_id=self._generate_transaction_id(),
                transaction_type=TransactionType.FEE,
                amount=penalty,
                timestamp=datetime.now(),
                status=TransactionStatus.COMPLETED,
                from_account=self._account_number,
                description="Early withdrawal penalty (90 days interest)",
                balance_after=self._balance
            )
            self._transactions.append(penalty_record)
        
        return super().withdraw(amount, description)
    
    def calculate_interest(self) -> float:
        daily_rate = self._interest_rate / 365
        return self._balance * daily_rate
    
    def apply_interest(self) -> float:
        """Interest is typically applied at maturity for CDs."""
        if not self.is_mature():
            return 0.0
        
        # Calculate total interest for the term
        interest = self._balance * self._interest_rate * (self._term_months / 12)
        self._balance += interest
        
        record = TransactionRecord(
            transaction_id=self._generate_transaction_id(),
            transaction_type=TransactionType.INTEREST,
            amount=interest,
            timestamp=datetime.now(),
            status=TransactionStatus.COMPLETED,
            to_account=self._account_number,
            description=f"CD maturity interest ({self._term_months} months)",
            balance_after=self._balance
        )
        self._transactions.append(record)
        
        return interest
    
    def get_apy(self) -> float:
        return self._interest_rate


# =============================================================================
# TRANSACTION HIERARCHY
# =============================================================================

class Transaction(Transactable):
    """Abstract base class for all transactions."""
    
    def __init__(
        self,
        transaction_id: str,
        amount: float,
        description: str = ""
    ):
        self._transaction_id = transaction_id
        self._amount = amount
        self._description = description
        self._status = TransactionStatus.PENDING
        self._timestamp = datetime.now()
        self._error_message: Optional[str] = None
    
    @property
    def transaction_id(self) -> str:
        return self._transaction_id
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @property
    def status(self) -> TransactionStatus:
        return self._status
    
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    @abstractmethod
    def get_transaction_type(self) -> TransactionType:
        """Return the transaction type."""
        pass


class DepositTransaction(Transaction):
    """Deposit transaction."""
    
    def __init__(
        self,
        transaction_id: str,
        amount: float,
        to_account: Account,
        description: str = "Deposit"
    ):
        super().__init__(transaction_id, amount, description)
        self._to_account = to_account
    
    def get_transaction_type(self) -> TransactionType:
        return TransactionType.DEPOSIT
    
    def validate(self) -> bool:
        if self._amount <= 0:
            self._error_message = "Deposit amount must be positive"
            return False
        if not self._to_account.is_active:
            self._error_message = "Target account is closed"
            return False
        return True
    
    def execute(self) -> bool:
        if not self.validate():
            self._status = TransactionStatus.FAILED
            return False
        
        try:
            self._to_account.deposit(self._amount, self._description)
            self._status = TransactionStatus.COMPLETED
            return True
        except BankingException as e:
            self._error_message = str(e)
            self._status = TransactionStatus.FAILED
            return False
    
    def rollback(self) -> bool:
        if self._status != TransactionStatus.COMPLETED:
            return False
        
        try:
            self._to_account.withdraw(self._amount, f"Rollback: {self._description}")
            self._status = TransactionStatus.REVERSED
            return True
        except BankingException:
            return False


class WithdrawalTransaction(Transaction):
    """Withdrawal transaction."""
    
    def __init__(
        self,
        transaction_id: str,
        amount: float,
        from_account: Account,
        daily_limit: float,
        description: str = "Withdrawal"
    ):
        super().__init__(transaction_id, amount, description)
        self._from_account = from_account
        self._daily_limit = daily_limit
    
    def get_transaction_type(self) -> TransactionType:
        return TransactionType.WITHDRAWAL
    
    def validate(self) -> bool:
        if self._amount <= 0:
            self._error_message = "Withdrawal amount must be positive"
            return False
        
        if not self._from_account.is_active:
            self._error_message = "Source account is closed"
            return False
        
        if self._amount > self._from_account.balance:
            self._error_message = "Insufficient funds"
            return False
        
        # Check daily limit
        daily_total = self._from_account.get_daily_withdrawal_total()
        if daily_total + self._amount > self._daily_limit:
            self._error_message = f"Would exceed daily limit of ${self._daily_limit}"
            return False
        
        return True
    
    def execute(self) -> bool:
        if not self.validate():
            self._status = TransactionStatus.FAILED
            return False
        
        try:
            self._from_account.withdraw(self._amount, self._description)
            self._status = TransactionStatus.COMPLETED
            return True
        except BankingException as e:
            self._error_message = str(e)
            self._status = TransactionStatus.FAILED
            return False
    
    def rollback(self) -> bool:
        if self._status != TransactionStatus.COMPLETED:
            return False
        
        try:
            self._from_account.deposit(self._amount, f"Rollback: {self._description}")
            self._status = TransactionStatus.REVERSED
            return True
        except BankingException:
            return False


class TransferTransaction(Transaction):
    """Transfer transaction between accounts."""
    
    def __init__(
        self,
        transaction_id: str,
        amount: float,
        from_account: Account,
        to_account: Account,
        description: str = "Transfer"
    ):
        super().__init__(transaction_id, amount, description)
        self._from_account = from_account
        self._to_account = to_account
    
    def get_transaction_type(self) -> TransactionType:
        return TransactionType.TRANSFER
    
    def validate(self) -> bool:
        if self._amount <= 0:
            self._error_message = "Transfer amount must be positive"
            return False
        
        if self._from_account.account_number == self._to_account.account_number:
            self._error_message = "Cannot transfer to the same account"
            return False
        
        if not self._from_account.is_active:
            self._error_message = "Source account is closed"
            return False
        
        if not self._to_account.is_active:
            self._error_message = "Target account is closed"
            return False
        
        if self._amount > self._from_account.balance:
            self._error_message = "Insufficient funds"
            return False
        
        return True
    
    def execute(self) -> bool:
        if not self.validate():
            self._status = TransactionStatus.FAILED
            return False
        
        try:
            self._from_account.withdraw(self._amount, f"Transfer to {self._to_account.account_number}")
            self._to_account.deposit(self._amount, f"Transfer from {self._from_account.account_number}")
            self._status = TransactionStatus.COMPLETED
            return True
        except BankingException as e:
            self._error_message = str(e)
            self._status = TransactionStatus.FAILED
            return False
    
    def rollback(self) -> bool:
        if self._status != TransactionStatus.COMPLETED:
            return False
        
        try:
            self._to_account.withdraw(self._amount, f"Rollback transfer")
            self._from_account.deposit(self._amount, f"Rollback transfer")
            self._status = TransactionStatus.REVERSED
            return True
        except BankingException:
            return False


class BillPaymentTransaction(Transaction):
    """Bill payment transaction."""
    
    def __init__(
        self,
        transaction_id: str,
        amount: float,
        from_account: Account,
        payee_name: str,
        payee_account: str,
        description: str = "Bill Payment"
    ):
        super().__init__(transaction_id, amount, description)
        self._from_account = from_account
        self._payee_name = payee_name
        self._payee_account = payee_account
    
    def get_transaction_type(self) -> TransactionType:
        return TransactionType.BILL_PAYMENT
    
    def validate(self) -> bool:
        if self._amount <= 0:
            self._error_message = "Payment amount must be positive"
            return False
        
        if not self._from_account.is_active:
            self._error_message = "Account is closed"
            return False
        
        if self._amount > self._from_account.balance:
            self._error_message = "Insufficient funds"
            return False
        
        return True
    
    def execute(self) -> bool:
        if not self.validate():
            self._status = TransactionStatus.FAILED
            return False
        
        try:
            self._from_account.withdraw(
                self._amount,
                f"Bill payment to {self._payee_name}"
            )
            self._status = TransactionStatus.COMPLETED
            return True
        except BankingException as e:
            self._error_message = str(e)
            self._status = TransactionStatus.FAILED
            return False
    
    def rollback(self) -> bool:
        if self._status != TransactionStatus.COMPLETED:
            return False
        
        try:
            self._from_account.deposit(
                self._amount,
                f"Refund: Bill payment to {self._payee_name}"
            )
            self._status = TransactionStatus.REVERSED
            return True
        except BankingException:
            return False


# =============================================================================
# CARD HIERARCHY
# =============================================================================

class Card(ABC):
    """Abstract base class for bank cards."""
    
    MAX_PIN_ATTEMPTS = 3
    
    def __init__(
        self,
        card_number: str,
        account_number: str,
        customer_id: str,
        expiry_date: date
    ):
        self._card_number = card_number
        self._account_number = account_number
        self._customer_id = customer_id
        self._expiry_date = expiry_date
        self._pin_hash: Optional[str] = None
        self._status = CardStatus.ACTIVE
        self._pin_attempts = 0
        self._daily_usage: Dict[date, float] = {}
    
    @property
    def card_number(self) -> str:
        return self._card_number
    
    @property
    def card_number_masked(self) -> str:
        return f"****-****-****-{self._card_number[-4:]}"
    
    @property
    def account_number(self) -> str:
        return self._account_number
    
    @property
    def status(self) -> CardStatus:
        return self._status
    
    @property
    def is_expired(self) -> bool:
        return date.today() > self._expiry_date
    
    @abstractmethod
    def get_daily_limit(self) -> float:
        """Return the daily transaction limit."""
        pass
    
    @abstractmethod
    def get_card_type(self) -> str:
        """Return the card type name."""
        pass
    
    def set_pin(self, pin: str) -> None:
        """Set the card PIN (stores hash)."""
        self._pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    
    def validate_pin(self, pin: str) -> bool:
        """Validate the entered PIN."""
        if self._status == CardStatus.BLOCKED:
            raise CardBlockedError(self._card_number, "Too many invalid PIN attempts")
        
        if self.is_expired:
            self._status = CardStatus.EXPIRED
            raise CardBlockedError(self._card_number, "Card has expired")
        
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        if pin_hash == self._pin_hash:
            self._pin_attempts = 0
            return True
        else:
            self._pin_attempts += 1
            remaining = self.MAX_PIN_ATTEMPTS - self._pin_attempts
            
            if remaining <= 0:
                self._status = CardStatus.BLOCKED
                raise CardBlockedError(
                    self._card_number,
                    "Card blocked due to too many invalid PIN attempts"
                )
            
            raise InvalidPINError(remaining)
    
    def change_pin(self, old_pin: str, new_pin: str) -> bool:
        """Change the card PIN."""
        if self.validate_pin(old_pin):
            self.set_pin(new_pin)
            return True
        return False
    
    def block(self, reason: str = "User request") -> None:
        """Block the card."""
        self._status = CardStatus.BLOCKED
    
    def unblock(self) -> None:
        """Unblock the card."""
        if not self.is_expired:
            self._status = CardStatus.ACTIVE
            self._pin_attempts = 0
    
    def get_daily_usage(self) -> float:
        """Get total usage for today."""
        return self._daily_usage.get(date.today(), 0)
    
    def record_usage(self, amount: float) -> None:
        """Record card usage for daily limit tracking."""
        today = date.today()
        self._daily_usage[today] = self._daily_usage.get(today, 0) + amount


class DebitCard(Card):
    """Debit card linked directly to an account."""
    
    DAILY_LIMIT = 2000.0
    
    def get_daily_limit(self) -> float:
        return self.DAILY_LIMIT
    
    def get_card_type(self) -> str:
        return "Debit"


class CreditCard(Card):
    """Credit card with credit limit."""
    
    DAILY_LIMIT = 5000.0
    
    def __init__(
        self,
        card_number: str,
        account_number: str,
        customer_id: str,
        expiry_date: date,
        credit_limit: float = 5000.0
    ):
        super().__init__(card_number, account_number, customer_id, expiry_date)
        self._credit_limit = credit_limit
        self._current_balance = 0.0
    
    @property
    def credit_limit(self) -> float:
        return self._credit_limit
    
    @property
    def available_credit(self) -> float:
        return self._credit_limit - self._current_balance
    
    def get_daily_limit(self) -> float:
        return min(self.DAILY_LIMIT, self.available_credit)
    
    def get_card_type(self) -> str:
        return "Credit"


class PrepaidCard(Card):
    """Prepaid card with loaded balance."""
    
    def __init__(
        self,
        card_number: str,
        account_number: str,
        customer_id: str,
        expiry_date: date,
        loaded_amount: float = 0.0
    ):
        super().__init__(card_number, account_number, customer_id, expiry_date)
        self._loaded_amount = loaded_amount
    
    @property
    def balance(self) -> float:
        return self._loaded_amount
    
    def load(self, amount: float) -> None:
        """Load money onto the card."""
        self._loaded_amount += amount
    
    def get_daily_limit(self) -> float:
        return self._loaded_amount
    
    def get_card_type(self) -> str:
        return "Prepaid"


# =============================================================================
# OBSERVER IMPLEMENTATIONS
# =============================================================================

class FraudDetectionObserver(Observer):
    """Observer for detecting fraudulent activity."""
    
    def __init__(self):
        self._alerts: List[Dict[str, Any]] = []
    
    def update(self, event_type: AlertType, data: Dict[str, Any]) -> None:
        if event_type == AlertType.LARGE_TRANSACTION:
            alert = {
                "type": "FRAUD_ALERT",
                "event": event_type.name,
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "action": "Review required for large transaction"
            }
            self._alerts.append(alert)
            print(f"  🚨 FRAUD DETECTION: Large {data.get('type', 'transaction')} "
                  f"of ${data.get('amount', 0):.2f} flagged for review")
        
        elif event_type == AlertType.SUSPICIOUS_ACTIVITY:
            alert = {
                "type": "FRAUD_ALERT",
                "event": event_type.name,
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "action": "Immediate investigation required"
            }
            self._alerts.append(alert)
            print(f"  🚨 FRAUD DETECTION: Suspicious activity detected!")
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        return self._alerts.copy()


class CustomerNotificationObserver(Observer):
    """Observer for sending customer notifications."""
    
    def __init__(self):
        self._notifications: List[Dict[str, Any]] = []
    
    def update(self, event_type: AlertType, data: Dict[str, Any]) -> None:
        notification = {
            "type": event_type.name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self._notifications.append(notification)
        
        if event_type == AlertType.LOW_BALANCE:
            print(f"  📱 SMS: Your account balance is low (${data.get('balance', 0):.2f})")
        elif event_type == AlertType.LARGE_TRANSACTION:
            print(f"  📱 SMS: {data.get('type', 'Transaction').title()} of "
                  f"${data.get('amount', 0):.2f} processed")
        elif event_type == AlertType.LOGIN_ATTEMPT:
            print(f"  📧 Email: New login from {data.get('location', 'unknown')}")
        elif event_type == AlertType.CARD_BLOCKED:
            print(f"  📱 SMS: Your card has been blocked. Contact support.")


class AuditLogObserver(Observer):
    """Observer for maintaining audit logs."""
    
    def __init__(self):
        self._log_entries: List[Dict[str, Any]] = []
    
    def update(self, event_type: AlertType, data: Dict[str, Any]) -> None:
        entry = {
            "event_type": event_type.name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self._log_entries.append(entry)
        print(f"  📋 AUDIT LOG: {event_type.name} recorded")
    
    def get_logs(self) -> List[Dict[str, Any]]:
        return self._log_entries.copy()


class BalanceMonitorObserver(Observer):
    """Observer for monitoring account balances."""
    
    def __init__(self, low_balance_threshold: float = 100.0):
        self._threshold = low_balance_threshold
        self._low_balance_accounts: Set[str] = set()
    
    def update(self, event_type: AlertType, data: Dict[str, Any]) -> None:
        if event_type == AlertType.LOW_BALANCE:
            account = data.get('account', 'Unknown')
            self._low_balance_accounts.add(account)
            print(f"  ⚠️ BALANCE MONITOR: Account {account} below threshold")
    
    def get_low_balance_accounts(self) -> Set[str]:
        return self._low_balance_accounts.copy()


# =============================================================================
# SINGLETON PATTERN - Bank Registry
# =============================================================================

class SingletonMeta(type):
    """Metaclass for implementing Singleton pattern."""
    
    _instances: Dict[type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class BankRegistry(metaclass=SingletonMeta):
    """
    Singleton registry for all bank entities.
    Ensures single source of truth for accounts, customers, and transactions.
    """
    
    def __init__(self):
        self._customers: Dict[str, Customer] = {}
        self._accounts: Dict[str, Account] = {}
        self._cards: Dict[str, Card] = {}
        self._transactions: List[Transaction] = []
        self._atms: Dict[str, 'ATM'] = {}
        self._observers: List[Observer] = []
        
        # Initialize global observers
        self._fraud_detector = FraudDetectionObserver()
        self._customer_notifier = CustomerNotificationObserver()
        self._audit_logger = AuditLogObserver()
        self._balance_monitor = BalanceMonitorObserver()
    
    def register_customer(self, customer: Customer) -> None:
        """Register a new customer."""
        if customer.customer_id in self._customers:
            raise BankingException(f"Customer {customer.customer_id} already exists")
        self._customers[customer.customer_id] = customer
    
    def get_customer(self, customer_id: str) -> Customer:
        """Get a customer by ID."""
        if customer_id not in self._customers:
            raise BankingException(f"Customer {customer_id} not found")
        return self._customers[customer_id]
    
    def register_account(self, account: Account) -> None:
        """Register a new account and attach observers."""
        if account.account_number in self._accounts:
            raise BankingException(f"Account {account.account_number} already exists")
        
        # Attach all standard observers
        account.add_observer(self._fraud_detector)
        account.add_observer(self._customer_notifier)
        account.add_observer(self._audit_logger)
        account.add_observer(self._balance_monitor)
        
        self._accounts[account.account_number] = account
        
        # Link to customer
        customer = self._customers.get(account.customer_id)
        if customer:
            customer.add_account(account.account_number)
    
    def get_account(self, account_number: str) -> Account:
        """Get an account by number."""
        if account_number not in self._accounts:
            raise AccountNotFoundError(account_number)
        return self._accounts[account_number]
    
    def register_card(self, card: Card) -> None:
        """Register a new card."""
        self._cards[card.card_number] = card
    
    def get_card(self, card_number: str) -> Card:
        """Get a card by number."""
        if card_number not in self._cards:
            raise BankingException(f"Card not found")
        return self._cards[card_number]
    
    def register_atm(self, atm: 'ATM') -> None:
        """Register an ATM."""
        self._atms[atm.atm_id] = atm
    
    def get_atm(self, atm_id: str) -> 'ATM':
        """Get an ATM by ID."""
        if atm_id not in self._atms:
            raise BankingException(f"ATM {atm_id} not found")
        return self._atms[atm_id]
    
    def record_transaction(self, transaction: Transaction) -> None:
        """Record a transaction."""
        self._transactions.append(transaction)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_customers": len(self._customers),
            "total_accounts": len(self._accounts),
            "total_cards": len(self._cards),
            "total_transactions": len(self._transactions),
            "total_atms": len(self._atms),
            "accounts_by_type": self._count_accounts_by_type(),
            "customers_by_type": self._count_customers_by_type(),
            "low_balance_accounts": len(self._balance_monitor.get_low_balance_accounts()),
            "fraud_alerts": len(self._fraud_detector.get_alerts())
        }
    
    def _count_accounts_by_type(self) -> Dict[str, int]:
        counts = {}
        for account in self._accounts.values():
            acc_type = account.get_account_type().name
            counts[acc_type] = counts.get(acc_type, 0) + 1
        return counts
    
    def _count_customers_by_type(self) -> Dict[str, int]:
        counts = {}
        for customer in self._customers.values():
            cust_type = customer.get_customer_type().name
            counts[cust_type] = counts.get(cust_type, 0) + 1
        return counts


# =============================================================================
# FACTORY PATTERN
# =============================================================================

class AccountFactory:
    """Factory for creating bank accounts."""
    
    _account_counter = 1000
    
    @classmethod
    def _generate_account_number(cls) -> str:
        cls._account_counter += 1
        return f"ACC{cls._account_counter:08d}"
    
    @classmethod
    def create_account(
        cls,
        account_type: AccountType,
        customer_id: str,
        initial_deposit: float,
        **kwargs
    ) -> Account:
        """
        Create an account of the specified type.
        
        Args:
            account_type: Type of account to create
            customer_id: Customer ID
            initial_deposit: Initial deposit amount
            **kwargs: Additional arguments for specific account types
        
        Returns:
            Created account instance
        """
        account_number = cls._generate_account_number()
        
        if account_type == AccountType.SAVINGS:
            return SavingsAccount(account_number, customer_id, initial_deposit)
        
        elif account_type == AccountType.CHECKING:
            return CheckingAccount(
                account_number,
                customer_id,
                initial_deposit,
                overdraft_protection=kwargs.get('overdraft_protection', False),
                linked_savings=kwargs.get('linked_savings')
            )
        
        elif account_type == AccountType.MONEY_MARKET:
            if initial_deposit < MoneyMarketAccount.MINIMUM_BALANCE:
                raise InvalidAmountError(
                    initial_deposit,
                    f"Money Market requires minimum ${MoneyMarketAccount.MINIMUM_BALANCE}"
                )
            return MoneyMarketAccount(account_number, customer_id, initial_deposit)
        
        elif account_type == AccountType.CERTIFICATE_OF_DEPOSIT:
            return CertificateOfDeposit(
                account_number,
                customer_id,
                initial_deposit,
                term_months=kwargs.get('term_months', 12)
            )
        
        else:
            raise ValueError(f"Unknown account type: {account_type}")


class TransactionFactory:
    """Factory for creating transactions."""
    
    _transaction_counter = 0
    
    @classmethod
    def _generate_transaction_id(cls) -> str:
        cls._transaction_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TXN{timestamp}{cls._transaction_counter:04d}"
    
    @classmethod
    def create_deposit(
        cls,
        amount: float,
        to_account: Account,
        description: str = "Deposit"
    ) -> DepositTransaction:
        """Create a deposit transaction."""
        return DepositTransaction(
            cls._generate_transaction_id(),
            amount,
            to_account,
            description
        )
    
    @classmethod
    def create_withdrawal(
        cls,
        amount: float,
        from_account: Account,
        daily_limit: float,
        description: str = "Withdrawal"
    ) -> WithdrawalTransaction:
        """Create a withdrawal transaction."""
        return WithdrawalTransaction(
            cls._generate_transaction_id(),
            amount,
            from_account,
            daily_limit,
            description
        )
    
    @classmethod
    def create_transfer(
        cls,
        amount: float,
        from_account: Account,
        to_account: Account,
        description: str = "Transfer"
    ) -> TransferTransaction:
        """Create a transfer transaction."""
        if from_account.account_number == to_account.account_number:
            raise TransferToSameAccountError(from_account.account_number)
        
        return TransferTransaction(
            cls._generate_transaction_id(),
            amount,
            from_account,
            to_account,
            description
        )
    
    @classmethod
    def create_bill_payment(
        cls,
        amount: float,
        from_account: Account,
        payee_name: str,
        payee_account: str,
        description: str = "Bill Payment"
    ) -> BillPaymentTransaction:
        """Create a bill payment transaction."""
        return BillPaymentTransaction(
            cls._generate_transaction_id(),
            amount,
            from_account,
            payee_name,
            payee_account,
            description
        )


class CardFactory:
    """Factory for creating bank cards."""
    
    @classmethod
    def _generate_card_number(cls) -> str:
        """Generate a 16-digit card number."""
        return ''.join([str(random.randint(0, 9)) for _ in range(16)])
    
    @classmethod
    def create_card(
        cls,
        card_type: str,
        account_number: str,
        customer_id: str,
        **kwargs
    ) -> Card:
        """Create a card of the specified type."""
        card_number = cls._generate_card_number()
        expiry_date = date.today() + timedelta(days=365 * 3)  # 3 years validity
        
        if card_type.lower() == "debit":
            return DebitCard(card_number, account_number, customer_id, expiry_date)
        
        elif card_type.lower() == "credit":
            return CreditCard(
                card_number,
                account_number,
                customer_id,
                expiry_date,
                credit_limit=kwargs.get('credit_limit', 5000.0)
            )
        
        elif card_type.lower() == "prepaid":
            return PrepaidCard(
                card_number,
                account_number,
                customer_id,
                expiry_date,
                loaded_amount=kwargs.get('loaded_amount', 0.0)
            )
        
        else:
            raise ValueError(f"Unknown card type: {card_type}")


# =============================================================================
# ADAPTER PATTERN
# =============================================================================

@dataclass
class LegacyAccountData:
    """Represents data from a legacy banking system."""
    acct_num: str  # Old format: "SAV-12345" or "CHK-67890"
    cust_name: str
    cust_ssn: str  # Full SSN in legacy system
    balance_cents: int  # Balance in cents
    acct_status: str  # "A" for active, "C" for closed
    open_date: str  # Format: "MMDDYYYY"
    interest_rate_bps: int  # Interest rate in basis points


class LegacyBankingAdapter:
    """
    Adapter to convert legacy banking system data to new system format.
    Demonstrates the Adapter pattern.
    """
    
    ACCOUNT_TYPE_MAPPING = {
        "SAV": AccountType.SAVINGS,
        "CHK": AccountType.CHECKING,
        "MMA": AccountType.MONEY_MARKET,
        "COD": AccountType.CERTIFICATE_OF_DEPOSIT
    }
    
    @classmethod
    def convert_account_number(cls, legacy_num: str) -> Tuple[AccountType, str]:
        """Convert legacy account number to new format."""
        parts = legacy_num.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid legacy account number: {legacy_num}")
        
        type_code, number = parts
        account_type = cls.ACCOUNT_TYPE_MAPPING.get(type_code)
        
        if account_type is None:
            raise ValueError(f"Unknown account type code: {type_code}")
        
        new_number = f"ACC{int(number):08d}"
        return account_type, new_number
    
    @classmethod
    def convert_balance(cls, balance_cents: int) -> float:
        """Convert balance from cents to dollars."""
        return balance_cents / 100.0
    
    @classmethod
    def convert_date(cls, legacy_date: str) -> date:
        """Convert legacy date format (MMDDYYYY) to date object."""
        month = int(legacy_date[0:2])
        day = int(legacy_date[2:4])
        year = int(legacy_date[4:8])
        return date(year, month, day)
    
    @classmethod
    def convert_status(cls, legacy_status: str) -> bool:
        """Convert legacy status to boolean is_active."""
        return legacy_status.upper() == "A"
    
    @classmethod
    def convert_interest_rate(cls, rate_bps: int) -> float:
        """Convert interest rate from basis points to decimal."""
        return rate_bps / 10000.0
    
    @classmethod
    def mask_ssn(cls, full_ssn: str) -> str:
        """Mask SSN to show only last 4 digits."""
        # Remove any dashes or spaces
        clean_ssn = ''.join(filter(str.isdigit, full_ssn))
        return clean_ssn[-4:] if len(clean_ssn) >= 4 else clean_ssn
    
    @classmethod
    def import_legacy_account(
        cls,
        legacy_data: LegacyAccountData,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Convert legacy account data to new system format.
        
        Returns a dictionary that can be used to create a new account.
        """
        account_type, account_number = cls.convert_account_number(legacy_data.acct_num)
        
        return {
            "account_type": account_type,
            "account_number": account_number,
            "customer_id": customer_id,
            "balance": cls.convert_balance(legacy_data.balance_cents),
            "is_active": cls.convert_status(legacy_data.acct_status),
            "open_date": cls.convert_date(legacy_data.open_date),
            "interest_rate": cls.convert_interest_rate(legacy_data.interest_rate_bps),
            "customer_name": legacy_data.cust_name,
            "ssn_last4": cls.mask_ssn(legacy_data.cust_ssn)
        }


# =============================================================================
# ATM CLASS
# =============================================================================

class ATM:
    """
    ATM machine simulation with full transaction capabilities.
    """
    
    SESSION_TIMEOUT_MINUTES = 5
    MAX_WITHDRAWAL_PER_TRANSACTION = 500.0
    
    DENOMINATIONS = [100, 50, 20, 10]  # Available bill denominations
    
    def __init__(
        self,
        atm_id: str,
        location: str,
        initial_cash: float = 50000.0
    ):
        self._atm_id = atm_id
        self._location = location
        self._cash_available = initial_cash
        self._is_operational = True
        
        # Session management
        self._current_card: Optional[Card] = None
        self._current_account: Optional[Account] = None
        self._session_start: Optional[datetime] = None
        self._authenticated = False
    
    @property
    def atm_id(self) -> str:
        return self._atm_id
    
    @property
    def location(self) -> str:
        return self._location
    
    @property
    def cash_available(self) -> float:
        return self._cash_available
    
    @property
    def is_operational(self) -> bool:
        return self._is_operational
    
    def _check_session(self) -> None:
        """Check if session is valid and not expired."""
        if not self._authenticated:
            raise SessionExpiredError("No active session")
        
        if self._session_start:
            elapsed = datetime.now() - self._session_start
            if elapsed.total_seconds() > self.SESSION_TIMEOUT_MINUTES * 60:
                self._end_session()
                raise SessionExpiredError("Session timed out")
    
    def insert_card(self, card: Card) -> str:
        """Insert a card into the ATM."""
        if not self._is_operational:
            raise ATMException("ATM is out of service", {})
        
        if card.status == CardStatus.BLOCKED:
            raise CardBlockedError(card.card_number, "Card is blocked")
        
        if card.is_expired:
            raise CardBlockedError(card.card_number, "Card has expired")
        
        self._current_card = card
        return f"Card {card.card_number_masked} inserted. Please enter your PIN."
    
    def enter_pin(self, pin: str) -> str:
        """Enter PIN for authentication."""
        if self._current_card is None:
            raise ATMException("No card inserted", {})
        
        try:
            self._current_card.validate_pin(pin)
            self._authenticated = True
            self._session_start = datetime.now()
            
            # Get the linked account
            registry = BankRegistry()
            self._current_account = registry.get_account(
                self._current_card.account_number
            )
            
            return "PIN accepted. Welcome!"
        except InvalidPINError:
            raise
        except CardBlockedError as e:
            self._retain_card("Too many invalid PIN attempts")
            raise
    
    def check_balance(self) -> str:
        """Check account balance."""
        self._check_session()
        
        balance = self._current_account.balance
        account_type = self._current_account.get_account_type().name
        
        return f"""
╔══════════════════════════════════════╗
║         BALANCE INQUIRY              ║
╠══════════════════════════════════════╣
║ Account: {self._current_account.account_number}      ║
║ Type: {account_type:20}       ║
║ Available Balance: ${balance:>12,.2f}  ║
╚══════════════════════════════════════╝
"""
    
    def withdraw(self, amount: float) -> str:
        """Withdraw cash from ATM."""
        self._check_session()
        
        # Validate amount
        if amount <= 0:
            raise InvalidAmountError(amount, "Amount must be positive")
        
        if amount > self.MAX_WITHDRAWAL_PER_TRANSACTION:
            raise WithdrawalLimitError(self.MAX_WITHDRAWAL_PER_TRANSACTION, amount)
        
        # Check if amount is dispensable (multiples of smallest denomination)
        if amount % min(self.DENOMINATIONS) != 0:
            raise InvalidAmountError(
                amount,
                f"Amount must be in multiples of ${min(self.DENOMINATIONS)}"
            )
        
        # Check ATM cash availability
        if amount > self._cash_available:
            raise InsufficientCashError(amount, self._cash_available)
        
        # Check daily limit
        card_daily_limit = self._current_card.get_daily_limit()
        current_usage = self._current_card.get_daily_usage()
        
        if current_usage + amount > card_daily_limit:
            raise DailyLimitExceededError(card_daily_limit, amount, current_usage)
        
        # Perform withdrawal
        try:
            self._current_account.withdraw(amount, f"ATM Withdrawal at {self._location}")
            self._cash_available -= amount
            self._current_card.record_usage(amount)
            
            # Calculate bill dispensing
            bills = self._calculate_bills(amount)
            
            return self._format_withdrawal_receipt(amount, bills)
        except BankingException:
            raise
    
    def _calculate_bills(self, amount: float) -> Dict[int, int]:
        """Calculate bill denomination breakdown."""
        bills = {}
        remaining = int(amount)
        
        for denom in self.DENOMINATIONS:
            if remaining >= denom:
                count = remaining // denom
                bills[denom] = count
                remaining -= count * denom
        
        return bills
    
    def _format_withdrawal_receipt(
        self,
        amount: float,
        bills: Dict[int, int]
    ) -> str:
        """Format withdrawal receipt."""
        bill_lines = "\n".join([
            f"║   ${denom:>3} x {count:>2} = ${denom * count:>6}           ║"
            for denom, count in bills.items()
        ])
        
        new_balance = self._current_account.balance
        
        return f"""
╔══════════════════════════════════════╗
║           ATM WITHDRAWAL             ║
╠══════════════════════════════════════╣
║ Amount: ${amount:>10,.2f}                ║
╠══════════════════════════════════════╣
║ Bills Dispensed:                     ║
{bill_lines}
╠══════════════════════════════════════╣
║ New Balance: ${new_balance:>10,.2f}           ║
╠══════════════════════════════════════╣
║ Please take your cash.               ║
╚══════════════════════════════════════╝
"""
    
    def deposit(self, amount: float) -> str:
        """Deposit cash at ATM."""
        self._check_session()
        
        if amount <= 0:
            raise InvalidAmountError(amount, "Amount must be positive")
        
        self._current_account.deposit(amount, f"ATM Deposit at {self._location}")
        self._cash_available += amount
        
        new_balance = self._current_account.balance
        
        return f"""
╔══════════════════════════════════════╗
║            ATM DEPOSIT               ║
╠══════════════════════════════════════╣
║ Amount Deposited: ${amount:>10,.2f}       ║
║ New Balance: ${new_balance:>14,.2f}       ║
╠══════════════════════════════════════╣
║ Thank you for your deposit.          ║
╚══════════════════════════════════════╝
"""
    
    def transfer(self, to_account_number: str, amount: float) -> str:
        """Transfer funds to another account."""
        self._check_session()
        
        registry = BankRegistry()
        to_account = registry.get_account(to_account_number)
        
        transfer_txn = TransactionFactory.create_transfer(
            amount,
            self._current_account,
            to_account,
            f"ATM Transfer at {self._location}"
        )
        
        if transfer_txn.execute():
            registry.record_transaction(transfer_txn)
            new_balance = self._current_account.balance
            
            return f"""
╔══════════════════════════════════════╗
║           ATM TRANSFER               ║
╠══════════════════════════════════════╣
║ To Account: {to_account_number}       ║
║ Amount: ${amount:>10,.2f}                ║
║ New Balance: ${new_balance:>10,.2f}           ║
╠══════════════════════════════════════╣
║ Transfer completed successfully.     ║
╚══════════════════════════════════════╝
"""
        else:
            raise TransactionException(
                f"Transfer failed: {transfer_txn._error_message}",
                {}
            )
    
    def get_mini_statement(self) -> str:
        """Get mini statement (last 5 transactions)."""
        self._check_session()
        
        transactions = self._current_account.transactions[-5:]
        
        lines = [
            "╔══════════════════════════════════════╗",
            "║          MINI STATEMENT              ║",
            "╠══════════════════════════════════════╣",
            f"║ Account: {self._current_account.account_number}      ║",
            "╠══════════════════════════════════════╣"
        ]
        
        for txn in transactions:
            txn_date = txn.timestamp.strftime("%m/%d")
            txn_type = txn.transaction_type.name[:8]
            lines.append(
                f"║ {txn_date} {txn_type:8} ${txn.amount:>8.2f} ║"
            )
        
        lines.extend([
            "╠══════════════════════════════════════╣",
            f"║ Current Balance: ${self._current_account.balance:>10,.2f}   ║",
            "╚══════════════════════════════════════╝"
        ])
        
        return "\n".join(lines)
    
    def change_pin(self, old_pin: str, new_pin: str) -> str:
        """Change card PIN."""
        self._check_session()
        
        if len(new_pin) != 4 or not new_pin.isdigit():
            raise InvalidAmountError(0, "PIN must be 4 digits")
        
        if self._current_card.change_pin(old_pin, new_pin):
            return "PIN changed successfully."
        else:
            raise AuthenticationException("Failed to change PIN", {})
    
    def _end_session(self) -> None:
        """End the current session."""
        self._current_card = None
        self._current_account = None
        self._session_start = None
        self._authenticated = False
    
    def eject_card(self) -> str:
        """Eject the card and end session."""
        card_masked = (self._current_card.card_number_masked 
                      if self._current_card else "****")
        self._end_session()
        return f"Card {card_masked} ejected. Thank you for using our ATM."
    
    def _retain_card(self, reason: str) -> None:
        """Retain the card (for security reasons)."""
        if self._current_card:
            self._current_card.block(reason)
            card_num = self._current_card.card_number
            self._end_session()
            raise CardRetainedError(card_num, reason)


# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

def main():
    """Main demonstration of the Banking/ATM System."""
    
    print("=" * 60)
    print("   BANKING/ATM SYSTEM - OOP DEMONSTRATION")
    print("=" * 60)
    
    # =========================================================================
    # 1. SINGLETON PATTERN - Bank Registry
    # =========================================================================
    print("\n" + "=" * 60)
    print("1. SINGLETON PATTERN - Bank Registry")
    print("=" * 60)
    
    registry1 = BankRegistry()
    registry2 = BankRegistry()
    
    print(f"Registry 1 ID: {id(registry1)}")
    print(f"Registry 2 ID: {id(registry2)}")
    print(f"Same instance: {registry1 is registry2}")
    
    # =========================================================================
    # 2. CUSTOMER HIERARCHY (Polymorphism)
    # =========================================================================
    print("\n" + "=" * 60)
    print("2. CUSTOMER HIERARCHY - Inheritance & Polymorphism")
    print("=" * 60)
    
    # Create different customer types
    individual = IndividualCustomer(
        customer_id="CUST001",
        name="John Smith",
        email="john.smith@email.com",
        phone="555-0101",
        address="123 Main St",
        date_of_birth=date(1985, 5, 15),
        ssn_last4="1234"
    )
    
    business = BusinessCustomer(
        customer_id="CUST002",
        name="Jane Doe",
        email="jane@techcorp.com",
        phone="555-0102",
        address="456 Business Ave",
        business_name="TechCorp LLC",
        tax_id="12-3456789",
        business_type="Technology"
    )
    
    vip = VIPCustomer(
        customer_id="CUST003",
        name="Robert Wilson",
        email="robert.wilson@email.com",
        phone="555-0103",
        address="789 Luxury Lane",
        relationship_manager="Sarah Manager",
        vip_tier="Platinum"
    )
    
    # Register customers
    registry1.register_customer(individual)
    registry1.register_customer(business)
    registry1.register_customer(vip)
    
    # Demonstrate polymorphism
    customers = [individual, business, vip]
    print("\nCustomer Types and Limits (Polymorphism):")
    print("-" * 50)
    for customer in customers:
        print(f"  {customer}")
        print(f"    - Daily Withdrawal Limit: ${customer.get_daily_withdrawal_limit():,.2f}")
        print(f"    - Fee Waiver: {customer.get_transaction_fee_waiver()}")
        print(f"    - Overdraft Limit: ${customer.get_overdraft_limit():,.2f}")
    
    # =========================================================================
    # 3. FACTORY PATTERN - Account Creation
    # =========================================================================
    print("\n" + "=" * 60)
    print("3. FACTORY PATTERN - Account Creation")
    print("=" * 60)
    
    # Create accounts using factory
    savings = AccountFactory.create_account(
        AccountType.SAVINGS,
        "CUST001",
        1000.0
    )
    
    checking = AccountFactory.create_account(
        AccountType.CHECKING,
        "CUST001",
        500.0,
        overdraft_protection=True,
        linked_savings=savings.account_number
    )
    
    money_market = AccountFactory.create_account(
        AccountType.MONEY_MARKET,
        "CUST002",
        5000.0
    )
    
    cd = AccountFactory.create_account(
        AccountType.CERTIFICATE_OF_DEPOSIT,
        "CUST003",
        10000.0,
        term_months=24
    )
    
    # Register accounts
    for account in [savings, checking, money_market, cd]:
        registry1.register_account(account)
        print(f"Created: {account}")
    
    # =========================================================================
    # 4. ACCOUNT HIERARCHY - Interest Rates (Polymorphism)
    # =========================================================================
    print("\n" + "=" * 60)
    print("4. ACCOUNT HIERARCHY - Interest Bearing Interface")
    print("=" * 60)
    
    accounts = [savings, checking, money_market, cd]
    print("\nInterest Rates (Polymorphism):")
    print("-" * 50)
    for account in accounts:
        print(f"  {account.get_account_type().name}:")
        print(f"    - APY: {account.get_apy() * 100:.2f}%")
        print(f"    - Minimum Balance: ${account.get_minimum_balance():,.2f}")
        print(f"    - Monthly Withdrawal Limit: {account.get_monthly_withdrawal_limit() or 'Unlimited'}")
    
    # =========================================================================
    # 5. TRANSACTION OPERATIONS
    # =========================================================================
    print("\n" + "=" * 60)
    print("5. TRANSACTION OPERATIONS")
    print("=" * 60)
    
    print("\n--- Deposit ---")
    deposit_txn = TransactionFactory.create_deposit(500.0, savings, "Paycheck deposit")
    deposit_txn.execute()
    print(f"Deposited $500 to {savings.account_number}")
    print(f"New balance: ${savings.balance:,.2f}")
    
    print("\n--- Withdrawal ---")
    withdrawal_txn = TransactionFactory.create_withdrawal(
        200.0, checking, individual.get_daily_withdrawal_limit()
    )
    withdrawal_txn.execute()
    print(f"Withdrew $200 from {checking.account_number}")
    print(f"New balance: ${checking.balance:,.2f}")
    
    print("\n--- Transfer ---")
    transfer_txn = TransactionFactory.create_transfer(
        100.0, savings, checking, "Moving funds"
    )
    transfer_txn.execute()
    print(f"Transferred $100 from {savings.account_number} to {checking.account_number}")
    print(f"Savings balance: ${savings.balance:,.2f}")
    print(f"Checking balance: ${checking.balance:,.2f}")
    
    # =========================================================================
    # 6. OBSERVER PATTERN - Notifications
    # =========================================================================
    print("\n" + "=" * 60)
    print("6. OBSERVER PATTERN - Transaction Notifications")
    print("=" * 60)
    
    print("\nTriggering a large transaction (>$10,000):")
    large_deposit = TransactionFactory.create_deposit(
        15000.0, money_market, "Large investment deposit"
    )
    large_deposit.execute()
    
    print("\nTriggering low balance alert:")
    # Withdraw to trigger low balance
    small_account = AccountFactory.create_account(
        AccountType.SAVINGS,
        "CUST001",
        150.0
    )
    registry1.register_account(small_account)
    withdrawal_small = TransactionFactory.create_withdrawal(
        100.0, small_account, 500.0
    )
    withdrawal_small.execute()
    
    # =========================================================================
    # 7. CUSTOM EXCEPTIONS
    # =========================================================================
    print("\n" + "=" * 60)
    print("7. CUSTOM EXCEPTION HANDLING")
    print("=" * 60)
    
    print("\n--- Insufficient Funds ---")
    try:
        bad_withdrawal = TransactionFactory.create_withdrawal(
            10000.0, checking, 500.0
        )
        bad_withdrawal.execute()
    except InsufficientFundsError as e:
        print(f"  Caught: {e.message}")
        print(f"  Details: {e.details}")
    
    print("\n--- Minimum Balance Violation ---")
    try:
        low_savings = AccountFactory.create_account(
            AccountType.SAVINGS, "CUST001", 200.0
        )
        registry1.register_account(low_savings)
        low_savings.withdraw(150.0)
    except MinimumBalanceViolationError as e:
        print(f"  Caught: {e.message}")
    
    print("\n--- Transfer to Same Account ---")
    try:
        TransactionFactory.create_transfer(100.0, savings, savings)
    except TransferToSameAccountError as e:
        print(f"  Caught: {e.message}")
    
    print("\n--- Account Not Found ---")
    try:
        registry1.get_account("INVALID123")
    except AccountNotFoundError as e:
        print(f"  Caught: {e.message}")
    
    # =========================================================================
    # 8. CARD HIERARCHY
    # =========================================================================
    print("\n" + "=" * 60)
    print("8. CARD HIERARCHY")
    print("=" * 60)
    
    # Create cards using factory
    debit_card = CardFactory.create_card(
        "debit",
        savings.account_number,
        "CUST001"
    )
    debit_card.set_pin("1234")
    
    credit_card = CardFactory.create_card(
        "credit",
        checking.account_number,
        "CUST001",
        credit_limit=10000.0
    )
    credit_card.set_pin("5678")
    
    prepaid_card = CardFactory.create_card(
        "prepaid",
        savings.account_number,
        "CUST001",
        loaded_amount=500.0
    )
    prepaid_card.set_pin("9012")
    
    registry1.register_card(debit_card)
    registry1.register_card(credit_card)
    registry1.register_card(prepaid_card)
    
    print("\nCards Created:")
    for card in [debit_card, credit_card, prepaid_card]:
        print(f"  {card.get_card_type()} Card: {card.card_number_masked}")
        print(f"    - Daily Limit: ${card.get_daily_limit():,.2f}")
    
    # =========================================================================
    # 9. ATM SIMULATION
    # =========================================================================
    print("\n" + "=" * 60)
    print("9. ATM SIMULATION")
    print("=" * 60)
    
    # Create and register ATM
    atm = ATM("ATM001", "Main Street Branch", 50000.0)
    registry1.register_atm(atm)
    
    print(f"\nATM: {atm.atm_id} at {atm.location}")
    print(f"Cash Available: ${atm.cash_available:,.2f}")
    
    # Full ATM session
    print("\n--- ATM Session ---")
    try:
        # Insert card
        print(atm.insert_card(debit_card))
        
        # Enter PIN
        print(atm.enter_pin("1234"))
        
        # Check balance
        print(atm.check_balance())
        
        # Withdraw cash
        print(atm.withdraw(200.0))
        
        # Get mini statement
        print(atm.get_mini_statement())
        
        # End session
        print(atm.eject_card())
        
    except BankingException as e:
        print(f"ATM Error: {e.message}")
    
    # =========================================================================
    # 10. ADAPTER PATTERN - Legacy Data Import
    # =========================================================================
    print("\n" + "=" * 60)
    print("10. ADAPTER PATTERN - Legacy Data Import")
    print("=" * 60)
    
    # Create legacy account data
    legacy_data = LegacyAccountData(
        acct_num="SAV-00012345",
        cust_name="Legacy Customer",
        cust_ssn="123-45-6789",
        balance_cents=2500000,  # $25,000.00
        acct_status="A",
        open_date="05152020",
        interest_rate_bps=50  # 0.50%
    )
    
    print("\nLegacy Data:")
    print(f"  Account: {legacy_data.acct_num}")
    print(f"  Balance: {legacy_data.balance_cents} cents")
    print(f"  Status: {legacy_data.acct_status}")
    print(f"  Open Date: {legacy_data.open_date}")
    print(f"  Interest: {legacy_data.interest_rate_bps} bps")
    
    # Convert using adapter
    converted = LegacyBankingAdapter.import_legacy_account(legacy_data, "LEGACY001")
    
    print("\nConverted Data:")
    print(f"  Account Type: {converted['account_type'].name}")
    print(f"  Account Number: {converted['account_number']}")
    print(f"  Balance: ${converted['balance']:,.2f}")
    print(f"  Active: {converted['is_active']}")
    print(f"  Open Date: {converted['open_date']}")
    print(f"  Interest Rate: {converted['interest_rate'] * 100:.2f}%")
    print(f"  SSN (masked): ***-**-{converted['ssn_last4']}")
    
    # =========================================================================
    # 11. PIN AUTHENTICATION - Security
    # =========================================================================
    print("\n" + "=" * 60)
    print("11. PIN AUTHENTICATION & SECURITY")
    print("=" * 60)
    
    test_card = CardFactory.create_card(
        "debit",
        savings.account_number,
        "CUST001"
    )
    test_card.set_pin("1111")
    
    print("\nAttempting invalid PINs:")
    for attempt in range(1, 4):
        try:
            test_card.validate_pin("9999")  # Wrong PIN
        except InvalidPINError as e:
            print(f"  Attempt {attempt}: {e.message}")
        except CardBlockedError as e:
            print(f"  Attempt {attempt}: {e.message}")
    
    print(f"\nCard Status: {test_card.status.name}")
    
    # =========================================================================
    # 12. AUDIT TRAIL
    # =========================================================================
    print("\n" + "=" * 60)
    print("12. AUDIT TRAIL (Auditable Interface)")
    print("=" * 60)
    
    audit_trail = savings.get_audit_trail()
    print(f"\nAudit Trail for {savings.account_number}:")
    print("-" * 50)
    for entry in audit_trail[-5:]:  # Last 5 entries
        print(f"  {entry['timestamp'][:19]} | {entry['action']}")
    
    # =========================================================================
    # 13. ACCOUNT STATEMENT
    # =========================================================================
    print("\n" + "=" * 60)
    print("13. ACCOUNT STATEMENT (Auditable Interface)")
    print("=" * 60)
    
    today = date.today()
    start = today - timedelta(days=30)
    
    print(savings.generate_report(start, today))
    
    # =========================================================================
    # 14. CERTIFICATE OF DEPOSIT - Special Rules
    # =========================================================================
    print("\n" + "=" * 60)
    print("14. CERTIFICATE OF DEPOSIT - Business Rules")
    print("=" * 60)
    
    print(f"\nCD Account: {cd.account_number}")
    print(f"Term: {cd.term_months} months")
    print(f"APY: {cd.get_apy() * 100:.2f}%")
    print(f"Maturity Date: {cd.maturity_date.date()}")
    print(f"Is Mature: {cd.is_mature()}")
    print(f"Balance: ${cd.balance:,.2f}")
    
    print("\nAttempting early withdrawal (incurs 90-day interest penalty):")
    try:
        cd.withdraw(1000.0)
        print(f"Withdrew $1000 with penalty applied")
        print(f"New Balance: ${cd.balance:,.2f}")
    except BankingException as e:
        print(f"Error: {e.message}")
    
    # =========================================================================
    # 15. REGISTRY STATISTICS
    # =========================================================================
    print("\n" + "=" * 60)
    print("15. REGISTRY STATISTICS")
    print("=" * 60)
    
    stats = registry1.get_statistics()
    print("\nBank Registry Summary:")
    print("-" * 40)
    print(f"  Total Customers: {stats['total_customers']}")
    print(f"  Total Accounts: {stats['total_accounts']}")
    print(f"  Total Cards: {stats['total_cards']}")
    print(f"  Total Transactions: {stats['total_transactions']}")
    print(f"  ATMs: {stats['total_atms']}")
    print(f"\n  Accounts by Type:")
    for acc_type, count in stats['accounts_by_type'].items():
        print(f"    - {acc_type}: {count}")
    print(f"\n  Customers by Type:")
    for cust_type, count in stats['customers_by_type'].items():
        print(f"    - {cust_type}: {count}")
    print(f"\n  Low Balance Alerts: {stats['low_balance_accounts']}")
    print(f"  Fraud Alerts: {stats['fraud_alerts']}")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("   OOP CONCEPTS DEMONSTRATED")
    print("=" * 60)
    print("""
    ✓ Encapsulation
      - Private attributes (_balance, _pin_hash)
      - Properties with validation
      - Protected sensitive data
    
    ✓ Inheritance
      - Customer hierarchy (Individual, Joint, Business, VIP)
      - Account hierarchy (Savings, Checking, MoneyMarket, CD)
      - Transaction hierarchy (Deposit, Withdrawal, Transfer)
      - Card hierarchy (Debit, Credit, Prepaid)
    
    ✓ Polymorphism
      - get_daily_withdrawal_limit() varies by customer type
      - get_apy() varies by account type
      - get_daily_limit() varies by card type
    
    ✓ Abstraction
      - Transactable interface (execute, validate, rollback)
      - InterestBearing interface (calculate_interest, apply_interest)
      - Observable interface (add_observer, notify_observers)
      - Auditable interface (log_action, get_audit_trail)
    
    ✓ Factory Pattern
      - AccountFactory.create_account()
      - TransactionFactory.create_transfer()
      - CardFactory.create_card()
    
    ✓ Adapter Pattern
      - LegacyBankingAdapter converts legacy data formats
    
    ✓ Observer Pattern
      - FraudDetectionObserver, CustomerNotificationObserver
      - AuditLogObserver, BalanceMonitorObserver
    
    ✓ Singleton Pattern
      - BankRegistry using SingletonMeta metaclass
    
    ✓ Custom Exceptions
      - Full hierarchy from BankingException
      - Specific exceptions with context data
    """)
    
    print("=" * 60)
    print("   DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
