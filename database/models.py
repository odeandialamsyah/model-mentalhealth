from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)

    # FK ke users.id
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    input_text = Column(String(1000), nullable=False)
    predicted_label = Column(String(50), nullable=False)
    predicted_id = Column(Integer, nullable=False)
    probability_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
