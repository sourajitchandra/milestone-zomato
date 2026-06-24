"""
One-time script: downloads the Zomato dataset shards from HuggingFace,
selects only the columns needed by the app, and saves to data/restaurants.parquet
so Railway can load it directly from git without any network call at startup.

Run once locally:
    python scripts/generate_bundled_data.py
Then commit data/restaurants.parquet to git.
"""

import io
import os
import sys

import pandas as pd
import pyarrow.parquet as pq
import requests

PARQUET_URLS = [
    "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation"
    "/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet",
    "https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation"
    "/resolve/refs%2Fconvert%2Fparquet/default/train/0001.parquet",
]

NEEDED_COLUMNS = [
    "name",
    "location",
    "rate",
    "approx_cost(for two people)",
    "cuisines",
    "address",
    "online_order",
    "book_table",
    "votes",
    "rest_type",
    "listed_in(type)",
    "listed_in(city)",
]

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "restaurants.parquet")


def download_shard(url: str, idx: int) -> pd.DataFrame:
    print(f"  Downloading shard {idx}: {url}")
    headers = {"User-Agent": "python-requests/zomato-ai"}
    with requests.get(url, headers=headers, timeout=300, stream=True) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("Content-Length", 0))
        print(f"  Shard {idx} size: {total / 1024 / 1024:.1f} MB")
        buf = io.BytesIO()
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                buf.write(chunk)
    buf.seek(0)
    pf = pq.ParquetFile(buf)
    available = pf.schema_arrow.names
    cols = [c for c in NEEDED_COLUMNS if c in available]
    missing = [c for c in NEEDED_COLUMNS if c not in available]
    if missing:
        print(f"  WARNING: columns missing from shard {idx}: {missing}")
    table = pf.read(columns=cols)
    df = table.to_pandas()
    print(f"  Shard {idx}: {len(df)} rows, {len(df.columns)} columns")
    return df


def main():
    print("=== Generating bundled restaurant data ===")
    shards = [download_shard(url, i + 1) for i, url in enumerate(PARQUET_URLS)]
    df = pd.concat(shards, ignore_index=True)
    print(f"Total rows: {len(df)}")

    out = os.path.abspath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_parquet(out, index=False, compression="zstd")

    size_mb = os.path.getsize(out) / 1024 / 1024
    print(f"\n✅ Saved to: {out}")
    print(f"   File size: {size_mb:.1f} MB")
    print(f"\nNext step: git add data/restaurants.parquet && git commit -m 'data: add bundled restaurant parquet'")


if __name__ == "__main__":
    main()
