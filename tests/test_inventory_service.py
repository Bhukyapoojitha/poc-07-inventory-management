from unittest.mock import MagicMock

from app.services.inventory_service import (
    generate_sku,
    generate_po_number,
    check_stock_alerts
)

from app.models import StockLevel


def test_sku_format():
    mock_db = MagicMock()

    mock_db.query.return_value\
        .filter.return_value\
        .count.return_value = 41

    sku = generate_sku(
        "grocery",
        mock_db
    )

    assert sku == "SKU-GRO-0042"
    assert sku.startswith("SKU-GRO-")


def test_sku_categories():
    mock_db = MagicMock()

    mock_db.query.return_value\
        .filter.return_value\
        .count.return_value = 0

    assert generate_sku(
        "electronics",
        mock_db
    ).startswith("SKU-ELC-")

    assert generate_sku(
        "clothing",
        mock_db
    ).startswith("SKU-CLO-")

    assert generate_sku(
        "household",
        mock_db
    ).startswith("SKU-HHD-")


def test_po_number():
    mock_db = MagicMock()

    mock_db.query.return_value\
        .filter.return_value\
        .count.return_value = 41

    po_number = generate_po_number(
        mock_db
    )

    assert po_number.endswith("0042")


def test_low_stock_alert():
    mock_product = MagicMock()
    mock_product.id = 1
    mock_product.sku = "SKU-GRO-0001"
    mock_product.reorder_point = 20

    mock_stock = MagicMock()
    mock_stock.quantity_available = 15

    mock_db = MagicMock()

    check_stock_alerts(
        mock_product,
        mock_stock,
        mock_db
    )

    mock_db.add.assert_called_once()


def test_out_of_stock_alert():
    mock_product = MagicMock()
    mock_product.id = 1
    mock_product.sku = "SKU-GRO-0001"
    mock_product.reorder_point = 20

    mock_stock = MagicMock()
    mock_stock.quantity_available = 0

    mock_db = MagicMock()

    check_stock_alerts(
        mock_product,
        mock_stock,
        mock_db
    )

    mock_db.add.assert_called_once()


def test_quantity_available():
    stock = StockLevel()

    stock.quantity_on_hand = 100
    stock.quantity_reserved = 30

    assert stock.quantity_available == 70