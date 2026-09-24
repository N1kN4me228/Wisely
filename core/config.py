"""
core/config.py

Single source of truth for two decisions that were previously implicit /
duplicated across the codebase:

1. DEMO_USER_ID
   No login screen for the hackathon MVP. core/content.py seeds exactly
   one user ('Руслан', id=1) and every screen should act as that user.
   Import DEMO_USER_ID here instead of hardcoding `1` in UI code, so if
   this ever changes (e.g. real login is added later) there's one place
   to update, not a search-and-replace across every screen.

2. FEATURES
   Toggles for sections that exist in the product plan but not in this
   build. UI code should check FEATURES["homework"] before rendering
   the Homework Page as an active link — see core/repository.py's
   get_homework() for the matching backend stub.
"""

DEMO_USER_ID = 1

FEATURES = {
    # No `homework` table in the schema yet, and no due-date/assignment
    # model has been designed. Keep the entry point visible but disabled
    # for MVP rather than removing it, so the screen isn't a surprise
    # add-on later. Flip to True once core/database.py has a real
    # `homework` table and repository.py has real CRUD for it.
    "homework": False,
}
