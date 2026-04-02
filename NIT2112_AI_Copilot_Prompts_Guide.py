"""
Generate PDF: AI Copilot Prompts Guide for NIT2112 OOP Practical Assessments
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

def create_pdf():
    doc = SimpleDocTemplate(
        "NIT2112_AI_Copilot_Prompts_Guide.pdf",
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=13,
        spaceAfter=8,
        spaceBefore=14,
        textColor=colors.darkgreen
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=11,
        spaceAfter=6,
        spaceBefore=10,
        textColor=colors.darkcyan
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    prompt_style = ParagraphStyle(
        'PromptStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        spaceBefore=4,
        leftIndent=20,
        backColor=colors.Color(0.95, 0.95, 1.0),
        borderPadding=8,
        fontName='Courier'
    )
    
    example_style = ParagraphStyle(
        'ExampleStyle',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=6,
        leftIndent=30,
        textColor=colors.darkslategray,
        fontName='Courier'
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        leftIndent=20,
        bulletIndent=10
    )
    
    story = []
    
    # Title
    story.append(Paragraph("NIT2112 AI Copilot Prompts Guide", title_style))
    story.append(Paragraph("Effective Prompts for OOP Practical Assessments", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Introduction
    story.append(Paragraph("Introduction", heading1_style))
    story.append(Paragraph(
        """This guide provides a comprehensive collection of AI Copilot prompts for completing 
        NIT2112 Object-Oriented Programming practical assessments. It includes example prompts 
        from the lab materials and additional generated prompts organised by OOP concept and 
        development phase.""",
        normal_style
    ))
    story.append(Spacer(1, 10))
    
    # Important Note
    story.append(Paragraph(
        """<b>Important:</b> Using AI Copilots effectively means asking targeted questions, 
        critically evaluating responses, and adapting suggestions to your specific design. 
        Never blindly copy AI-generated code without understanding it.""",
        normal_style
    ))
    
    story.append(Spacer(1, 20))
    
    # ==========================================================================
    # SECTION 1: EXAMPLE PROMPTS FROM LAB MATERIALS
    # ==========================================================================
    story.append(Paragraph("Section 1: Example Prompts from Lab Materials", heading1_style))
    
    # Lab 10 Examples
    story.append(Paragraph("1.1 Documentation Prompts (from Lab 10)", heading2_style))
    
    doc_prompts = [
        ("Docstring Generation", 
         '"Generate a detailed Python docstring for this method using Google style format. Include descriptions for parameters (Args), return values (Returns), and any custom exceptions it might raise (Raises)."'),
        ("Code Comments", 
         '"Add explanatory code comments to this Python code block to clarify the logic, especially the purpose of different checks or error handling."'),
        ("System Summary", 
         '"Write a short summary describing the purpose and relationships between the main classes (Person, Student, Teacher, Unit, EnrollmentSystem, SchoolRegistry) in my Python school simulator project."'),
        ("Interaction Explanation", 
         '"Explain, in plain English, the steps involved when a student enrolls in a unit using the EnrollmentSystem, mentioning the roles of the Registry and the Unit class."'),
        ("Diagram Generation", 
         '"Generate PlantUML (or Mermaid) syntax for a simple class diagram. It should show that Student and Teacher inherit from an abstract Person class. It should also show an association relationship between Student and Unit."'),
        ("README Draft", 
         '"Generate a draft README.md file for my Python project. Include sections for: Project Title, Description, Features, Getting Started, Main Classes, and How to Run Tests."'),
    ]
    
    for title, prompt in doc_prompts:
        story.append(Paragraph(f"<b>{title}:</b>", normal_style))
        story.append(Paragraph(prompt, prompt_style))
        story.append(Spacer(1, 4))
    
    # Practical Assessment Examples
    story.append(Paragraph("1.2 Practical Assessment Prompts (Good Examples)", heading2_style))
    
    assessment_prompts = [
        ("Design Trade-offs", 
         '"What are the trade-offs between using composition vs inheritance for my Zone classes?"'),
        ("Pattern Implementation", 
         '"Help me implement an Observer pattern for low-stock alerts where products notify subscribed managers."'),
        ("Refactoring", 
         '"How can I refactor this code to better follow the Single Responsibility Principle?"'),
        ("Debugging Polymorphism", 
         '"Why might my polymorphic is_shippable() method not be called on PerishableProduct?"'),
        ("Ticket Validation", 
         '"Why is my EarlyBirdTicket validation not correctly checking the 30-day rule?"'),
    ]
    
    for title, prompt in assessment_prompts:
        story.append(Paragraph(f"<b>{title}:</b>", normal_style))
        story.append(Paragraph(prompt, prompt_style))
        story.append(Spacer(1, 4))
    
    # Poor Examples (what to avoid)
    story.append(Paragraph("1.3 Poor AI Usage Examples (What to Avoid)", heading2_style))
    
    poor_examples = [
        ("Wholesale Delegation", '"Write the entire warehouse system for me"', 
         "Too broad; shows no understanding of requirements"),
        ("No Critical Thinking", "Accepting generated code without understanding or testing it",
         "Must always evaluate and adapt AI suggestions"),
        ("No Documentation", "Using AI but not recording how it influenced your solution",
         "AI interactions must be documented for assessment"),
        ("Ignoring Context", "Pasting AI code that doesn't integrate with your design",
         "AI suggestions must fit your architecture"),
    ]
    
    for issue, example, reason in poor_examples:
        story.append(Paragraph(f"<b>❌ {issue}:</b>", normal_style))
        story.append(Paragraph(f'"{example}"', example_style))
        story.append(Paragraph(f"<i>Why it's poor: {reason}</i>", bullet_style))
        story.append(Spacer(1, 4))
    
    story.append(PageBreak())
    
    # ==========================================================================
    # SECTION 2: DESIGN PHASE PROMPTS
    # ==========================================================================
    story.append(Paragraph("Section 2: Design Phase Prompts", heading1_style))
    
    story.append(Paragraph("2.1 Understanding Requirements", heading2_style))
    
    design_prompts_1 = [
        '"Help me break down these business requirements into potential classes and their responsibilities."',
        '"What entities should I model for a [domain] system? List the key nouns that could become classes."',
        '"Looking at these requirements, which relationships should be composition vs aggregation?"',
        '"What are the main actors and objects in this system? How do they interact?"',
        '"Help me identify the core abstractions needed for this problem domain."',
    ]
    
    for prompt in design_prompts_1:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("2.2 Class Hierarchy Design", heading2_style))
    
    design_prompts_2 = [
        '"Should I use inheritance or composition for the relationship between [ClassA] and [ClassB]? What are the trade-offs?"',
        '"I have three types of [Entity]: Type1, Type2, and Type3. How should I structure the inheritance hierarchy?"',
        '"What common attributes and methods should go in my base [Entity] class vs the subclasses?"',
        '"Is this a good candidate for an abstract base class, or should it be a concrete class?"',
        '"How deep should my inheritance hierarchy be? I currently have 4 levels."',
        '"What\'s the difference between using ABC vs Protocol for defining interfaces in Python?"',
    ]
    
    for prompt in design_prompts_2:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("2.3 Design Pattern Selection", heading2_style))
    
    design_prompts_3 = [
        '"Which design pattern would be best for creating different types of [Entity] based on configuration?"',
        '"I need to notify multiple objects when [Event] occurs. Which pattern should I use?"',
        '"I have legacy data in format X and need to convert it to format Y. Is the Adapter pattern appropriate?"',
        '"How do I ensure only one instance of my [Registry/Manager] class exists? Show me the Singleton pattern in Python."',
        '"Should I use Factory Method or Abstract Factory for creating my product hierarchy?"',
        '"I need to add functionality to objects at runtime without modifying them. Which pattern fits?"',
    ]
    
    for prompt in design_prompts_3:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(PageBreak())
    
    # ==========================================================================
    # SECTION 3: IMPLEMENTATION PHASE PROMPTS
    # ==========================================================================
    story.append(Paragraph("Section 3: Implementation Phase Prompts", heading1_style))
    
    story.append(Paragraph("3.1 Encapsulation", heading2_style))
    
    impl_prompts_1 = [
        '"How do I implement private attributes with property getters and setters in Python?"',
        '"Show me how to add validation to a property setter that ensures [condition]."',
        '"What\'s the Python convention for protected vs private attributes? When should I use each?"',
        '"How do I make an attribute read-only after initialization?"',
        '"Should this be a property or a method? It requires some calculation."',
    ]
    
    for prompt in impl_prompts_1:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("3.2 Abstract Base Classes & Interfaces", heading2_style))
    
    impl_prompts_2 = [
        '"Show me how to define an abstract base class with abstract methods using Python\'s abc module."',
        '"How do I create an interface-like class that defines a contract for [Behavior]?"',
        '"Can a class implement multiple interfaces in Python? Show me an example."',
        '"When should I use @abstractmethod vs @abstractproperty?"',
        '"How do I enforce that subclasses implement certain methods?"',
    ]
    
    for prompt in impl_prompts_2:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("3.3 Polymorphism", heading2_style))
    
    impl_prompts_3 = [
        '"Help me implement polymorphic behavior where each [Entity] type calculates [value] differently."',
        '"Show me how to override a method in a subclass while still calling the parent\'s implementation."',
        '"How do I use duck typing effectively in Python for polymorphism?"',
        '"What\'s the difference between method overriding and method overloading in Python?"',
        '"How do I implement __str__ and __repr__ methods that are polymorphic across my hierarchy?"',
    ]
    
    for prompt in impl_prompts_3:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("3.4 Factory Pattern Implementation", heading2_style))
    
    impl_prompts_4 = [
        '"Show me how to implement a Factory class that creates different [Entity] types based on a type string."',
        '"How do I add validation in my factory to ensure required parameters are provided?"',
        '"Should my factory use class methods or static methods?"',
        '"How do I extend my factory to support new product types without modifying existing code?"',
        '"What\'s the best way to handle invalid type parameters in a factory?"',
    ]
    
    for prompt in impl_prompts_4:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("3.5 Observer Pattern Implementation", heading2_style))
    
    impl_prompts_5 = [
        '"Help me implement the Observer pattern where [Subject] notifies [Observers] when [Event] occurs."',
        '"How do I manage multiple types of notifications (e.g., email, SMS, dashboard) using Observer?"',
        '"Show me how to implement add_observer, remove_observer, and notify_observers methods."',
        '"How do I pass different types of data to observers depending on the event type?"',
        '"Should observers pull data from the subject or should the subject push data to observers?"',
    ]
    
    for prompt in impl_prompts_5:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("3.6 Adapter Pattern Implementation", heading2_style))
    
    impl_prompts_6 = [
        '"How do I create an Adapter class to convert legacy data format to my new system\'s format?"',
        '"Show me how to adapt a class with interface X to work with interface Y."',
        '"What\'s the difference between object adapter and class adapter patterns?"',
        '"How do I handle data type conversions (e.g., cents to dollars, grams to kg) in an adapter?"',
        '"My legacy system uses different field names. How do I map them in the adapter?"',
    ]
    
    for prompt in impl_prompts_6:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("3.7 Singleton Pattern Implementation", heading2_style))
    
    impl_prompts_7 = [
        '"Show me how to implement the Singleton pattern in Python using a metaclass."',
        '"What are the different ways to implement Singleton in Python and their trade-offs?"',
        '"How do I make my [Registry] class a Singleton to ensure only one instance exists?"',
        '"Is there a way to reset a Singleton for testing purposes?"',
        '"How do I handle thread safety with the Singleton pattern in Python?"',
    ]
    
    for prompt in impl_prompts_7:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(PageBreak())
    
    # ==========================================================================
    # SECTION 4: EXCEPTION HANDLING PROMPTS
    # ==========================================================================
    story.append(Paragraph("Section 4: Exception Handling Prompts", heading1_style))
    
    story.append(Paragraph("4.1 Custom Exception Design", heading2_style))
    
    exc_prompts_1 = [
        '"Help me design a custom exception hierarchy for my [Domain] system."',
        '"What exceptions should I define for handling [specific business rules]?"',
        '"How do I add context information (like entity IDs) to my custom exceptions?"',
        '"Should I have separate exceptions for validation errors vs business rule violations?"',
        '"Show me how to create a base exception class that all my domain exceptions inherit from."',
    ]
    
    for prompt in exc_prompts_1:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("4.2 Exception Implementation", heading2_style))
    
    exc_prompts_2 = [
        '"How do I implement a custom exception with additional attributes like error_code and details?"',
        '"Show me how to chain exceptions in Python to preserve the original error context."',
        '"When should I raise an exception vs return an error code or None?"',
        '"How do I write informative exception messages that help with debugging?"',
        '"What\'s the best practice for documenting exceptions in docstrings?"',
    ]
    
    for prompt in exc_prompts_2:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Spacer(1, 20))
    
    # ==========================================================================
    # SECTION 5: DEBUGGING PROMPTS
    # ==========================================================================
    story.append(Paragraph("Section 5: Debugging Prompts", heading1_style))
    
    story.append(Paragraph("5.1 Common OOP Issues", heading2_style))
    
    debug_prompts_1 = [
        '"Why is my abstract method not being called on the subclass?"',
        '"My isinstance() check is returning False when I expect True. What could cause this?"',
        '"Why is my property setter not being called when I assign a value?"',
        '"My Observer is not receiving notifications. How do I debug this?"',
        '"The Singleton is creating multiple instances. What\'s wrong with my implementation?"',
    ]
    
    for prompt in debug_prompts_1:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("5.2 Debugging Specific Patterns", heading2_style))
    
    debug_prompts_2 = [
        '"My factory is returning None instead of the created object. Why?"',
        '"The adapter is not converting the data correctly. Here\'s my code: [paste code]"',
        '"Why is super().__init__() not calling the parent constructor as expected?"',
        '"My method override is not being recognized. Is there something wrong with the signature?"',
        '"How do I trace method resolution order (MRO) issues in my class hierarchy?"',
    ]
    
    for prompt in debug_prompts_2:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("5.3 Logic Errors", heading2_style))
    
    debug_prompts_3 = [
        '"My validation is passing when it should fail. Here\'s the condition: [paste code]"',
        '"The calculation in my [method] is returning wrong values. Can you spot the error?"',
        '"Why is my loop not iterating over all items in the collection?"',
        '"My date comparison is not working correctly. What\'s wrong?"',
        '"The discount is being applied incorrectly. Here\'s my pricing logic: [paste code]"',
    ]
    
    for prompt in debug_prompts_3:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(PageBreak())
    
    # ==========================================================================
    # SECTION 6: REFACTORING PROMPTS
    # ==========================================================================
    story.append(Paragraph("Section 6: Refactoring Prompts", heading1_style))
    
    story.append(Paragraph("6.1 Code Quality Improvements", heading2_style))
    
    refactor_prompts_1 = [
        '"How can I refactor this long method into smaller, more focused methods?"',
        '"This class has too many responsibilities. How should I split it?"',
        '"How do I refactor duplicate code in these two classes into a shared base class?"',
        '"What\'s a cleaner way to handle these multiple if-elif conditions?"',
        '"How can I make this code more Pythonic?"',
    ]
    
    for prompt in refactor_prompts_1:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("6.2 SOLID Principles", heading2_style))
    
    refactor_prompts_2 = [
        '"How can I refactor this code to follow the Single Responsibility Principle?"',
        '"My class is violating the Open/Closed Principle. How do I fix it?"',
        '"Is this a Liskov Substitution Principle violation? How should I restructure?"',
        '"How do I apply the Interface Segregation Principle to this large interface?"',
        '"Help me apply Dependency Inversion to reduce coupling between these classes."',
    ]
    
    for prompt in refactor_prompts_2:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Spacer(1, 20))
    
    # ==========================================================================
    # SECTION 7: DOMAIN-SPECIFIC PROMPTS
    # ==========================================================================
    story.append(Paragraph("Section 7: Domain-Specific Prompts", heading1_style))
    
    story.append(Paragraph("7.1 Warehouse/Inventory Systems", heading2_style))
    
    domain_prompts_1 = [
        '"How should I model different product types (standard, perishable, hazardous) in a warehouse system?"',
        '"What\'s the best way to implement stock level tracking with low-stock alerts?"',
        '"How do I handle product expiry dates and prevent shipping of expired items?"',
        '"Show me how to implement zone-based storage with capacity limits."',
        '"How should I design order fulfillment that deducts stock from multiple zones?"',
    ]
    
    for prompt in domain_prompts_1:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("7.2 Event Management Systems", heading2_style))
    
    domain_prompts_2 = [
        '"How do I model different event types (conference, workshop, webinar) with their specific rules?"',
        '"What\'s the best approach for implementing tiered ticket pricing (standard, VIP, early bird)?"',
        '"How should I handle event capacity and waitlist management?"',
        '"Show me how to implement registration with duplicate email prevention."',
        '"How do I calculate ticket prices with various discounts and multipliers?"',
    ]
    
    for prompt in domain_prompts_2:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("7.3 Healthcare/Clinic Systems", heading2_style))
    
    domain_prompts_3 = [
        '"How should I model patient types (outpatient, inpatient, emergency) with different billing rules?"',
        '"What\'s the best way to implement appointment scheduling with slot validation?"',
        '"How do I handle medical record access control and privacy?"',
        '"Show me how to implement insurance calculation and coverage rules."',
        '"How should I design prescription tracking with medication interaction checks?"',
    ]
    
    for prompt in domain_prompts_3:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("7.4 Booking/Reservation Systems", heading2_style))
    
    domain_prompts_4 = [
        '"How do I model room types with seasonal pricing variations?"',
        '"What\'s the best approach for implementing booking status transitions?"',
        '"How should I handle cancellation policies with graduated refunds?"',
        '"Show me how to implement loyalty points earning and redemption."',
        '"How do I prevent double-booking and handle conflicts?"',
    ]
    
    for prompt in domain_prompts_4:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(Paragraph("7.5 Financial/Banking Systems", heading2_style))
    
    domain_prompts_5 = [
        '"How should I model different account types with their interest rates and limits?"',
        '"What\'s the best way to implement transaction validation and daily limits?"',
        '"How do I handle overdraft protection and linked accounts?"',
        '"Show me how to implement interest calculation (daily accrual, monthly application)."',
        '"How should I design ATM operations with PIN validation and card blocking?"',
    ]
    
    for prompt in domain_prompts_5:
        story.append(Paragraph(prompt, prompt_style))
    
    story.append(PageBreak())
    
    # ==========================================================================
    # SECTION 8: AI INTERACTION LOGGING
    # ==========================================================================
    story.append(Paragraph("Section 8: AI Interaction Logging", heading1_style))
    
    story.append(Paragraph(
        """When documenting AI interactions for your reflection document, include:""",
        normal_style
    ))
    
    logging_points = [
        "1. <b>The prompt you used</b> — Record the exact question or request",
        "2. <b>Summary of the AI's response</b> — Key points, code suggestions, or explanations",
        "3. <b>How you used/modified/rejected the suggestion</b> — Critical evaluation",
        "4. <b>Why you made that decision</b> — Your reasoning and understanding",
    ]
    
    for point in logging_points:
        story.append(Paragraph(point, bullet_style))
    
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Example AI Interaction Log Entry:", heading3_style))
    
    log_example = """
    <b>Prompt:</b> "How should I implement the Observer pattern for low-stock alerts?"
    
    <b>AI Response Summary:</b> The AI suggested creating an Observable interface with 
    add_observer(), remove_observer(), and notify_observers() methods. Products inherit 
    this interface and call notify_observers() when quantity drops below threshold.
    
    <b>How I Used It:</b> I adopted the basic structure but modified it to:
    - Pass the product SKU and current quantity in the notification
    - Use a default threshold of 10 instead of requiring it as a parameter
    - Added AlertType enum to categorize different notification types
    
    <b>Why:</b> The AI's suggestion was good for the basic pattern, but I needed more 
    context in notifications for the WarehouseManager to take action. Adding the enum 
    makes the system more extensible for future alert types.
    """
    
    story.append(Paragraph(log_example, example_style))
    
    story.append(Spacer(1, 20))
    
    # ==========================================================================
    # SECTION 9: PROMPT ENGINEERING TIPS
    # ==========================================================================
    story.append(Paragraph("Section 9: Prompt Engineering Tips", heading1_style))
    
    tips = [
        ("<b>Be Specific:</b>", "Instead of 'help me with classes', say 'help me design a class hierarchy for product types where each has different shipping rules'"),
        ("<b>Provide Context:</b>", "Include relevant code snippets, class names, and the problem domain"),
        ("<b>Ask for Trade-offs:</b>", "Request pros/cons when choosing between approaches"),
        ("<b>Request Examples:</b>", "Ask for Python code examples demonstrating the concept"),
        ("<b>Iterate:</b>", "Build on previous responses with follow-up questions"),
        ("<b>Challenge Assumptions:</b>", "Ask 'what if' questions to explore edge cases"),
        ("<b>Request Alternatives:</b>", "Ask for multiple approaches to compare"),
        ("<b>Verify Understanding:</b>", "Ask the AI to explain its suggestion in simpler terms"),
    ]
    
    for tip, explanation in tips:
        story.append(Paragraph(tip, normal_style))
        story.append(Paragraph(f"<i>{explanation}</i>", bullet_style))
        story.append(Spacer(1, 4))
    
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph("—" * 50, normal_style))
    story.append(Paragraph(
        "<i>This guide was created as a reference for NIT2112 Object-Oriented Programming. "
        "Use these prompts as starting points and adapt them to your specific assessment requirements.</i>",
        normal_style
    ))
    
    # Build PDF
    doc.build(story)
    print("PDF created successfully: NIT2112_AI_Copilot_Prompts_Guide.pdf")

if __name__ == "__main__":
    create_pdf()
