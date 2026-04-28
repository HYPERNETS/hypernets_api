r"""
Create a subset SQLite DB from an existing archive DB.

Default source DB: C:\Users\pdv\data\insitu\hypernets\\archive\\archive.db
Default query: SELECT * FROM products WHERE (site_id='WWUK' AND id<22114) OR id<20
Default destination: examples/archive_subset.db

Usage:
  python examples/create_subset_db.py
  python examples/create_subset_db.py --src /path/to/archive.db --dest examples/subset.db --query "SELECT ..."
"""
import os
import sqlite3
import argparse
import sys


DEFAULT_SRC = r"C:\Users\pdv\data\insitu\hypernets\archive\archive.db"


def copy_subset(src_db, dest_db, query):
    if not os.path.exists(src_db):
        raise FileNotFoundError(f"Source DB not found: {src_db}")

    # Connect to source DB
    src_conn = sqlite3.connect(src_db)
    src_cur = src_conn.cursor()

    # Get CREATE TABLE statement for `products`
    src_cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'")
    row = src_cur.fetchone()
    if row is None or row[0] is None:
        src_conn.close()
        raise RuntimeError("No `products` table found in source DB")
    create_sql = row[0]

    # Get column names for `products`
    src_cur.execute("PRAGMA table_info('products')")
    cols_info = src_cur.fetchall()
    if not cols_info:
        src_conn.close()
        raise RuntimeError("Failed to read columns for `products` table")
    cols = [c[1] for c in cols_info]

    # Execute query on source
    src_cur.execute(query)
    rows = src_cur.fetchall()

    # Prepare destination DB
    if os.path.exists(dest_db):
        os.remove(dest_db)
    dest_conn = sqlite3.connect(dest_db)
    dest_cur = dest_conn.cursor()

    # Create products table in destination using the original CREATE SQL
    dest_cur.execute(create_sql)

    # Insert fetched rows into destination
    placeholders = ",".join(["?" for _ in cols])
    insert_sql = f"INSERT INTO products ({', '.join(cols)}) VALUES ({placeholders})"

    # If rows are tuples matching columns order, insert directly.
    dest_cur.executemany(insert_sql, rows)
    dest_conn.commit()

    src_conn.close()
    dest_conn.close()

    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create subset SQLite DB from archive.db")
    parser.add_argument("--src", help="Source archive DB path", default=DEFAULT_SRC)
    parser.add_argument("--dest", help="Destination DB path", default=os.path.join(os.path.dirname(__file__), "archive_subset.db"))
    parser.add_argument(
        "--query",
        help="SQL query to select rows from products",
        default="SELECT * FROM products WHERE (site_id='WWUK' AND id<22114) OR id<20",
    )
    args = parser.parse_args(argv)

    try:
        count = copy_subset(args.src, args.dest, args.query)
        print(f"Wrote {count} rows to {args.dest}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
