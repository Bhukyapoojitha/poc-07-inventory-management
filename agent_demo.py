from agent.tools import (
    get_dashboard_stats,
    search_inventory_policy
)

print("=" * 50)
print("PHASE 3 TOOL DEMO")
print("=" * 50)

print("\nDashboard Stats\n")
print(get_dashboard_stats.invoke(""))

print("\nPolicy Search\n")
print(
    search_inventory_policy.invoke(
        "When is PO approval required?"
    )
)