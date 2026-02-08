"""Player controller with first/third person camera and movement."""

from ursina import *
import config


class PlayerController(Entity):
    """Advanced player controller with first/third person toggle."""

    def __init__(self, character, **kwargs):
        super().__init__()
        self.character = character

        # Movement settings
        self.speed = config.PLAYER_SPEED
        self.sprint_multiplier = config.PLAYER_SPRINT_MULTIPLIER
        self.jump_height = config.PLAYER_JUMP_HEIGHT
        self.gravity = config.GRAVITY

        # State
        self.grounded = False
        self.velocity_y = 0
        self.sprinting = False
        self.crouching = False

        # Camera mode
        self.first_person = True
        self.third_person_distance = 5

        # Create player model (visible in third person)
        self.model_entity = Entity(
            parent=self,
            model='cube',
            color=color.rgb(100, 150, 200),
            scale=(1, 2, 1),
            visible=False  # Hidden in first person
        )

        # Camera pivot for third person
        self.camera_pivot = Entity(parent=self, y=1.5)

        # Set up camera
        camera.parent = self.camera_pivot
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)

        # Mouse look
        self.mouse_sensitivity = Vec2(config.MOUSE_SENSITIVITY, config.MOUSE_SENSITIVITY)
        self.rotation_y = 0
        self.camera_pivot.rotation_x = 0

        # Collision
        self.collider = BoxCollider(self, center=(0, 1, 0), size=(1, 2, 1))

        # Position
        self.position = kwargs.get('position', (0, 2, 0))

        # Lock mouse
        mouse.locked = True

    def update(self):
        # Mouse look
        if mouse.locked:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity.x
            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity.y
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        # Calculate movement direction
        move_direction = Vec3(0, 0, 0)

        if held_keys['w'] or held_keys['up arrow']:
            move_direction += self.forward
        if held_keys['s'] or held_keys['down arrow']:
            move_direction -= self.forward
        if held_keys['d'] or held_keys['right arrow']:
            move_direction += self.right
        if held_keys['a'] or held_keys['left arrow']:
            move_direction -= self.right

        # Normalize diagonal movement
        if move_direction.length() > 0:
            move_direction = move_direction.normalized()

        # Sprint
        current_speed = self.speed
        if held_keys['shift'] and self.character.use_stamina(10 * time.dt):
            current_speed *= self.sprint_multiplier
            self.sprinting = True
        else:
            self.sprinting = False

        # Apply movement
        self.position += move_direction * current_speed * time.dt

        # Gravity
        ray = raycast(self.position + Vec3(0, 1, 0), Vec3(0, -1, 0), distance=1.1, ignore=[self])
        self.grounded = ray.hit

        if self.grounded:
            self.velocity_y = 0
            # Snap to ground
            if ray.distance < 1:
                self.y = ray.world_point.y
        else:
            self.velocity_y -= self.gravity * 30 * time.dt
            self.y += self.velocity_y * time.dt

        # Prevent falling through floor
        if self.y < -10:
            self.y = 5
            self.velocity_y = 0

        # Regenerate character stats
        self.character.regenerate(time.dt)

    def input(self, key):
        # Jump
        if key == 'space' and self.grounded:
            if self.character.use_stamina(10):
                self.velocity_y = self.jump_height * 5
                self.grounded = False

        # Toggle camera mode
        if key == 'v':
            self.toggle_camera_mode()

        # Crouch
        if key == 'c':
            self.crouching = not self.crouching
            if self.crouching:
                self.speed = config.PLAYER_SPEED * 0.5
                self.model_entity.scale_y = 1.2
            else:
                self.speed = config.PLAYER_SPEED
                self.model_entity.scale_y = 2

    def toggle_camera_mode(self):
        """Toggle between first and third person camera."""
        self.first_person = not self.first_person

        if self.first_person:
            camera.position = (0, 0, 0)
            self.model_entity.visible = False
        else:
            camera.position = (0, 2, -self.third_person_distance)
            self.model_entity.visible = True

    def get_look_direction(self):
        """Get the direction the player is looking."""
        return self.camera_pivot.forward

    def interact(self):
        """Check for interactable objects in front of player."""
        origin = self.position + Vec3(0, 1.5, 0)
        direction = self.get_look_direction()

        ray = raycast(origin, direction, distance=3, ignore=[self, self.model_entity])

        if ray.hit:
            return ray.entity
        return None
