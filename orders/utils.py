import random

from orders.models import Order

GENERATE_LOGISTIC_TRACKING_BASE = 1000000000


def generate_logistic_tracking(user_id):
    while True:
        logistic_tracking = str(GENERATE_LOGISTIC_TRACKING_BASE + user_id) + str(random.randint(10, 99))
        if not Order.objects.filter(logistic_tracking=logistic_tracking).exists():
            break
    return logistic_tracking
