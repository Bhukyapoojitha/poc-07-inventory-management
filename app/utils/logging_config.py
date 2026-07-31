import logging

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )
)

logger = logging.getLogger(
    "inventory-management"
)


def log_product_created(
    sku: str
):
    logger.info(
        f"product_created | "
        f"poc_id=POC-07 | "
        f"sku={sku}"
    )


def log_stock_updated(
    sku: str,
    quantity: int
):
    logger.info(
        f"stock_updated | "
        f"poc_id=POC-07 | "
        f"sku={sku} | "
        f"quantity={quantity}"
    )


def log_po_created(
    po_number: str
):
    logger.info(
        f"po_created | "
        f"poc_id=POC-07 | "
        f"po_number={po_number}"
    )


def log_low_stock_alert(
    sku: str
):
    logger.info(
        f"low_stock_alert | "
        f"poc_id=POC-07 | "
        f"sku={sku}"
    )