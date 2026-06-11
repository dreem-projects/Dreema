from dreema.requests import Request
from dreema.responses import response
from dreema.responses import SysCodes
from models.usersModel import UsersModel

class UsersController:

    @staticmethod
    async def welcome():
        return response(message="Setup completed", status=SysCodes.SETUP_COMPLETED)

    @staticmethod
    async def testCreate(request: Request):
        body = await request.body()
        mod = UsersModel()
        return await mod.create(body.data)

    @staticmethod
    async def testRead():
        # read all samples  
        mod = UsersModel()
        return await mod.read(params={'include':['name'], 'limit':5, 'skip':1, 'sort': 1, 'sortfield':'name'})

    @staticmethod
    async def testUpdate(request: Request):
        body = await request.trimApplyRules({
            'id': 'required',
            'name':'required',
        })

        # validate request body
        if body.status < 0:
            return response(body, custom=True)

        mod = UsersModel()
        return await mod.update(filters={'id':body.data.id}, data={'name':body.data.name})

    @staticmethod
    async def testDelete(request: Request):
        body = await request.trimApplyRules({
            'id': 'required',
        }, request.params()) # id on request parameter

        if body.status < 0:
            return response(body, custom=True)

        mod = UsersModel()
        return await mod.delete(filters={'id':body.data.id})