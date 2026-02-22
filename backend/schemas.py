from pydantic import BaseModel, HttpUrl
from typing import Optional

class URLRequest(BaseModel):
    url: HttpUrl
    html_content: Optional[str] = None
    
class InferenceResponse(BaseModel):
    target_url: str
    risk_score: float
    is_phishing: bool
    message: str