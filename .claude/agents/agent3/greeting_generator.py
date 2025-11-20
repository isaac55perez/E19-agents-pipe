"""
Greeting message generation with celebrity-style personalities.

This module provides greeting generation for two performance tiers:
- Low performers (grades 0-60): Eddie Murphy style
- High performers (grades >60): Donald Trump style
"""

import logging
import random
from typing import Tuple

logger = logging.getLogger(__name__)


class GreetingGenerator:
    """Generate personalized greeting messages based on grade and personality style."""

    # Grade threshold for personality style
    GRADE_THRESHOLD = 60

    # Eddie Murphy style greetings (grades 0-60)
    EDDIE_MURPHY_GREETINGS = [
        "Hey, hey! Keep it funky! You got this, now let's work on the code!",
        "Listen here! You're grinding, and that's what matters. Keep that energy up!",
        "C'mon now! Every master was once a beginner. You're on your way! Keep it funky!",
        "For real though, you've got talent - now show it on the next one! Stay positive!",
        "Hey! Don't let this slow you down. You know what I'm talking about? Keep grinding!",
        "That's the truth! You're learning and improving every day. Keep that funk alive!",
        "You know what you're saying? You got the moves, just need to perfect the code!",
        "Matter of fact, this is just a stepping stone. Keep moving forward, keep it funky!",
        "Ha! You tried, you learned, and you're getting better. That's what matters!",
        "Listen! Next time, you're gonna crush it. I can feel it. Keep that energy going!",
        "Hey, hey! Give yourself credit - you're out here trying and learning! That's awesome!",
        "You know what's real? Growth! And that's exactly what you're doing. Keep it up!",
        "C'mon, this is just fuel for the fire! Learn from it and come back stronger!",
        "That's right! Your journey is unique, and you're making progress. Believe in yourself!",
        "For real, you got this! Just need to fine-tune your approach. Let's go!",
    ]

    # Donald Trump style greetings (grades >60)
    DONALD_TRUMP_GREETINGS = [
        "Fantastic work! You're a winner, and these grades prove it. Tremendous execution!",
        "Incredible job! You did fantastic work here. That's the best kind of result!",
        "Fantastic! You've got what it takes - fantastic effort! Keep winning!",
        "Tremendous! Absolutely fantastic results. You're going to do great things. Believe me!",
        "The best performers understand quality work. You've got it. Keep winning!",
        "Outstanding! That's fantastic, fantastic work. You're a superstar! Keep it up!",
        "Incredible job on this! Fantastic execution - that's what winners do!",
        "You did a tremendous job! Fantastic, absolutely fantastic! Keep crushing it!",
        "Believe me, that's fantastic work! You're doing things the right way - the Trump way!",
        "Fantastic effort! These results are tremendous. You're winning, and I love it!",
        "The best results! Fantastic work, fantastic execution. Keep being great!",
        "Incredible! You nailed it! That's the kind of fantastic work that wins!",
        "Tremendous job! This is what excellence looks like. Keep up the fantastic work!",
        "You're fantastic! These results are tremendous - absolutely the best!",
        "Believe me, this is fantastic work! You're doing tremendous things. Keep winning!",
    ]

    @staticmethod
    def generate_greeting(grade: float) -> str:
        """
        Generate a greeting message based on grade and personality style.

        Args:
            grade: Numeric grade (0-100)

        Returns:
            Greeting message string

        Raises:
            ValueError: If grade is not numeric or out of range
        """
        # Validate grade
        try:
            grade_float = float(grade)
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid grade value: {grade}")
            raise ValueError(f"Grade must be numeric, got: {grade}") from e

        if not 0 <= grade_float <= 100:
            logger.warning(f"Grade out of expected range (0-100): {grade_float}")

        logger.debug(f"Generating greeting for grade: {grade_float}")

        # Select greeting based on grade threshold
        if grade_float <= GreetingGenerator.GRADE_THRESHOLD:
            greeting = random.choice(GreetingGenerator.EDDIE_MURPHY_GREETINGS)
            logger.debug(f"Selected Eddie Murphy style greeting for grade {grade_float}")
        else:
            greeting = random.choice(GreetingGenerator.DONALD_TRUMP_GREETINGS)
            logger.debug(f"Selected Donald Trump style greeting for grade {grade_float}")

        return greeting

    @staticmethod
    def get_personality_style(grade: float) -> str:
        """
        Get the personality style for a given grade.

        Args:
            grade: Numeric grade (0-100)

        Returns:
            Personality style name: "Eddie Murphy" or "Donald Trump"
        """
        try:
            grade_float = float(grade)
        except (ValueError, TypeError):
            raise ValueError(f"Grade must be numeric, got: {grade}")

        if grade_float <= GreetingGenerator.GRADE_THRESHOLD:
            return "Eddie Murphy"
        else:
            return "Donald Trump"

    @staticmethod
    def get_greeting_statistics() -> dict:
        """
        Get statistics about available greetings.

        Returns:
            Dictionary with greeting counts by personality
        """
        return {
            "eddie_murphy_count": len(GreetingGenerator.EDDIE_MURPHY_GREETINGS),
            "donald_trump_count": len(GreetingGenerator.DONALD_TRUMP_GREETINGS),
            "total_greetings": (
                len(GreetingGenerator.EDDIE_MURPHY_GREETINGS)
                + len(GreetingGenerator.DONALD_TRUMP_GREETINGS)
            ),
            "grade_threshold": GreetingGenerator.GRADE_THRESHOLD,
        }
