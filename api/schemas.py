from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

# --- 1. Top Products Response Model Schema ---
class TopProductItem(BaseModel):
    product_term: str
    mention_count: int
    
    model_config = ConfigDict(from_attributes=True)

# --- 2. Channel Activity Output Schema ---
class ChannelActivityItem(BaseModel):
    post_date: datetime
    message_count: int
    avg_views: float
    
    model_config = ConfigDict(from_attributes=True)

# --- 3. Message Search Result Schema ---
class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_text: Optional[str] = None
    view_count: int
    forward_count: int
    has_image: bool
    
    model_config = ConfigDict(from_attributes=True)

# --- 4. Visual Content Stats Response Schema ---
class ChannelVisualStat(BaseModel):
    channel_name: str
    total_images_scraped: int
    promotional_count: int
    product_display_count: int
    lifestyle_count: int
    other_count: int
    
    model_config = ConfigDict(from_attributes=True)
    