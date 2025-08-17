from api.errors import ApiError, DataValidationError
from api.http_client import request
from planner.dtos import TaskDTO
import config


async def get_today_stops() -> list[TaskDTO]:
    response = await request("GET", config.STOPS_API_URL)
    if not 200 <= response.status_code < 300:
        raise ApiError(response.status_code, response.text[:100])
    try:
        data = response.json()
    except Exception as exc:  # broad to catch json decoding
        raise DataValidationError from exc
    try:
        return [TaskDTO.model_validate(item) for item in data]
    except Exception as exc:  # pydantic validation
        raise DataValidationError from exc
