from grpc_tools import protoc
import pkg_resources

proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')

protoc.main([
    'grpc_tools.protoc',
    f'-Iapp/grpc',
    f'-I{proto_include}',  # добавим путь к google/protobuf
    '--python_out=app/grpc',
    '--grpc_python_out=app/grpc',
    'app/grpc/pvz.proto',
])
