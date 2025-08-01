import numpy as np
import pygame
from track import Track
from car import Car


class Environment:
    """
    Reinforcement learning environment for a racing car simulation.
    Provides control, physics, collision, reward logic, and rendering.
    """

    SCREEN_WIDTH = 1200 #TODO this should probably be moved up to simulation
    SCREEN_HEIGHT = 800
    MAX_STEPS = 1200

    def __init__(self, track):
        
        self.track = track
        self.car = Car(self.track.start_position, self.track.start_angle)

        self.current_step = 0
        self.last_distance = 0

    def reset(self):
        """Reset the environment to its initial state."""
        self.car.reset(self.track.start_position, self.track.start_angle)
        self.current_step = 0
        self.last_distance = 0
        return np.array(self._get_state(), dtype=np.float32)

    def step(self, action):
        """
        Execute one step in the environment.

        Args:
            action (int): The action to take (0-6).

        Returns:
            tuple: (state, reward, done, info)
        """
        self.current_step += 1
        self._execute_action(action)
        self.car.update_position()
        self._check_collision()

        reward = self._calculate_reward()
        done = self._is_done()
        state = self._get_state()

        info = {
            "distance_traveled": self.car.total_distance,
            "is_alive": self.car.is_alive,
            "speed": self.car.speed,
            "position": self.car.position.copy(),
            "crashed": not self.car.is_alive and self.current_step < self.MAX_STEPS,
        }

        return np.array(state, dtype=np.float32), reward, done, info

    def _execute_action(self, action):
        """Apply the chosen action to the car."""
        if action == 0:
            pass
        elif action == 1:
            self.car.increase_speed()
        elif action == 2:
            self.car.decrease_speed()
        elif action == 3:
            self.car.turn_left()
        elif action == 4:
            self.car.turn_right()
        elif action == 5:
            self.car.increase_speed()
            self.car.turn_left()
        elif action == 6:
            self.car.increase_speed()
            self.car.turn_right()

    def _check_collision(self):
        """Kill the car if any important part is off-track."""
        if not self.car.is_alive:
            return

        car_rect = self.car.get_rect()
        critical_points = [
            (car_rect.left, car_rect.top),
            (car_rect.right, car_rect.top),
            (car_rect.left, car_rect.bottom),
            (car_rect.right, car_rect.bottom),
            (car_rect.centerx, car_rect.centery),
        ]

        if any(not self.track.is_on_track(p) for p in critical_points):
            self.car.kill_car()

    def _calculate_reward(self):
        """Reward for distance progress and staying alive."""
        if not self.car.is_alive:
            return -200 #TODO magic numbers in function

        delta_distance = self.car.total_distance - self.last_distance
        self.last_distance = self.car.total_distance
        
        speed_factor = max(0.3, self.car.speed / self.car.max_speed)
        progress_reward = delta_distance * speed_factor * 10
    
        return progress_reward

    def _get_state(self):
        """Return current car state."""
        return self.car.get_state(self.track)

    def _is_done(self):
        """Episode ends on death or max steps."""
        return not self.car.is_alive or self.current_step >= self.MAX_STEPS