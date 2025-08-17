from urllib.parse import urljoin
from pydantic import ValidationError

from api.dtos import VehicleDTO
from api.errors import ApiError, DataValidationError
from api.http_client import request
import config


async def get_vehicles() -> list[VehicleDTO]:
    base = config.BOKKA_API_BASE_URL.rstrip("/") + "/"
    url = urljoin(base, "api/v1/vehicles")
    response = await request("GET", url)
    if not 200 <= response.status_code < 300:
        raise ApiError(response.status_code, response.text[:100])
    try:
        payload = response.json()
    except ValueError as exc:
        raise DataValidationError() from exc
    try:
        return [VehicleDTO.model_validate(item) for item in payload]
    except ValidationError as exc:
        raise DataValidationError() from exc
