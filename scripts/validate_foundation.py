#!/usr/bin/env python3
"""Backward-compatible entry point for the learner-release validator."""

from __future__ import annotations

import sys

from validate_release import main


if __name__ == "__main__":
    print("validate_foundation.py is retained for compatibility; running validate_release.py")
    sys.exit(main())
