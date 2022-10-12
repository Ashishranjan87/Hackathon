from sqlalchemy import MetaData
import models
from sqlalchemy import Table, Column, Integer, String, BigInteger
meta = MetaData()
users = Table(
    'employeeDetails', meta,
    Column('id', Integer, primary_key=True),
    Column('Name', String(60), nullable=False),
    Column('Address', String(100), nullable=False),
    Column('Email', String(100), nullable=False),
    Column('mobileNo', Integer, nullable=False),
    Column('Desiganation', String(60), nullable=False)
)
