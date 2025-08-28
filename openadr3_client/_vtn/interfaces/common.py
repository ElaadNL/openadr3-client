from openadr3_client.plugin import ValidatorPlugin


class Interface:
    """Interface for a VTN."""

    validator_plugins: tuple[ValidatorPlugin, ...]

    def __init__(self, validator_plugins: tuple[ValidatorPlugin, ...]) -> None:
        """Initialize the interface."""
        self.validator_plugins = validator_plugins
