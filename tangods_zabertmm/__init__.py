from .ZaberTMMAxis import ZaberTMMAxis
from .ZaberTMMCtrl import ZaberTMMCtrl


def main():
    import sys
    import tango.server

    args = ["ZaberTMM"] + sys.argv[1:]
    tango.server.run(
        (
            ZaberTMMCtrl,
            ZaberTMMAxis,
        ),
        args=args,
    )
