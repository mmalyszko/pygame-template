class Viewport:
    def __init__(self, world_width: float, world_height: float, width: float, height: float):
        self.world_width = world_width
        self.world_height = world_height
        self.width = width
        self.height = height
        self.offset_x = 0.0
        self.offset_y = 0.0

    def center_on(self, focus_x: float, focus_y: float) -> None:
        self.offset_x = max(0.0, min(self.world_width - self.width, focus_x - self.width / 2))
        self.offset_y = max(0.0, min(self.world_height - self.height, focus_y - self.height / 2))

    def world_to_viewport(self, world_x: float, world_y: float, scale: float = 1) -> tuple[float, float]:
        return (world_x - self.offset_x) * scale, (world_y - self.offset_y) * scale

    def viewport_to_world(self, viewport_x: float, viewport_y: float, scale: float = 1) -> tuple[float, float]:
        return viewport_x / scale + self.offset_x, viewport_y / scale + self.offset_y
