from typing import Literal
from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr


class VehicleDTO(BaseModel):
    id: StrictStr
    plate: StrictStr
    capacity: StrictInt
    office: StrictStr
    division: StrictStr | None
    model_config = ConfigDict(extra="ignore")


class CrewMemberDTO(BaseModel):
    id: StrictStr
    name: StrictStr
    role: Literal["driver", "assistant", "assistant2"]
    model_config = ConfigDict(extra="ignore")


class CrewDTO(BaseModel):
    id: StrictStr
    driver: CrewMemberDTO
    assistant: CrewMemberDTO | None
    assistant2: CrewMemberDTO | None
    vehicle: VehicleDTO | None
    office: StrictStr
    division: StrictStr | None
    model_config = ConfigDict(extra="ignore")
