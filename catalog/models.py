import uuid  # Required for unique book instances
from contextlib import nullcontext

from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse


class Genre(models.Model):
    """Model representing a book genre"""

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry, etc.)",
    )

    def __str__(self):
        """String for representing the Genre object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse(
            "genre-detail",
            args=[str(self.id)],  # pyright: ignore [reportGeneralTypeIssues]
        )

    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        constraints = [
            UniqueConstraint(
                Lower("name"),
                name="genre_name_case_insensitive_unique",
                violation_error_message="Genre already exists (case insensitive match)",
            ),
        ]


class Language(models.Model):
    """Language book is written in."""

    abbreviation = models.CharField(max_length=2)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("language-detail", args=[str(self.id)])


class Book(models.Model):
    """Model representing a book (but not specific to a copy of a book)."""

    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey("Author", on_delete=models.RESTRICT, null=True)

    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book"
    )
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>',
    )
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    language = models.ForeignKey("Language", on_delete=models.RESTRICT, null=True)

    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        ordering = ["title", "author"]

    def __str__(self):
        """String for representing the Book object"""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse(
            "book-detail",
            args=[str(self.id)],  # pyright: ignore [reportGeneralTypeIssues]
        )

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ", ".join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = "Genre"


class BookInstance(models.Model):

    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book across whole library",
    )
    book = models.ForeignKey("Book", on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="m",
        help_text="Book availability",
    )

    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        ordering = ["due_back"]

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.id} ({self.book.title})"


class Author(models.Model):
    """Model representing an author."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)

    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse("author-detail", args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.last_name}, {self.first_name}"
