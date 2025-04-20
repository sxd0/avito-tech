from grpc_tools import protoc
import pkg_resources
import os

proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')

os.makedirs("app/grpc", exist_ok=True)

protoc.main([
    'grpc_tools.protoc',
    '--proto_path=app',              
    f'-I{proto_include}',   
    '--python_out=app',
    '--grpc_python_out=app',
    'app/grpc/pvz.proto'
])
