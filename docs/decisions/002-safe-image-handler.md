# Decision 002: support a narrow image format

**Status:** Accepted

The demonstration resize handler accepts uncompressed 24-bit BMP and uses the standard library, avoiding native image dependencies. Input is validated before pixel processing. This is not general-purpose image support; additional formats need explicit size and resource limits.
