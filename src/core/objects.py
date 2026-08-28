class GameObject:
    _next_uid = 1

    def __init__(self, center_x: float, center_y: float):
        self.uid = GameObject._next_uid
        GameObject._next_uid += 1

        self.center_x = center_x
        self.center_y = center_y
        self.is_active = True

    def update(self, dt: float) -> None:
        pass
