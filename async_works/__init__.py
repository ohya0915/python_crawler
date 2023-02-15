
from blinker import Namespace

my_signals = Namespace()


USER_CREATED = my_signals.signal("user_created")
USER_FORGOT_PASSWORD = my_signals.signal("user_forgot_password")
