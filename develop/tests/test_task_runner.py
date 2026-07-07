import time

from services.task_runner import TaskRunner


def task():

    print("Inicio")

    time.sleep(2)

    print("Fin")


runner = TaskRunner()

thread = runner.run(task)

thread.join()

print()
print("Prueba satisfactoria.")