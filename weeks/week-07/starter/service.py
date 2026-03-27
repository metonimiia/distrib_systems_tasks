import grpc
from concurrent import futures

import service_pb2
import service_pb2_grpc


class LogsServiceImplementation(service_pb2_grpc.LogsServiceServicer):

    def CreateLog(self, request, context):
        log_text = request.log
        level = request.level

        print("Received log:")
        print("log =", log_text)
        print("level =", level)

        return service_pb2.CreateLogResponse(
            message=f"Log '{log_text}' with level '{level}' created"
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    service_pb2_grpc.add_LogsServiceServicer_to_server(
        LogsServiceImplementation(),
        server
    )

    server.add_insecure_port('[::]:50051')

    server.start()
    print("gRPC server started on port 50051")

    server.wait_for_termination()


if __name__ == '__main__':
    serve()