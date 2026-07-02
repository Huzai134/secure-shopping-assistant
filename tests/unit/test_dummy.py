from app.tools import (
    award_loyalty_points,
    discount_codes,
    loyalty_points,
    redeem_discount_code,
)


def test_redeem_discount_code_success() -> None:
    # Reset state
    discount_codes["WELCOME50"] = True

    # Test successful redemption
    result = redeem_discount_code("WELCOME50", "Huzai134")
    assert result["status"] == "success"
    assert "successfully redeemed" in result["message"]
    assert not discount_codes["WELCOME50"]


def test_redeem_discount_code_already_redeemed() -> None:
    # Already redeemed
    discount_codes["WELCOME50"] = False

    result = redeem_discount_code("WELCOME50", "Huzai134")
    assert result["status"] == "error"
    assert "already been redeemed" in result["message"]


def test_redeem_discount_code_invalid_user() -> None:
    result = redeem_discount_code("SUMMER20", "invalid_user")
    assert result["status"] == "error"
    assert "not registered" in result["message"]


def test_redeem_discount_code_invalid_code() -> None:
    result = redeem_discount_code("INVALID_CODE", "Huzai134")
    assert result["status"] == "error"
    assert "invalid" in result["message"]


def test_award_loyalty_points_success() -> None:
    # Setup initial state
    loyalty_points["Huzai134"] = 500

    result = award_loyalty_points("Huzai134", 150)
    assert result["status"] == "success"
    assert loyalty_points["Huzai134"] == 650
    assert "Successfully awarded 150" in result["message"]


def test_award_loyalty_points_negative() -> None:
    result = award_loyalty_points("Huzai134", -10)
    assert result["status"] == "error"
    assert "Validation Error" in result["message"]


def test_award_loyalty_points_excessive() -> None:
    result = award_loyalty_points("Huzai134", 20000)
    assert result["status"] == "error"
    assert "Validation Error" in result["message"]


def test_award_loyalty_points_invalid_user() -> None:
    result = award_loyalty_points("invalid_user", 100)
    assert result["status"] == "error"
    assert "not registered" in result["message"]
