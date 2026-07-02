from app.tools import discount_codes, redeem_discount_code


def test_redeem_discount_code_success() -> None:
    # Reset state
    discount_codes["WELCOME50"] = True

    # Test successful redemption
    result = redeem_discount_code("WELCOME50", "Huzai134")
    assert result["status"] == "success"
    assert "successfully redeemed" in result["message"]
    assert not discount_codes["WELCOME50"]


def test_redeem_discount_code_already_redeemed() -> None:
    # Set code as already redeemed
    discount_codes["WELCOME50"] = False

    result = redeem_discount_code("WELCOME50", "Huzai134")
    assert result["status"] == "error"
    assert "already been redeemed" in result["message"]


def test_redeem_discount_code_invalid_user() -> None:
    result = redeem_discount_code("SUMMER20", "invalid_user")
    assert result["status"] == "error"
    assert "not registered" in result["message"]


def test_redeem_discount_code_empty_user() -> None:
    result = redeem_discount_code("SUMMER20", "")
    assert result["status"] == "error"
    assert "registered user ID is required" in result["message"]


def test_redeem_discount_code_invalid_code() -> None:
    result = redeem_discount_code("INVALID_CODE", "Huzai134")
    assert result["status"] == "error"
    assert "invalid" in result["message"]


def test_redeem_discount_code_normalization() -> None:
    # Reset state
    discount_codes["SUMMER20"] = True

    # Test lowercase and trailing spaces
    result = redeem_discount_code("  summer20  ", "Huzai134")
    assert result["status"] == "success"
    assert not discount_codes["SUMMER20"]
