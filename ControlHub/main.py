from test_extra_thread import *
from test_python_server import *
from task_manager import *
from state_manager import *


# main.py should state
# - Setup Wi-Fi connection
# - System restart process
# -

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    dummy_function_thread = threading.Thread(target=dummy_function)

    server_thread.start()
    dummy_function_thread.start()

    task_manager = TaskManager(server_queue)
    task_manager.start()

    state_manager = StateManager(server_queue, task_manager)
    state_manager.start()
