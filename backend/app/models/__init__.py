"""
Models package for the MRO (Maintenance, Repair, Operations) system.

This package contains the database models for managing boards, repair orders,
and diagnostics in the maintenance system.

To use the models, import them from the mro module:
    from app.models.mro import Board, RepairOrder, RepairStatus
"""

# Note: We don't import everything by default to avoid dependency loading issues.
# Use explicit imports from submodules as needed:
#   from app.models.mro import Board, RepairOrder, etc.