from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    pipeline_enabled = Column(Boolean, default=False)
    public_output_template = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Query(Base):
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_input = Column(Text, nullable=False)
    detected_category = Column(String)
    detected_intent = Column(String)
    constraints_json = Column(JSON)
    answer_text = Column(Text)
    answer_meta_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Connector(Base):
    __tablename__ = "connectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    config_json = Column(JSON, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    source_connector_id = Column(UUID(as_uuid=True), ForeignKey("connectors.id"))
    external_id = Column(String)
    title = Column(String, nullable=False)
    normalized_json = Column(JSON)
    raw_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Score(Base):
    __tablename__ = "scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("queries.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    total_score = Column(Integer)
    score_breakdown_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    label = Column(String)
    centroid_json = Column(JSON)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TokenizedInput(Base):
    __tablename__ = "tokenized_inputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("queries.id"), nullable=False)
    tokens_json = Column(JSON)
    features_json = Column(JSON)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("clusters.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminRule(Base):
    __tablename__ = "admin_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    key = Column(String, nullable=False)
    value_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
