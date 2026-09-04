import os
import time

from flask import jsonify, make_response, request
from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from limiter import limiter
from services.history_service import get_history
from utils.logging import get_logger

from .data_schemas import HistorySchema

API_RATE_LIMIT = os.getenv("API_RATE_LIMIT", "10 per second")
api = Namespace("history", description="Historical Data API")

# Initialize logger
logger = get_logger(__name__)

# Initialize schema
history_schema = HistorySchema()


@api.route("/", strict_slashes=False)
class History(Resource):
    @limiter.limit(API_RATE_LIMIT)
    def post(self):
        """Get historical data for given symbol"""
        request_started_at = time.perf_counter()
        try:
            # Validate request data
            history_data = history_schema.load(request.json)

            api_key = history_data["apikey"]
            symbol = history_data["symbol"]
            exchange = history_data["exchange"]
            interval = history_data["interval"]
            start_date = history_data["start_date"]
            end_date = history_data["end_date"]
            source = history_data.get("source", "api")  # Optional, defaults to 'api'

            # Call the service function to get historical data with API key
            success, response_data, status_code = get_history(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
                api_key=api_key,
                source=source,
            )

            before_response_ms = (time.perf_counter() - request_started_at) * 1000
            logger.info(
                "History request service completed in %.2f ms (symbol=%s, exchange=%s, source=%s)",
                before_response_ms,
                symbol,
                exchange,
                source,
            )

            response = make_response(jsonify(response_data), status_code)
            total_request_ms = (time.perf_counter() - request_started_at) * 1000
            logger.info(
                "History request completed in %.2f ms (response construction: %.2f ms, status=%s, symbol=%s, exchange=%s, source=%s)",
                total_request_ms,
                total_request_ms - before_response_ms,
                status_code,
                symbol,
                exchange,
                source,
            )
            return response

        except ValidationError as err:
            return make_response(jsonify({"status": "error", "message": err.messages}), 400)
        except Exception as e:
            logger.exception(f"Unexpected error in history endpoint: {e}")
            return make_response(
                jsonify({"status": "error", "message": "An unexpected error occurred"}), 500
            )
