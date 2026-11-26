import os
import traceback

import uvicorn
from sqlalchemy import inspect
from db import engine, initialize
from part2 import main as run_part2


def main():
    with engine.begin() as connection:
        tables = inspect(connection).get_table_names()
        if not tables:
            initialize(connection)
            print("Database created and populated.", flush=True)
        elif "app_user" not in tables:
            raise RuntimeError("Unexpected database structure.")
        else:
            print("Existing database preserved.", flush=True)

    print("========== PART 2 START ==========", flush=True)

    try:
        run_part2()
        print("========== PART 2 PASSED ==========", flush=True)
    except Exception:
        traceback.print_exc()
        print("========== PART 2 FAILED ==========", flush=True)

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000"))
    )


if __name__ == "__main__":
    main()
