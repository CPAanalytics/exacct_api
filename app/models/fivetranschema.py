from sqlalchemy import Column, String, Boolean, DateTime, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FivetranSchema(Base):
    __tablename__ = 'xadmin_fivetranschema'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=False)
    source = Column(String(255), nullable=True)
    schema_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))

    def build_dbt_schema(self):
        if "test" in self.schema_name:
            return f'dbt_{self.source}'
        return f"dbt_{self.schema_name}_{self.source}"

    def build_schema(self):
        if 'test' in self.schema_name:
            return self.source
        return f"{self.schema_name}_{self.source}"
