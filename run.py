#!/usr/bin/env python
"""Run script for the Financial Tracking API."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.ai_worthy_api_roo_1.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )