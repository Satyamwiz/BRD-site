from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, groups, projects, documents, brd
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles



Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(brd.router, prefix="/api/brd", tags=["BRD"])
# Mount the 'uploads' directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")