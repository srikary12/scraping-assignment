from fastapi import Header, HTTPException

def validate_api_key(api_key: str = Header(...)) -> None:
    if api_key != "secret-token":
        raise HTTPException(status_code=403, detail="Invalid API key")