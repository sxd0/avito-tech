import grpc
import asyncio
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp

from app.grpc import pvz_pb2, pvz_pb2_grpc
from app.dao.pvz import PVZDAO
from app.database import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession


class PVZService(pvz_pb2_grpc.PVZServiceServicer):
    async def GetPVZList(self, request, context):
        async with async_session_maker() as session:
            dao = PVZDAO(session=session)
            pvzs = await dao.find_all()
            response = pvz_pb2.GetPVZListResponse()
            for pvz in pvzs:
                ts = Timestamp()
                ts.FromDatetime(pvz.registration_date)
                response.pvzs.append(pvz_pb2.PVZ(
                    id=str(pvz.id),
                    registration_date=ts,
                    city=pvz.city
                ))
            return response


async def serve():
    print("Вошли в async serve()")
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    pvz_pb2_grpc.add_PVZServiceServicer_to_server(PVZService(), server)
    server.add_insecure_port('[::]:3000')
    await server.start()
    print("gRPC server is running on port 3000")
    await server.wait_for_termination()


if __name__ == "__main__":
    print("Запускаем сервер gRPC...")
    asyncio.run(serve())
