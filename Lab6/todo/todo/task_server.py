"""TODO:
    * Implement error handling in TaskapiImpl methods
    * Implement saveTasks, loadTasks
    * Implement TaskapiImpl.editTask (ignoring write conflicts)
    * Fix data race in TaskapiImpl.addTask
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
import threading
from pprint import pformat
from typing import Mapping, Sequence, Tuple

from google.protobuf import (
    any_pb2,
    api_pb2,
    duration_pb2,
    empty_pb2,
    field_mask_pb2,
    source_context_pb2,
    struct_pb2,
    timestamp_pb2,
    type_pb2,
    wrappers_pb2,
)
from grpc import server, StatusCode
import task_pb2, task_pb2_grpc

# Define MAXLEN for task description
MAXLEN = 1024

class TaskapiImpl:
    def __init__(self, taskfile: str):
        self.taskfile = taskfile
        self.task_id = 0
        self.tasks: Mapping[int, task_pb2.Task] = {}
        self.lock = threading.Lock()

    def __enter__(self):
        """Load tasks from self.taskfile"""
        try:
            with open(self.taskfile, mode="rb") as t:
                tasklist = task_pb2.Tasks()
                tasklist.ParseFromString(t.read())
                self.tasks = {task.id: task for task in tasklist.pending}
                self.task_id = max(self.tasks.keys(), default=0) + 1
                logging.info(f"Loaded data from {self.taskfile}")
        except FileNotFoundError:
            self.tasks = {}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Save tasks to self.taskfile"""
        with open(self.taskfile, mode="wb") as t:
            tasks = task_pb2.Tasks(pending=list(self.tasks.values()))
            t.write(tasks.SerializeToString())
            logging.info(f"Saved data to {self.taskfile}")

    def addTask(self, request: wrappers_pb2.StringValue, context) -> task_pb2.Task:
        """Adds a new task, ensuring mutual exclusion."""
        if len(request.value) > MAXLEN:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Task description exceeds 1024 characters.")
            return task_pb2.Task()

        with self.lock:
            t = task_pb2.Task(id=self.task_id, description=request.value)
            self.tasks[self.task_id] = t
            self.task_id += 1
        return t

    def delTask(self, request: wrappers_pb2.UInt64Value, context) -> task_pb2.Task:
        """Deletes a task if it exists."""
        if request.value not in self.tasks:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details("Task ID not found.")
            return task_pb2.Task()

        with self.lock:
            return self.tasks.pop(request.value)

    def editTask(self, request: task_pb2.Task, context) -> task_pb2.Task:
        """Edits an existing task."""
        if request.id not in self.tasks:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details("Task ID not found.")
            return task_pb2.Task()

        if len(request.description) > MAXLEN:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Task description exceeds 1024 characters.")
            return task_pb2.Task()

        with self.lock:
            self.tasks[request.id].description = request.description
        return self.tasks[request.id]

    def listTasks(self, request: empty_pb2.Empty, context) -> task_pb2.Tasks:
        """Lists all tasks."""
        return task_pb2.Tasks(pending=list(self.tasks.values()))

TASKFILE = "tasklist.protobuf"
if __name__ == "__main__":
    Path(TASKFILE).touch()
    logging.basicConfig(level=logging.DEBUG)

    with ThreadPoolExecutor(max_workers=1) as pool, TaskapiImpl(
        TASKFILE
    ) as taskapiImpl:
        taskserver = server(pool)
        task_pb2_grpc.add_TaskapiServicer_to_server(taskapiImpl, taskserver)
        taskserver.add_insecure_port("[::]:50051")
        try:
            taskserver.start()
            logging.info("Taskapi ready to serve requests")
            taskserver.wait_for_termination()
        except:
            logging.info("Shutting down server")
            taskserver.stop(None)
