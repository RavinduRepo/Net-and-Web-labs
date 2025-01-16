import logging
from concurrent.futures import ThreadPoolExecutor
from grpc import server, StatusCode
import task_pb2, task_pb2_grpc


class TaskapiImpl:
    """'Implementation of the Taskapi service"""

    def __init__(self):
        self.tasks = {} # space (dictionary) to keep tasks
        self.next_id = 1 # task id

    def addTask(self, request, context):
        logging.info(f"adding task {request.description}")# propt a log
        current_task_id = self.next_id
        self.tasks[current_task_id] = request.description # store the next task with next_id
        self.next_id += 1 # increment the id
        return task_pb2.Id(id=current_task_id) # return the id of added task

    def delTask(self, request, context):
        logging.info(f"deleting task {request.id}")
        if request.id in self.tasks:
            description = self.tasks.pop(request.id) # remove the task and take the description
            return task_pb2.Task(id = request.id, description=description) # return the task with id and description
        else:# return error msg if task not found
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(f'Task of id:{request.id} not found')
            return task_pb2.Task() # return empty task since need to return Task

    def listTasks(self, request, context):
        logging.info("returning task list") # prompt a log
        tasks_list = [task_pb2.Task(id=id, description=desc) for id, desc in self.tasks.items()] # get all tasks
        return task_pb2.Tasks(tasks=tasks_list) # return the list of all tasks as a Tasks obj


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with ThreadPoolExecutor(max_workers=1) as pool:
        taskserver = server(pool)
        task_pb2_grpc.add_TaskapiServicer_to_server(TaskapiImpl(), taskserver)
        taskserver.add_insecure_port("[::]:50051")
        try:
            taskserver.start()
            logging.info("Taskapi ready to serve requests")
            taskserver.wait_for_termination()
        except:
            logging.info("Shutting down server")
            taskserver.stop(None)
