from sqlalchemy import Column, Integer, LargeBinary, String, event
from app.core.database import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(LargeBinary(4), primary_key=True, index=True)
    last_byte = Column(Integer)
    gps_coordinates = Column(String)
    battery_level = Column(Integer)
    status = Column(String)

@event.listens_for(Node.id, 'set', retval=True)
def update_last_byte(target, value, oldvalue, initiator):
    """Automatically update last_byte when id is set"""
    if value is not None:
        target.last_byte = value[-1] if isinstance(value, bytes) else None
    return value
    