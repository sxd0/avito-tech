from app.dao.base import BaseDAO
from app.models.users import Users


class UsersDAO(BaseDAO):
    model = Users