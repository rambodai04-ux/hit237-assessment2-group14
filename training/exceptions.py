class ProgramNotFound(Exception):
    """Raised when a requested training program does not exist."""
    pass


class ProgramInactive(Exception):
    """Raised when trying to enrol in an inactive training program."""
    pass
