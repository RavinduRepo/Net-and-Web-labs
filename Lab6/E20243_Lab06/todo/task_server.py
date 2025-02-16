"""TODO:
    * Implement error handling in TaskapiImpl methods
    * Implement saveTasks, loadTasks
    * Implement TaskapiImpl.editTask (ignoring write conflicts)
    * Fix data race in TaskapiImpl.addTask
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import logging
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

class TaskapiImpl(task_pb2_grpc.TaskapiServicer):
    def __init__(self, taskfile: str):
        self.taskfile = taskfile
        self.task_id = 0

    def __enter__(self):
        """Load tasks from self.taskfile"""
        self.tasks = {}
        self.task_id = 0

        if Path(self.taskfile).exists() and Path(self.taskfile).stat().st_size > 0:
            with open(self.taskfile, mode="rb") as t:
                tasklist = task_pb2.Tasks()
                tasklist.ParseFromString(t.read())
                logging.info(f"Loaded data from {self.taskfile}")
                
                # Convert tasklist to a dictionary
                self.tasks = {t.id: t for t in tasklist.pending}

                # Ensure new task IDs continue sequentially
                if self.tasks:
                    self.task_id = max(self.tasks.keys()) + 1

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Save tasks to self.taskfile"""
        with open(self.taskfile, mode="wb") as t:
            tasklist = task_pb2.Tasks()
            tasklist.pending.extend(self.tasks.values()) # Convert dictionary to a Task object
            t.write(tasklist.SerializeToString())
            logging.info(f"Saved data to {self.taskfile}")

    def addTask(self, request: wrappers_pb2.StringValue, context) -> task_pb2.Task:
        logging.debug(f"addTask parameters {pformat(request)}")
        if len(request.value) > MAXLEN:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Task description exceeds {MAXLEN} characters")
            return task_pb2.Task()

        t = task_pb2.Task(id=self.task_id, description=request.value, state=task_pb2.TaskState.OPEN)
        self.tasks[self.task_id] = t
        self.task_id += 1
        return t

    def delTask(self, request: wrappers_pb2.UInt64Value, context) -> task_pb2.Task:
        logging.debug(f"delTask parameters {pformat(request)}")

        if request.value not in self.tasks:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(f"Task {request.value} not found")
            return task_pb2.Task()

        return self.tasks.pop(request.value)

    def listTasks(self, request: task_pb2.TaskQuery, context) -> task_pb2.Tasks:
        logging.debug(f"listTasks parameters {pformat(request)}")

        # If request.selected is empty, return all tasks
        if not request.selected:
            return task_pb2.Tasks(pending=list(self.tasks.values()))

        # Filter tasks based on request.selected
        filtered_tasks = [task for task in self.tasks.values() if task.state in request.selected]

        return task_pb2.Tasks(pending=filtered_tasks)

    def editTask(self, request: task_pb2.Task, context) -> task_pb2.Task:
        logging.debug(f"editTask parameters {pformat(request)}")
        # Ensure task ID exists
        if request.id not in self.tasks:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(f"Task {request.id} not found")
            return task_pb2.Task() # Return empty task

        # Validate task description length
        if len(request.description) > MAXLEN:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Task description exceeds {MAXLEN} characters")
            return task_pb2.Task()

        current_task = self.tasks[request.id]

        # Define allowed transitions
        allowed_transitions = {
            task_pb2.TaskState.OPEN: {task_pb2.TaskState.ASSIGNED, task_pb2.TaskState.CANCELLED},
            task_pb2.TaskState.ASSIGNED: {task_pb2.TaskState.PROGRESSING},
            task_pb2.TaskState.PROGRESSING: {task_pb2.TaskState.DONE, task_pb2.TaskState.CANCELLED},
            task_pb2.TaskState.DONE: set(),
            task_pb2.TaskState.CANCELLED: set()
        }

        # Ensure the state transition is allowed
        if request.state not in allowed_transitions.get(current_task.state, {}):
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Illegal state transition from {current_task.state} to {request.state}")
            return task_pb2.Task()

        # Update the task
        current_task.description = request.description
        current_task.state = request.state

        return current_task

    # Two two versions of TaskapiImpl.editTask that implement the different concurrency semantics
    # The nondestructive version will ignore write conflicts
    def nondestructive_editTask(self, request: task_pb2.Task, context) -> task_pb2.Task:
        logging.debug(f"editTask parameters {pformat(request)}")
        # Ensure task ID exists
        if request.id not in self.tasks:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(f"Task {request.id} not found")
            return task_pb2.Task() # Return empty task

        # Validate task description length
        if len(request.description) > MAXLEN:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Task description exceeds {MAXLEN} characters")
            return task_pb2.Task()

        # Store previous versions in a seperate history dictionary
        if not hasattr(self, 'history'):
            self.history = {}

        if request.id not in self.history:
            self.history[request.id] = []

        # Save the old version before modifying
        self.history[request.id].append(self.tasks[request.id])

        # Update the task
        self.tasks[request.id].description = request.description
        return self.tasks[request.id]

    # The destructive version will delete the old task
    def destructive_editTask(self, request: task_pb2.Task, context) -> task_pb2.Task:
        logging.debug(f"editTask parameters {pformat(request)}")
        # Ensure task ID exists
        if request.id not in self.tasks:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(f"Task {request.id} not found")
            return task_pb2.Task()

        # Validate task description length
        if len(request.description) > MAXLEN:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Task description exceeds {MAXLEN} characters")
            return task_pb2.Task()

        # Delete the old task
        old_task = self.tasks.pop(request.id)

        # Create a new task with a new ID
        new_task = task_pb2.Task(id=self.task_id, description=request.description, status=old_task.status)
        self.tasks[self.task_id] = new_task
        self.task_id += 1

        return new_task


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
        except KeyboardInterrupt:
            taskserver.stop(0)
            logging.info("Taskapi server stopped")
