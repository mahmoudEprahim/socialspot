#! /usr/bin/env python3

"""
socialspot entrypoint
"""

import asyncio

from .socialspot import main

if __name__ == "__main__":
    asyncio.run(main())
