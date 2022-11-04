from typing import List, Optional
from fastapi import Request

class RegistrationForm:
    def __init__(self, request:Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.confirm_password: Optional[str] = None
    
    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")
        self.confirm_password = form.get("confirm_password")
    
    async def is_valid(self):
        if not self.username or not (self.username.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if self.password != self.confirm_password:
            self.errors.append("Password is not the same")
        if not self.errors:
            return True
        return False
