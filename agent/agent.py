from types import SimpleNamespace

from agent.tools import (
    get_low_stock_alerts,
    get_product_stock,
    get_supplier_catalog,
    get_dashboard_stats,
    search_inventory_policy
)


def build_agent_executor():
    return SimpleNamespace(
        tools=[
            get_low_stock_alerts,
            get_product_stock,
            get_supplier_catalog,
            get_dashboard_stats,
            search_inventory_policy
        ]
    )