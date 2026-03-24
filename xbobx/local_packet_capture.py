import argparse
import os
import sys
import time
from pathlib import Path

from scapy.all import get_if_list, sniff, wrpcap


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture packets to local rotating PCAP files for diagnostics."
    )
    parser.add_argument(
        "--interface",
        required=True,
        help="Network interface name to capture from.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Seconds per capture file.",
    )
    parser.add_argument(
        "--output-dir",
        default="captures",
        help="Directory where PCAP files are written.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=10,
        help="Maximum number of capture files to keep.",
    )
    parser.add_argument(
        "--filter",
        default=None,
        help="Optional BPF filter, for example 'tcp port 443'.",
    )
    return parser.parse_args()


def validate_interface(interface: str) -> None:
    interfaces = set(get_if_list())
    if interface not in interfaces:
        available = ", ".join(sorted(interfaces))
        raise ValueError(
            f"Unknown interface '{interface}'. Available interfaces: {available}"
        )


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def cleanup_old_files(output_dir: Path, max_files: int) -> None:
    captures = sorted(output_dir.glob("capture-*.pcap"), key=lambda p: p.stat().st_mtime)
    while len(captures) > max_files:
        oldest = captures.pop(0)
        oldest.unlink(missing_ok=True)


def next_capture_path(output_dir: Path) -> Path:
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return output_dir / f"capture-{timestamp}.pcap"


def capture_loop(
    interface: str,
    duration: int,
    output_dir: Path,
    max_files: int,
    capture_filter: str | None,
) -> None:
    print(f"[*] Capturing on '{interface}'")
    print(f"[*] Writing PCAPs to '{output_dir}'")
    if capture_filter:
        print(f"[*] Using filter: {capture_filter}")

    while True:
        packets = sniff(iface=interface, timeout=duration, filter=capture_filter)
        if not packets:
            print("[!] No packets captured in this interval.")
            continue

        capture_path = next_capture_path(output_dir)
        wrpcap(str(capture_path), packets)
        print(f"[+] Saved {len(packets)} packets to {capture_path}")
        cleanup_old_files(output_dir, max_files)


def main() -> int:
    args = parse_args()

    if args.duration <= 0:
        print("Duration must be greater than 0.", file=sys.stderr)
        return 1
    if args.max_files <= 0:
        print("Max files must be greater than 0.", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir).resolve()

    try:
        validate_interface(args.interface)
        ensure_output_dir(output_dir)
        capture_loop(
            interface=args.interface,
            duration=args.duration,
            output_dir=output_dir,
            max_files=args.max_files,
            capture_filter=args.filter,
        )
    except KeyboardInterrupt:
        print("\n[*] Capture stopped.")
        return 0
    except Exception as exc:
        print(f"[!] Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
