"""
Unit tests for greeting_generator module.

Tests cover:
- Greeting generation for different grades
- Personality style selection
- Grade validation
- Error handling
"""

import pytest
from greeting_generator import GreetingGenerator


class TestGreetingGenerator:
    """Tests for GreetingGenerator class."""

    def test_generate_greeting_low_grade(self):
        """Test greeting generation for low grade (Eddie Murphy style)."""
        greeting = GreetingGenerator.generate_greeting(30)
        assert greeting is not None
        assert isinstance(greeting, str)
        assert len(greeting) > 0

    def test_generate_greeting_high_grade(self):
        """Test greeting generation for high grade (Donald Trump style)."""
        greeting = GreetingGenerator.generate_greeting(80)
        assert greeting is not None
        assert isinstance(greeting, str)
        assert len(greeting) > 0

    def test_generate_greeting_threshold(self):
        """Test greeting at threshold grade (60)."""
        greeting = GreetingGenerator.generate_greeting(60)
        assert greeting is not None
        assert isinstance(greeting, str)

    def test_generate_greeting_just_above_threshold(self):
        """Test greeting just above threshold (61)."""
        greeting = GreetingGenerator.generate_greeting(61)
        assert greeting is not None

    def test_generate_greeting_perfect_score(self):
        """Test greeting for perfect score (100)."""
        greeting = GreetingGenerator.generate_greeting(100)
        assert greeting is not None

    def test_generate_greeting_zero_score(self):
        """Test greeting for zero score."""
        greeting = GreetingGenerator.generate_greeting(0)
        assert greeting is not None

    def test_generate_greeting_float_grade(self):
        """Test greeting with float grade value."""
        greeting = GreetingGenerator.generate_greeting(75.5)
        assert greeting is not None

    def test_generate_greeting_string_numeric(self):
        """Test greeting with string numeric grade."""
        greeting = GreetingGenerator.generate_greeting("85")
        assert greeting is not None

    def test_generate_greeting_invalid_non_numeric(self):
        """Test greeting with non-numeric grade raises error."""
        with pytest.raises(ValueError):
            GreetingGenerator.generate_greeting("invalid")

    def test_generate_greeting_invalid_none(self):
        """Test greeting with None grade raises error."""
        with pytest.raises(ValueError):
            GreetingGenerator.generate_greeting(None)

    def test_get_personality_style_low_grade(self):
        """Test personality style for low grade."""
        style = GreetingGenerator.get_personality_style(50)
        assert style == "Eddie Murphy"

    def test_get_personality_style_high_grade(self):
        """Test personality style for high grade."""
        style = GreetingGenerator.get_personality_style(75)
        assert style == "Donald Trump"

    def test_get_personality_style_threshold(self):
        """Test personality style at threshold."""
        style = GreetingGenerator.get_personality_style(60)
        assert style == "Eddie Murphy"

    def test_get_personality_style_just_above_threshold(self):
        """Test personality style just above threshold."""
        style = GreetingGenerator.get_personality_style(61)
        assert style == "Donald Trump"

    def test_get_greeting_statistics(self):
        """Test greeting statistics."""
        stats = GreetingGenerator.get_greeting_statistics()
        assert isinstance(stats, dict)
        assert "eddie_murphy_count" in stats
        assert "donald_trump_count" in stats
        assert "total_greetings" in stats
        assert "grade_threshold" in stats
        assert stats["eddie_murphy_count"] > 0
        assert stats["donald_trump_count"] > 0
        assert stats["grade_threshold"] == 60

    def test_eddie_murphy_greetings_variety(self):
        """Test that Eddie Murphy greetings are diverse."""
        greetings = set()
        for _ in range(50):
            greeting = GreetingGenerator.generate_greeting(30)
            greetings.add(greeting)
        # With randomization, we should get multiple different greetings
        assert len(greetings) > 1

    def test_donald_trump_greetings_variety(self):
        """Test that Donald Trump greetings are diverse."""
        greetings = set()
        for _ in range(50):
            greeting = GreetingGenerator.generate_greeting(80)
            greetings.add(greeting)
        # With randomization, we should get multiple different greetings
        assert len(greetings) > 1

    def test_greeting_contains_key_words_eddie(self):
        """Test Eddie Murphy greeting contains characteristic keywords."""
        # Generate many to find ones with expected keywords
        found_keywords = False
        keywords = ["hey", "funky", "keep", "C'mon", "Listen", "Matter"]
        for _ in range(10):
            greeting = GreetingGenerator.generate_greeting(25)
            if any(keyword.lower() in greeting.lower() for keyword in keywords):
                found_keywords = True
                break
        assert found_keywords

    def test_greeting_contains_key_words_trump(self):
        """Test Donald Trump greeting contains characteristic keywords."""
        # Generate many to find ones with expected keywords
        found_keywords = False
        keywords = ["fantastic", "tremendous", "believe", "best", "winning"]
        for _ in range(10):
            greeting = GreetingGenerator.generate_greeting(75)
            if any(keyword.lower() in greeting.lower() for keyword in keywords):
                found_keywords = True
                break
        assert found_keywords
