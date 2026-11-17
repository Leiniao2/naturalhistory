"""
Requirements and grants chosen by hand for the links links.py generates from the tree of life:
"from>to": ([functions required], [behaviors required], [functions granted], [behaviors granted]).
Kept in parts (requirements_1..4.py) by position in evolution.json when they were reviewed;
links.py reports entries whose link no longer exists after the tree changes.
"""

REVIEWED = {}
for _part in ("requirements_1", "requirements_2", "requirements_3", "requirements_4"):
    try:
        REVIEWED.update(__import__(_part).REVIEWED)
    except ImportError:
        pass
