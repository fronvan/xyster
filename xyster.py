#!/usr/bin/env python3

import sys
import json
import requests
from typing import List

STATIC_API = "https://monero.fail/nodes.json"
HEADERS = {"Content-Type": "application/json"}
TEST_PAYLOAD = {"jsonrpc": "2.0", "id": "0", "method": "get_info"}


def test_json_rpc(target: str) -> bool:
    try:
        res = requests.post(
            f"{target}/json_rpc", json=TEST_PAYLOAD, headers=HEADERS, timeout=1
        )
        res.raise_for_status()
        data = res.json()
        result = data["result"]

        return (
            result["mainnet"] is True
            and result["status"] == "OK"
            and result["synchronized"] is True
        )
    except Exception:
        return False


def gather() -> List[str]:
    try:
        print("[*] fetching nodes list...")
        response = requests.get(STATIC_API, timeout=10)
        response.raise_for_status()
        data = response.json()

        addrs = data["monero"]["clear"] + data["monero"]["web_compatible"]
        print(f"[*] found {len(addrs)} addresses to test")

        return addrs
    except Exception as e:
        print(f"[!] failed to fetch nodes: {e}")
        sys.exit(1)


def output(valid: List[str], outpath: str):
    try:
        with open(outpath, "w") as f:
            for address in valid:
                f.write(f"{address}\n")
        print(f"[*] results written to {outpath}")
    except Exception as e:
        print(f"[!] failed to write output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: ./zzz.py <output_file_path>")
        sys.exit(1)

    outpath = sys.argv[1]

    addrs = gather()
    valids = []

    try:
        for i, address in enumerate(addrs, 1):
            # print(f"[*] testing {i}/{len(addresses)}: {address}")
            if test_json_rpc(address):
                print(f"[*] success: {address}")
                valids.append(address)
    except KeyboardInterrupt:
        print("[!] interrupted by user")
        sys.exit(1)

    print(
        f"[*] found {len(valids)} ({len(valids)/len(addrs):.2f}) working json rpc endpoints"
    )
    output(valids, outpath)
