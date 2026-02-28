from sqlalchemy import Column, Integer, LargeBinary, String
from app.core.database import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(LargeBinary(4), primary_key=True, index=True)
    gps_coordinates = Column(String)
    battery_level = Column(Integer)
    status = Column(String)
    