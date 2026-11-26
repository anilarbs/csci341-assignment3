from datetime import date, datetime, time
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Positive = Annotated[int, Field(gt=0, strict=True)]
Labels = Annotated[list[Label], Field(min_length=1)]


class Form(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Author(Form):
    orcid: Label | None = None
    areas: Labels


class Reviewer(Form):
    years_experience: Annotated[int, Field(ge=0, strict=True)]
    expertise: Labels


class User(Form):
    given_name: Label
    surname: Label
    email: Label
    affiliation: Label
    country: Label
    phone_number: Label
    author: Author | None = None
    reviewer: Reviewer | None = None

    @model_validator(mode="after")
    def has_role(self):
        if self.author is None and self.reviewer is None:
            raise ValueError("Select an author profile, a reviewer profile, or both.")
        return self


class Authorship(Form):
    author_id: Positive
    author_position: Positive
    is_corresponding: bool


class Version(Form):
    version_no: Positive
    file_location: Label
    uploaded_at: datetime
    change_note: str | None = None

    @model_validator(mode="after")
    def local_time(self):
        if self.uploaded_at.tzinfo is not None:
            raise ValueError("Enter local conference time without an offset.")
        return self


class Paper(Form):
    track_id: Positive
    title: Label
    abstract: Label
    submission_date: date
    status: Literal["submitted","under review","accepted","rejected","withdrawn"]
    session_id: Positive | None = None
    keywords: Labels
    authors: Annotated[list[Authorship], Field(min_length=1)]
    versions: Annotated[list[Version], Field(min_length=1)]

    @model_validator(mode="after")
    def corresponding_author(self):
        if sum(a.is_corresponding for a in self.authors) != 1:
            raise ValueError("Select exactly one corresponding author.")
        return self


class Review(Form):
    paper_id: Positive
    reviewer_id: Positive
    overall_score: Annotated[int, Field(ge=1, le=5, strict=True)]
    recommendation: Literal["accept","reject"]
    comments_for_authors: Label
    confidential_comments: str | None = None
    review_submission_date: date


class Session(Form):
    conference_id: Positive
    title: Label
    session_date: date
    start_time: time
    end_time: time
    room_label: Label
    chair_id: Positive
