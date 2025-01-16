from typing import Sequence, Mapping, Tuple
import random, string, logging, grpc
import task_pb2, task_pb2_grpc


def random_string_generator(str_size, allowed_chars):
    return "".join(random.choice(allowed_chars) for x in range(str_size))


# Test that will be used to grade addTask
def test_add(stub, count) -> Mapping[int, str]:
    tasks = {} 
    for i in range(count):
        desc = random_string_generator(99, string.ascii_letters)# Generate a randomm string
        response = stub.addTask(task_pb2.TaskDesc(description=desc))# this adds the task to the server.
        tasks[response.id] = desc # add task to the dictionary

    return tasks


# Test that will be used to grade listTask
def test_list(stub, tasks) -> None:
    response = stub.listTasks(task_pb2.Empty())
    for t in response.tasks:
        # Is the proper task desc is returned for this id?
        assert t.description == tasks[t.id] # updated to 'description' fom 'desc' since in the .proto desscribed task to have 'description'


# Test that will be used to grade delTask
def test_del(stub, task_ids) -> None:
    for i in task_ids:
        stub.delTask(task_pb2.Id(id=i))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = task_pb2_grpc.TaskapiStub(channel) # access the created methods (by the server) using Stub

        tasks = test_add(stub, 10)
        logging.info(f"added tasks {tasks}")
        test_list(stub, tasks)
        test_del(stub, tasks.keys())
