from application.app_controller import AppController


controller = AppController()

controller.start_meeting()

controller.pause_meeting()

controller.resume_meeting()

controller.stop_meeting()

print("Controller OK")