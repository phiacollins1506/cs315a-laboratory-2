from fastapi import FastAPI, Query, Path
from typing import Optional

app = FastAPI()

prices_db: list[float] = [15.50, 99.99, 45.00, 250.00, 12.00, 500.25, 75.10]

@app.get("/prices")
async def get_prices(
        min_price: Optional[float] = Query(None, ge=0.0, title="Minimum Price"),
        max_price: Optional[float] = Query(None, le=1000.0, title="Maximum Price")
    ):
        filtered_prices = prices_db

        if min_price is not None:
            filtered_prices = [price for price in filtered_prices if price >= min_price]

        if max_price is not None:
            filtered_prices = [price for price in filtered_prices if price <= max_price]

        return {"filtered_prices": filtered_prices, "count": len(filtered_prices)}

employee_db: dict[int, str] = {
        1001: "Alice Johnson",
        1002: "Bob Smith",
        1003: "Charlie Davis"
    }

@app.get("/employees/{emp_id}")
async def get_employee(
        emp_id: int = Path(
            ge=1000,
            lt=10000,
            title="Employee ID Key", 
            description="4-digit internal employee code"
        )
    ):
        if emp_id in employee_db:
            return {"emp_id": emp_id, "name": employee_db[emp_id]}
        return {"error": "Employee record not found"}