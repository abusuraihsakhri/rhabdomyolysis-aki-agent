#!/usr/bin/env python3
import os
import sys
os.environ.setdefault("AUDIT_SECRET_KEY", "cli-default-audit-key-change-in-production-2026")
from rhabdomyolysis_aki_agent.cli import main

if __name__ == '__main__':
    sys.exit(main())
