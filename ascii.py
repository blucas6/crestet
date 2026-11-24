import argparse
import shutil

CONTROL_NAMES = [
    "NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL",
    "BS", "HT", "LF", "VT", "FF", "CR", "SO", "SI",
    "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
    "CAN", "EM", "SUB", "ESC", "FS", "GS", "RS", "US",
]


def label(code: int) -> str:
    """Return a displayable label for a character code."""
    if code < 32:
        return CONTROL_NAMES[code]  # non-printable: show its standard name
    if code == 32:
        return "SP"
    if code == 127:
        return "DEL"
    if 128 <= code < 160:
        return "·"  # C1 control codes, not displayable
    return chr(code)  # codes 128-255 map to Latin-1

def show_ascii():
    start, end = (32, 400)
    codes = list(range(start, end))

    cell_width = 14
    cols = max(1, min(8, shutil.get_terminal_size().columns // cell_width))
    rows = -(-len(codes) // cols)  # ceiling division

    print(f"{'Dec':>3}  {'Hex':<3} {'Chr':<4}  " * cols)
    print("-" * (cell_width * cols))
    for r in range(rows):
        line = ""
        for c in range(cols):
            i = c * rows + r  # fill down columns so values read in order
            if i < len(codes):
                code = codes[i]
                char = f"{label(code):<4}"
                line += f"{code:>3}  {code:02X}  {char}  "
        print(line.rstrip())

if __name__ == '__main__':
    show_ascii()
