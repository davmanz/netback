import re
import subprocess
import ipaddress
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def _parse_ping_stats(output: str) -> Dict[str, Any]:
    """Try to extract transmitted/received/loss from ping output in a robust way."""
    try:
        # Search for a line containing 'transmitted' (language independent approach)
        for line in output.splitlines():
            if 'transmitted' in line or 'transmitidos' in line:
                # extract numbers from line
                nums = [int(n) for n in re.findall(r"(\d+)", line)]
                if len(nums) >= 2:
                    transmitted = nums[0]
                    received = nums[1]
                    loss = ((transmitted - received) / transmitted) * 100 if transmitted else 0.0
                    return {"transmitted": transmitted, "received": received, "loss_percentage": loss}
        # Fallback: try to parse summary like '2 packets transmitted, 2 received'
        nums = [int(n) for n in re.findall(r"(\d+)", output)]
        if len(nums) >= 2:
            transmitted = nums[0]
            received = nums[1]
            loss = ((transmitted - received) / transmitted) * 100 if transmitted else 0.0
            return {"transmitted": transmitted, "received": received, "loss_percentage": loss}
    except Exception:
        logger.debug("Failed to parse ping stats", exc_info=True)
    return {}


def ping_ip(ip: str, count: int = 2, timeout_per_packet: int = 2, overall_timeout: int = 5) -> Dict[str, Any]:
    """Ping an IP and return a structured result.

    Returns a dict with keys:
      - reachable: bool
      - ip: str
      - raw_output: str
      - stats: dict (may be empty)
      - error: Optional[str]
    """
    result: Dict[str, Any] = {
        "ip": ip,
        "reachable": False,
        "raw_output": "",
        "stats": {},
        "error": None,
    }

    # Validate basic IP format
    try:
        ipaddress.ip_address(ip)
    except Exception:
        result["error"] = "invalid_ip"
        return result

    # Try standard linux ping flags first, then a common alternative (busybox)
    candidates = [
        ["ping", "-c", str(count), "-W", str(timeout_per_packet), ip],
        ["ping", "-c", str(count), "-w", str(timeout_per_packet), ip],
    ]

    for cmd in candidates:
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=overall_timeout,
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            result["raw_output"] = output

            if proc.returncode == 0:
                result["reachable"] = True
                result["stats"] = _parse_ping_stats(output)
                return result
            else:
                # Not reachable; try to infer specific errors from output
                lower = output.lower()
                if "unknown host" in lower or "name or service not known" in lower:
                    result["error"] = "unknown_host"
                elif "network is unreachable" in lower:
                    result["error"] = "network_unreachable"
                else:
                    result["error"] = "unreachable"
                result["stats"] = _parse_ping_stats(output)
                return result

        except subprocess.TimeoutExpired:
            result["error"] = "timeout"
            return result
        except FileNotFoundError:
            # ping binary not available on this system; continue to next candidate
            logger.debug("ping binary not found for cmd: %s", cmd)
            continue
        except Exception as e:
            logger.exception("Unexpected error while pinging %s: %s", ip, e)
            result["error"] = "exception"
            return result

    # If we reach here, ping binary was not found or all candidates failed to run
    result["error"] = "no_ping_binary"
    return result
