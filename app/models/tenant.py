# Sqlalchemy database first Tenant Model
"""
Django model:

class Tenant(AbstractBaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(db_index=True, null=True, blank=True)
    billing_email = models.EmailField(db_index=True, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    db_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.db_name:
            self.db_name = generate_unique_db_name()
            # TODO async operation to create database in cloud sql postgres using db_name
        super(Tenant, self).save(*args, **kwargs)

"""
from sqlalchemy import Column, String, Boolean, DateTime, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tenant(Base):
    __tablename__ = 'authentication_tenant'  # Ensure this matches the table name used by Django

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    address = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    billing_email = Column(String(255), nullable=True, index=True)
    phone = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    deactivated_at = Column(DateTime, nullable=True)
    db_name = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Tenant(name='{self.name}')>"
