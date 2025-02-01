from fastapi import FastAPI, Depends
import logging
from models import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/scrape")
def run_scraper(settings: settings.ScraperSettings):
    pass
