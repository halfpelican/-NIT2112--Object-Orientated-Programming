"""Budget and transaction models for club financial management."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field

from constants import TransactionType
from exceptions import InsufficientFundsError
# =============================================================================
# FINANCIAL MANAGEMENT
# =============================================================================


@dataclass
class Transaction:
    """Represents a financial transaction."""
    transaction_id: str
    transaction_type: str
    amount: float
    description: str
    timestamp: datetime
    related_event: Optional[str] = None
    balance_after: float = 0.0


class Budget:
    """Manages club budget and transactions."""
    
    def __init__(self, initial_allocation: float = 0.0, overdraft_limit: float = 0.0):
        """Initialise a new Budget instance."""
        self._balance = initial_allocation
        self._overdraft_limit = overdraft_limit
        self._transactions: List[Transaction] = []
        self._reserved: Dict[str, float] = {}  # event_id -> reserved amount
        self._transaction_counter = 0
        
        if initial_allocation > 0:
            self._record_transaction(
                TransactionType._ALLOCATION,
                initial_allocation,
                "Initial budget allocation"
            )
    
    @property
    def balance(self) -> float:
        """Execute balance."""
        return self._balance
    
    @property
    def available_balance(self) -> float:
        """Balance minus reservations."""
        return self._balance - sum(self._reserved.values())
    
    @property
    def total_reserved(self) -> float:
        """Execute total reserved."""
        return sum(self._reserved.values())
    
    @property
    def transactions(self) -> List[Transaction]:
        """Execute transactions."""
        return self._transactions.copy()
    
    def _generate_transaction_id(self) -> str:
        """Generate transaction id."""
        self._transaction_counter += 1
        return f"TXN{self._transaction_counter:05d}"
    
    def _record_transaction(
        self,
        txn_type: str,
        amount: float,
        description: str,
        event_id: str = None
    ) -> Transaction:
        """Record transaction."""
        txn = Transaction(
            transaction_id=self._generate_transaction_id(),
            transaction_type=txn_type,
            amount=amount,
            description=description,
            timestamp=datetime.now(),
            related_event=event_id,
            balance_after=self._balance
        )
        self._transactions.append(txn)
        return txn
    
    def can_afford(self, amount: float) -> bool:
        """Check if amount can be afforded."""
        return amount <= self.available_balance + self._overdraft_limit
    
    def reserve_funds(self, event_id: str, amount: float) -> None:
        """Reserve funds for an event."""
        if not self.can_afford(amount):
            raise InsufficientFundsError(amount, self.available_balance, f"reserve for event {event_id}")
        
        self._reserved[event_id] = amount
        self._record_transaction(
            TransactionType._RESERVATION,
            amount,
            f"Funds reserved for event",
            event_id
        )
    
    def release_reservation(self, event_id: str) -> float:
        """Release reserved funds. Returns amount released."""
        amount = self._reserved.pop(event_id, 0.0)
        if amount > 0:
            self._record_transaction(
                TransactionType._REFUND,
                amount,
                f"Reservation released",
                event_id
            )
        return amount
    
    def spend(self, event_id: str, amount: float, description: str = "") -> None:
        """Spend reserved funds."""
        if event_id in self._reserved:
            # Use reservation
            reserved = self._reserved.pop(event_id)
            self._balance -= amount
            if amount < reserved:
                # Refund difference
                self._balance += (reserved - amount)
        else:
            if amount > self.available_balance + self._overdraft_limit:
                raise InsufficientFundsError(amount, self.available_balance, description)
            self._balance -= amount
        
        self._record_transaction(
            TransactionType._EXPENSE,
            amount,
            description or f"Expense for event",
            event_id
        )
    
    def add_revenue(self, amount: float, description: str, event_id: str = None) -> None:
        """Add revenue to budget."""
        self._balance += amount
        self._record_transaction(
            TransactionType._REVENUE,
            amount,
            description,
            event_id
        )
    
    def add_allocation(self, amount: float, description: str = "Budget allocation") -> None:
        """Add budget allocation."""
        self._balance += amount
        self._record_transaction(
            TransactionType._ALLOCATION,
            amount,
            description
        )
    
    def apply_cancellation_fee(self, event_id: str, fee: float) -> None:
        """Apply cancellation fee."""
        self.release_reservation(event_id)
        if fee > 0:
            self._balance -= fee
            self._record_transaction(
                TransactionType._CANCELLATION_FEE,
                fee,
                f"Cancellation fee",
                event_id
            )
    
    def get_financial_report(self) -> str:
        """Generate a financial report."""
        lines = [
            "=" * 50,
            "FINANCIAL REPORT",
            "=" * 50,
            f"Current Balance: ${self._balance:.2f}",
            f"Reserved Funds: ${self.total_reserved:.2f}",
            f"Available: ${self.available_balance:.2f}",
            f"Overdraft Limit: ${self._overdraft_limit:.2f}",
            "",
            "Recent Transactions:",
            "-" * 50
        ]
        
        for txn in self._transactions[-10:]:
            lines.append(
                f"  {txn.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                f"{txn.transaction_type:15} | "
                f"${txn.amount:>10.2f} | {txn.description[:20]}"
            )
        
        return "\n".join(lines)

