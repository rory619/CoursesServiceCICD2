from typing import Annotated
from annotated_types import Ge, Le
from pydantic import BaseModel, ConfigDict, StringConstraints

# ---------- Reusable type aliases ----------
CodeStr = Annotated[str, StringConstraints(min_length=1, max_length=32)]
CourseNameStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]
CreditsInt = Annotated[int, Ge(1), Le(120)]


class CourseCreate(BaseModel):
    code: CodeStr
    name: CourseNameStr
    credits: CreditsInt


class CourseRead(CourseCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)