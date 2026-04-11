"""
Review system for visitor feedback.
Generates reviews based on animal welfare and zoo conditions.
"""

import random
from datetime import date
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Review:
    """Represents a visitor review of the zoo."""
    visitor_name: str
    rating: int  # 1-5 stars
    comment: str
    day: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "visitor_name": self.visitor_name,
            "rating": self.rating,
            "comment": self.comment,
            "day": self.day
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Review':
        """Create from dictionary."""
        return cls(
            visitor_name=data["visitor_name"],
            rating=data["rating"],
            comment=data["comment"],
            day=data["day"]
        )
    
    def get_star_display(self) -> str:
        """Get star emoji display (e.g., '⭐⭐⭐⭐⭐ 5 out of 5 stars')."""
        stars = "⭐" * self.rating
        return f"{stars} {self.rating} out of 5 stars"


# Visitor names pool
VISITOR_NAMES = [
    "Sarah M.", "John D.", "Emma K.", "Michael B.", "Olivia W.",
    "James T.", "Sophia L.", "William R.", "Isabella P.", "Benjamin F.",
    "Mia H.", "Lucas S.", "Charlotte G.", "Alexander C.", "Amelia N.",
    "Daniel V.", "Harper M.", "Matthew J.", "Evelyn A.", "Jackson B.",
    "Abigail K.", "Henry L.", "Emily R.", "Sebastian W.", "Ella D.",
    "David T.", "Scarlett H.", "Joseph P.", "Grace F.", "Samuel C.",
    "Chloe N.", "Ryan M.", "Lily B.", "Andrew K.", "Zoe L.",
    "Christopher R.", "Hannah W.", "Joshua G.", "Natalie V.", "Nicholas T."
]

# Review templates based on rating
REVIEW_TEMPLATES = {
    5: [
        "Amazing zoo! The {animal} looked so happy and well-cared for!",
        "Best day ever! The animals are thriving here. Keep up the great work!",
        "Absolutely loved seeing the {animal}! You can tell they're well looked after.",
        "Five stars! The {animal} was the highlight of our visit!",
        "Incredible experience! All the animals seem so content and healthy.",
        "Outstanding! The {animal} enclosure is fantastic!",
        "Perfect day out! The animals are clearly loved and cared for here.",
        "Wonderful zoo! The {animal} was adorable and looked very happy!"
    ],
    4: [
        "Great visit! The {animal} was lovely to see.",
        "Really enjoyed it. The {animal} looked healthy and active.",
        "Good experience overall. The animals seem well-maintained.",
        "Nice zoo! The {animal} was fascinating to watch.",
        "Solid visit. Most animals looked happy and healthy.",
        "Pretty good! The {animal} was entertaining.",
        "Enjoyed our time here. The animals are in good shape.",
        "Good day out! The {animal} was delightful."
    ],
    3: [
        "Okay visit. Some animals like the {animal} looked a bit neglected.",
        "It was alright. The {animal} didn't seem very happy though.",
        "Mixed feelings. Some enclosures could use more attention.",
        "Average experience. The {animal} looked like it needed care.",
        "Not bad, but the {animal} seemed a bit sad.",
        "Decent, though some animals didn't look their best.",
        "Fair visit. The {animal} could be healthier.",
        "Okay, but improvements needed. The {animal} looked stressed."
    ],
    2: [
        "Disappointed. The {animal} looked really unhappy and neglected.",
        "Not great. Several animals including the {animal} seemed poorly cared for.",
        "Below expectations. The {animal} was clearly distressed.",
        "Concerning visit. The {animal} didn't look well at all.",
        "Not impressed. The {animal} needs urgent attention.",
        "Poor conditions. The {animal} looked miserable.",
        "Sad to see the {animal} in such a state.",
        "Underwhelming. The {animal} desperately needs better care."
    ],
    1: [
        "Terrible! The {animal} looked absolutely miserable. This is unacceptable!",
        "Appalling conditions! The {animal} is clearly suffering. Reported!",
        "Shocking neglect! The {animal} and others are in terrible shape!",
        "Absolutely awful! The {animal} needs help immediately!",
        "Disgraceful! The animals are suffering. This place should be shut down!",
        "Worst zoo ever! The {animal} is in distress. Do better!",
        "Unacceptable! The {animal} and other animals are being neglected!",
        "Horrific! The {animal} looked so sad and sick. Never coming back!"
    ]
}

# Generic positive reviews (when zoo is generally doing well)
GENERIC_POSITIVE = [
    "Fantastic zoo! All the animals look so well cared for!",
    "Amazing experience! The whole zoo is beautifully maintained!",
    "Love this place! Such happy, healthy animals!",
    "Outstanding! You can see the love and care in every enclosure!",
    "Perfect family day out! The animals are thriving!"
]

# Generic negative reviews (when zoo is generally doing poorly)
GENERIC_NEGATIVE = [
    "So many animals looked unhappy. This zoo needs serious improvement.",
    "Several animals appeared neglected. Very concerning.",
    "Disappointed with the overall condition of the zoo.",
    "Many enclosures need attention. The animals deserve better.",
    "Not what we expected. Too many sad-looking animals."
]


def generate_reviews(
    animals: Dict,
    day: int,
    num_reviews: int = None,
    visitor_count: Optional[int] = None
) -> List[Review]:
    """
    Generate visitor reviews based on animal welfare.
    
    Args:
        animals: Dictionary of animal_name -> Animal objects
        day: Current day number
        num_reviews: Number of reviews to generate (default: random 2-5)
        visitor_count: Number of visitors that day. If 0, no reviews are generated.
    
    Returns:
        List of Review objects
    """
    if visitor_count is not None and visitor_count <= 0:
        return []

    if num_reviews is None:
        if visitor_count is None:
            num_reviews = random.randint(2, 5)
        else:
            max_reviews = min(5, max(0, visitor_count))
            if max_reviews <= 0:
                return []
            num_reviews = random.randint(1, max_reviews)

    if num_reviews <= 0:
        return []
    
    reviews = []
    
    # Calculate average happiness across all living animals
    living_animals = [a for a in animals.values() if a.is_alive]
    if not living_animals:
        return reviews  # No reviews if no animals
    
    avg_happiness = sum(a.happiness for a in living_animals) / len(living_animals)
    
    for _ in range(num_reviews):
        # Pick a random visitor name
        visitor_name = random.choice(VISITOR_NAMES)
        
        # Pick a random animal to mention (prefer living animals)
        if living_animals:
            featured_animal = random.choice(living_animals)
            animal_display = featured_animal.species.title()
        else:
            animal_display = "animals"
        
        # Determine rating based on animal happiness
        # Use both average happiness and the specific animal's happiness
        if living_animals:
            animal_happiness = featured_animal.happiness
            # Weight: 70% specific animal, 30% average
            combined_happiness = (animal_happiness * 0.7) + (avg_happiness * 0.3)
        else:
            combined_happiness = avg_happiness
        
        # Convert happiness (0-100) to rating (1-5)
        if combined_happiness >= 80:
            rating = 5
        elif combined_happiness >= 65:
            rating = 4
        elif combined_happiness >= 45:
            rating = 3
        elif combined_happiness >= 25:
            rating = 2
        else:
            rating = 1
        
        # Add some randomness (±1 star, but keep in 1-5 range)
        rating = max(1, min(5, rating + random.choice([-1, 0, 0, 1])))
        
        # Generate comment
        # 70% chance of animal-specific comment, 30% generic
        if random.random() < 0.7 and living_animals:
            templates = REVIEW_TEMPLATES[rating]
            comment = random.choice(templates).format(animal=animal_display)
        else:
            if rating >= 4:
                comment = random.choice(GENERIC_POSITIVE)
            else:
                comment = random.choice(GENERIC_NEGATIVE)
        
        reviews.append(Review(
            visitor_name=visitor_name,
            rating=rating,
            comment=comment,
            day=day
        ))
    
    return reviews


def calculate_reputation_from_reviews(reviews: List[Review]) -> float:
    """
    Calculate reputation score (0-100) from recent reviews.
    More recent reviews have higher weight.
    
    Args:
        reviews: List of Review objects
    
    Returns:
        Reputation score (0-100)
    """
    if not reviews:
        return 50.0  # Neutral starting reputation
    
    # Take last 20 reviews (or all if fewer)
    recent_reviews = reviews[-20:]
    
    # Calculate weighted average
    # More recent reviews get higher weight
    total_weight = 0
    weighted_sum = 0
    
    for i, review in enumerate(recent_reviews):
        # Weight increases for more recent reviews
        weight = i + 1  # 1, 2, 3, ... for older to newer
        # Convert rating (1-5) to score (0-100)
        score = ((review.rating - 1) / 4) * 100
        weighted_sum += score * weight
        total_weight += weight
    
    reputation = weighted_sum / total_weight if total_weight > 0 else 50.0
    return round(reputation, 1)
