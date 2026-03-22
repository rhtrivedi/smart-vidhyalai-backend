from fastapi import FastAPI
from app.api import tenants, users, auth, academic, enrollment, attendance, finance

app = FastAPI(
    title="Smart Vidhyalai API",
    version="1.0.0",
    description="The AI-powered core engine for educational institutions.",
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# Attach the tenants router with a clean, versioned URL prefix
app.include_router(
    tenants.router, prefix="/api/v1/tenants", tags=["Tenants (Institutions)"]
)

app.include_router(users.router, prefix="/api/v1/users", tags=["Users & IAM"])

app.include_router(academic.router, prefix="/api/v1/academic", tags=["Academic Engine"])

app.include_router(
    enrollment.router, prefix="/api/v1/enrollment", tags=["Enrollment & Admissions"]
)

app.include_router(
    attendance.router, prefix="/api/v1/attendance", tags=["Attendance Engine"]
)

app.include_router(finance.router, prefix="/api/v1/finance", tags=["Financial Ledger"])


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Smart Vidhyalai API. System is running perfectly."
    }
