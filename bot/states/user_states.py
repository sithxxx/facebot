from aiogram.fsm.state import State, StatesGroup

class AnalysisFlow(StatesGroup):
    waiting_for_photo = State()     # after /start — waiting for user to send photo
    waiting_for_gender = State()    # photo received — waiting for gender selection
    waiting_for_payment = State()   # gender selected — waiting for payment
    processing = State()            # payment done — analysis running
