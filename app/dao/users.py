from app.dao.base import BaseDAO
from app.models.users import Users

class UsersDAO(BaseDAO):
    model = Users

    def __init__(self, session):
        super().__init__(session)
