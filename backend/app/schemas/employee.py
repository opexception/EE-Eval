from pydantic import BaseModel, Field

from app.models.employee import Employee


class EmployeeCreateRequest(BaseModel):
    employee_number: str = Field(min_length=1, max_length=32)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    job_title: str = Field(min_length=1, max_length=120)
    department: str = Field(min_length=1, max_length=120)
    manager_id: int | None = Field(default=None, gt=0)
    user_id: int | None = Field(default=None, gt=0)


class EmployeeUpdateRequest(BaseModel):
    employee_number: str | None = Field(default=None, min_length=1, max_length=32)
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    job_title: str | None = Field(default=None, min_length=1, max_length=120)
    department: str | None = Field(default=None, min_length=1, max_length=120)
    manager_id: int | None = Field(default=None, gt=0)
    user_id: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class EmployeeResponse(BaseModel):
    id: int
    employee_number: str
    first_name: str
    last_name: str
    full_name: str
    job_title: str
    department: str
    manager_id: int | None
    manager_name: str | None
    is_active: bool

    @classmethod
    def from_employee(cls, employee: Employee) -> "EmployeeResponse":
        manager_name = employee.manager.full_name if employee.manager is not None else None
        return cls(
            id=employee.id,
            employee_number=employee.employee_number,
            first_name=employee.first_name,
            last_name=employee.last_name,
            full_name=employee.full_name,
            job_title=employee.job_title,
            department=employee.department,
            manager_id=employee.manager_id,
            manager_name=manager_name,
            is_active=employee.is_active,
        )
