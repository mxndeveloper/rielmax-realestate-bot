from locust import HttpUser, task, between

class TelegramBotUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def send_start(self):
        # This simulates hitting your bot's webhook (if you switch to webhook mode)
        # For polling mode, load testing is less relevant; but you can still test the AI endpoint directly.
        pass