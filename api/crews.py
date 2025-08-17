from urllib.parse import urljoin
from pydantic import ValidationError

from api.dtos import CrewDTO
from api.errors import ApiError, DataValidationError
from api.http_client import request
import config


async def get_crews() -> list[CrewDTO]:
    base = config.BOKKA_API_BASE_URL.rstrip("/") + "/"
    url = urljoin(base, "api/v1/crews")
    response = await request("GET", url)
    if not 200 <= response.status_code < 300:
        raise ApiError(response.status_code, response.text[:100])
    try:
        payload = response.json()
    except ValueError as exc:
        raise DataValidationError() from exc
    try:
        return [CrewDTO.model_validate(item) for item in payload]
    except ValidationError as exc:
        raise DataValidationError() from exc
