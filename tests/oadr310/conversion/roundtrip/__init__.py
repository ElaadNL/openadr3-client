"""
Contains tests for the input and output module of the conversion module.

This module performs a roundtrip test on the input and output of the conversion module.
The roundtrip test ensures that the input and output conversion are inverse operations of each other.

The roundtrip test is performed by:
1. Converting the input to the output.
2. Converting the output back to the input.
3. Asserting that the original input and the converted input (from the output) are equal.
"""
