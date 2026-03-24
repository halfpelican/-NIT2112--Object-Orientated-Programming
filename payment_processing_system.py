from abc import ABC, abstractmethod

class PaymentProcesser(ABC):
    @abstractmethod
    def authorise_payment(self, amount):
        pass

    @abstractmethod    
    def execute_payment(self, amount):
        pass

class CreditCardProcessor(PaymentProcesser):
    def authorise_payment(self, amount):
        print(f"Authorising credit card payment of ${amount}")

    def execute_payment(self, amount):
        print(f"Executing credit card payment of ${amount}")

class PayPalProcessor(PaymentProcesser):
    def authorise_payment(self, amount):
        print(f"Authorising PayPal payment of ${amount}")

    def execute_payment(self, amount):
        print(f"Executing PayPal payment of ${amount}")

def process_order(payment_processor, amount):
    payment_processor.authorise_payment(amount)
    payment_processor.execute_payment(amount)

credit_card_processor = CreditCardProcessor()
paypal_processor = PayPalProcessor()

process_order(credit_card_processor, 100)
process_order(paypal_processor, 50)