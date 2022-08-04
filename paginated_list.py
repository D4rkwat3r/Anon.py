from typing import Optional


class PaginatedList(list):
    def __init__(self, cursor: Optional[str], original_list: list):
        super().__init__(original_list)
        self.cursor = cursor
