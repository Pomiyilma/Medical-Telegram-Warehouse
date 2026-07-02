from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from api.database import get_db
from api.schemas import (
    TopProductItem, 
    ChannelActivityItem, 
    MessageSearchResult, 
    ChannelVisualStat
)

app = FastAPI(
    title="Kara Solutions Medical Analytics Hub",
    description="Production REST API tier exposing dbt star schema data products and computer vision indicators.",
    version="1.0.0"
)

# --- Endpoint 1: Top Products ---
@app.get(
    "/api/reports/top-products", 
    response_model=List[TopProductItem],
    summary="Fetch most frequently mentioned medical terms",
    description="Scans message texts for dominant pharmaceutical terms and returns an aggregated frequency list table."
)
def get_top_products(limit: int = Query(10, description="Number of top terms to return"), db: Session = Depends(get_db)):
    # Simple algorithmic tokenization query matching dominant Ethiopian medical keywords
    query = text("""
        WITH words AS (
            SELECT regexp_split_to_table(lower(message_text), '\s+') AS word
            FROM dev.fct_messages
        )
        SELECT word AS product_term, count(*) AS mention_count
        FROM words
        WHERE word IN ('paracetamol', 'amoxicillin', 'cimetidine', 'ibuprofen', 'diclofenac', 
                       'vitamin', 'serum', 'cream', 'capsule', 'tablet', 'syrup', 'gel')
        GROUP BY word
        ORDER BY mention_count DESC
        LIMIT :limit;
    """)
    
    result = db.execute(query, {"limit": limit}).fetchall()
    return [{"product_term": row[0], "mention_count": row[1]} for row in result]


# --- Endpoint 2: Channel Activity ---
@app.get(
    "/api/channels/{channel_name}/activity", 
    response_model=List[ChannelActivityItem],
    summary="Get posting volume and view trends per channel",
    description="Aggregates message frequency counts and average views grouped by calendar dates for a specific target channel."
)
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            CAST(m.message_date AS DATE) as post_date,
            COUNT(*) as message_count,
            ROUND(AVG(m.view_count), 2) as avg_views
        FROM dev.stg_telegram_messages m
        WHERE LOWER(m.channel_name) = LOWER(:channel_name)
        GROUP BY CAST(m.message_date AS DATE)
        ORDER BY post_date DESC;
    """)
    
    result = db.execute(query, {"channel_name": channel_name}).fetchall()
    
    if not result:
        raise HTTPException(status_code=404, detail=f"No activity records discovered for channel name '{channel_name}'")
        
    return [{"post_date": row[0], "message_count": row[1], "avg_views": float(row[2])} for row in result]


# --- Endpoint 3: Message Search ---
@app.get(
    "/api/search/messages", 
    response_model=List[MessageSearchResult],
    summary="Case-insensitive keyword message search index",
    description="Searches through the central fact table text streams using case-insensitive wildcard expressions."
)
def search_messages(
    query: str = Query(..., description="The keyword to search for (e.g., paracetamol)"), 
    limit: int = Query(20, description="Maximum number of search matching rows to fetch"), 
    db: Session = Depends(get_db)
):
    sql_query = text("""
        SELECT 
            m.message_id,
            c.channel_name,
            m.message_text,
            m.view_count,
            m.forward_count,
            m.has_image
        FROM dev.fct_messages m
        JOIN dev.dim_channels c ON m.channel_key = c.channel_key
        WHERE m.message_text ILIKE :search_pattern
        ORDER BY m.view_count DESC
        LIMIT :limit;
    """)
    
    result = db.execute(sql_query, {"search_pattern": f"%{query}%", "limit": limit}).fetchall()
    
    return [{
        "message_id": row[0],
        "channel_name": row[1],
        "message_text": row[2],
        "view_count": row[3],
        "forward_count": row[4],
        "has_image": row[5]
    } for row in result]


# --- Endpoint 4: Visual Content Stats ---
@app.get(
    "/api/reports/visual-content", 
    response_model=List[ChannelVisualStat],
    summary="Fetch aggregated YOLO computer vision marketing statistics",
    description="Groups your YOLO image classification matrices to analyze promotional vs product catalog distribution strategy."
)
def get_visual_content_stats(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            c.channel_name,
            COUNT(i.message_id) as total_images_scraped,
            COUNT(CASE WHEN i.image_category = 'promotional' THEN 1 END) as promotional_count,
            COUNT(CASE WHEN i.image_category = 'product_display' THEN 1 END) as product_display_count,
            COUNT(CASE WHEN i.image_category = 'lifestyle' THEN 1 END) as lifestyle_count,
            COUNT(CASE WHEN i.image_category = 'other' THEN 1 END) as other_count
        FROM dev.dim_channels c
        LEFT JOIN dev.fct_image_detections i ON c.channel_key = i.channel_key
        GROUP BY c.channel_name
        ORDER BY total_images_scraped DESC;
    """)
    
    result = db.execute(query).fetchall()
    return [{
        "channel_name": row[0],
        "total_images_scraped": row[1],
        "promotional_count": row[2],
        "product_display_count": row[3],
        "lifestyle_count": row[4],
        "other_count": row[5]
    } for row in result]
