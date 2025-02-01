from pydantic import BaseModel

class ScraperSettings(BaseModel):
    page_limit: int  = 5
    proxy: str | None = None