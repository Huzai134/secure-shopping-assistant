from pydantic import BaseModel, Field, ValidationError

# In-memory store of discount codes and their availability.
# True means available/not redeemed. False means already redeemed.
discount_codes = {"WELCOME50": True, "SUMMER20": True}

# In-memory mock store of registered user IDs.
registered_users = {"user_1", "user_2", "user_3", "Huzai134"}

# In-memory database of loyalty points balances
loyalty_points = {"user_1": 100, "user_2": 250, "user_3": 50, "Huzai134": 500}


class LoyaltyPointsAwardRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="Registered user ID.")
    points: int = Field(
        ...,
        gt=0,
        le=10000,
        description="Loyalty points to award (must be positive, max 10,000 per transaction).",
    )


def redeem_discount_code(code: str, user_id: str) -> dict:
    """Redeems a single-use discount code for a registered user.

    Args:
        code: The discount code to redeem (e.g., WELCOME50, SUMMER20).
        user_id: The ID of the registered user (required).

    Returns:
        A dictionary with the redemption status and a descriptive message.
    """
    if not user_id:
        return {
            "status": "error",
            "message": "A registered user ID is required to redeem a discount code.",
        }

    if user_id not in registered_users:
        return {
            "status": "error",
            "message": f"User ID '{user_id}' is not registered. Registration is required to redeem discount codes.",
        }

    normalized_code = code.upper().strip()
    if normalized_code not in discount_codes:
        return {"status": "error", "message": f"Discount code '{code}' is invalid."}

    if not discount_codes[normalized_code]:
        return {
            "status": "error",
            "message": f"Discount code '{normalized_code}' has already been redeemed.",
        }

    # Mark as redeemed
    discount_codes[normalized_code] = False
    return {
        "status": "success",
        "message": f"Discount code '{normalized_code}' has been successfully redeemed for user '{user_id}'!",
    }


def award_loyalty_points(user_id: str, points: int) -> dict:
    """Awards loyalty points to a registered user's account after a successful purchase.

    Args:
        user_id: The ID of the registered user.
        points: The number of points to award (must be positive).

    Returns:
        A dictionary with the transaction status and result message.
    """
    try:
        # Validate parameters against the Pydantic schema
        request = LoyaltyPointsAwardRequest(user_id=user_id, points=points)
    except ValidationError as e:
        return {"status": "error", "message": f"Validation Error: {e.errors()}"}

    # Check if user ID is registered
    if request.user_id not in registered_users:
        return {
            "status": "error",
            "message": f"User ID '{request.user_id}' is not registered. Cannot award loyalty points.",
        }

    # Increment balance (default to 0 if not present)
    current_balance = loyalty_points.get(request.user_id, 0)
    new_balance = current_balance + request.points
    loyalty_points[request.user_id] = new_balance

    return {
        "status": "success",
        "message": f"Successfully awarded {request.points} loyalty points to user '{request.user_id}'. New balance: {new_balance} points.",
    }
