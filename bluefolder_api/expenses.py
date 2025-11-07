# bluefolder_api/expenses.py

from .base import BlueFolderBase

class BlueFolderExpenses(BlueFolderBase):
    def __init__(self):
        super().__init__(domain="Expenses")
