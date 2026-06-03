from dreema.requests import Request
from dreema.responses import response
from dreema.responses import SysCodes
from models.sampleModel import SampleModel

class SampleController:

    
    @staticmethod
    async def welcome(request: Request):
        return response(message="Setup completed", status=SysCodes.SETUP_COMPLETED)

    @staticmethod
    async def sampleCreate(request: Request):
        body = await request.body()
        mod = SampleModel()
        return await mod.create(body.data)

    @staticmethod
    async def sampleRead(request: Request):
        # read all samples  
        mod = SampleModel()
        return await mod.read(params={'include':['name'], 'limit':5, 'skip':1, 'sort': 1, 'sortfield':'name'})

    @staticmethod
    async def sampleUpdate(request: Request):
        body = await request.trimApplyRules({
            'id': 'required',
            'name':'required',
        })

        # validate request body
        if body.status < 0:
            return response(body, custom=True)

        mod = SampleModel()
        return await mod.update(filters={'id':body.data.id}, data={'name':body.data.name})

    @staticmethod
    async def sampleDelete(request: Request):
        body = await request.trimApplyRules({
            'id': 'required',
        }, request.params()) # id on request parameter

        if body.status < 0:
            return response(body, custom=True)

        mod = SampleModel()
        return await mod.delete(filters={'id':body.data.id})