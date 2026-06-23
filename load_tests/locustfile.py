from locust import HttpUser, task, between

class MLUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(3)
    def predict(self):
        user_id = 13
        amount = 200
        self.client.get(f"/predict/{user_id}?amount={amount}")

    @task(1)
    def health(self):
        self.client.get("/health")