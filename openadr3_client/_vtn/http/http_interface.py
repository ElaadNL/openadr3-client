class HttpInterface:
    """Represents a base class for a HTTP interface."""

    def __init__(self, base_url: str) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.

        """
        self.base_url = base_url
