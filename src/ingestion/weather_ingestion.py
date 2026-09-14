import json
import uuid
from datetime import datetime, timezone
import logging
import boto3
import requests


# Configuration
API_URL = "https://api.open-meteo.com/v1/forecast"

S3_BUCKET = "food-delivery-lakehouse-dev-2026"
S3_PREFIX = "raw/weather"

CITY = "mumbai"
LATITUDE = 19.0760
LONGITUDE = 72.8777

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# Extract
def extract_weather():
    try:
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "hourly": "temperature_2m,rain,weather_code",
            "timezone": "Asia/Kolkata"
        }

        response = requests.get(
            API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        logger.info("Weather data extracted successfully for %s", CITY)

        return response.json()

    except requests.RequestException:
        logger.exception("Weather API extraction failed")
        raise


# Load
def load_to_s3(data):
    try:
        s3 = boto3.client("s3")

        timestamp = datetime.now(timezone.utc)
        batch_id = str(uuid.uuid4())

        payload = {
            "metadata": {
                "ingestion_timestamp": timestamp.isoformat(),
                "source": "open-meteo",
                "batch_id": batch_id
            },
            "data": data
        }

        file_name = timestamp.strftime("%Y%m%d_%H%M%S") + ".json"

        s3_key = (
            f"{S3_PREFIX}/"
            f"city={CITY}/"
            f"ingestion_date={timestamp:%Y-%m-%d}/"
            f"{file_name}"
        )

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(payload),
            ContentType="application/json"
        )

        logger.info(
            "Data loaded successfully to s3://%s/%s",
            S3_BUCKET,
            s3_key
        )

    except Exception:
        logger.exception("S3 load failed")
        raise


# Main
def main():
    try:
        weather_data = extract_weather()
        load_to_s3(weather_data)

        logger.info("Weather ingestion pipeline completed successfully")

    except Exception:
        logger.exception("Weather ingestion pipeline failed")
        raise


if __name__ == "__main__":
    main()