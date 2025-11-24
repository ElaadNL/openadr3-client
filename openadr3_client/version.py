from enum import Enum


class OADRVersion(str, Enum):
    """The OpenADR Versions supported by this library."""

    OADR_301 = "oadr301"
    OADR_310 = "oadr310"
