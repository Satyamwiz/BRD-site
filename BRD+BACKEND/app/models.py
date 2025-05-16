from sqlalchemy import Column, Integer, String, ForeignKey, Table, LargeBinary
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import Text


group_members = Table(
    'group_members', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    groups = relationship("Group", secondary=group_members, back_populates="members")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    members = relationship("User", secondary=group_members, back_populates="groups")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    group_id = Column(Integer, ForeignKey("groups.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    group = relationship("Group")
    creator = relationship("User")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    path = Column(String)
    description = Column(String)
    summary_title = Column(String)
    summary_description = Column(Text)

    project_id = Column(Integer, ForeignKey("projects.id"))
    uploaded_by = Column(Integer, ForeignKey("users.id"))

    project = relationship("Project", backref="documents")
    uploader = relationship("User")
