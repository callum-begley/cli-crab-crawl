#!/usr/bin/env python3
import os
import sys
import time
import random
import tty
import termios
import select

class CrabCrawl:
    def __init__(self):
        self.width = 60
        self.height = 5
        self.crab_pos = 5
        self.crab_y = self.height - 2  # Crab sits above the ground
        self.jump_height = 0
        self.max_jump = 2  # Reduced jump height
        self.is_jumping = False
        self.jump_velocity = 0
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.obstacle_speed = 1
        self.obstacle_frequency = 40
        self.frame_count = 0
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def get_key_press(self):
        """Check if a key is pressed without blocking"""
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None
        
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = 1.5  # Reduced jump velocity
            
    def update_crab(self):
        if self.is_jumping:
            self.crab_y -= self.jump_velocity
            self.jump_velocity -= 0.2  # Faster gravity
            
            if self.crab_y >= self.height - 2:  # Return to position above ground
                self.crab_y = self.height - 2
                self.is_jumping = False
                self.jump_velocity = 0
                
    def add_obstacle(self):
        if self.frame_count % self.obstacle_frequency == 0:
            obstacle_type = random.choice(['octopus', 'squid', 'fish'])
            y_pos = self.height - 2 if obstacle_type != 'fish' else self.height - 3
            self.obstacles.append({
                'x': self.width - 1,
                'y': y_pos,
                'type': obstacle_type
            })
            
    def update_obstacles(self):
        for obstacle in self.obstacles:
            obstacle['x'] -= self.obstacle_speed
            
        # Remove obstacles that are off screen
        self.obstacles = [obs for obs in self.obstacles if obs['x'] > 0]
        
    def check_collision(self):
        crab_x_range = range(self.crab_pos, self.crab_pos + 2)
        crab_y = int(self.crab_y)
        
        for obstacle in self.obstacles:
            obs_x_range = range(int(obstacle['x']), int(obstacle['x']) + 2)
            obs_y = int(obstacle['y'])
            
            # Check for collision
            x_overlap = any(x in obs_x_range for x in crab_x_range)
            
            # For fish (flying obstacles), check if crab collides when jumping
            # For ground obstacles, check if crab is on the ground
            if obstacle['type'] == 'fish':
                # Fish is at height-3, so check if crab is at height-3 or nearby
                y_overlap = abs(crab_y - obs_y) <= 1
            else:
                # Ground obstacles need exact match
                y_overlap = (crab_y == obs_y)
            
            if x_overlap and y_overlap:
                return True
        return False
        
    def draw_crab(self, y):
        if int(self.crab_y) == y:
            return '🦀'
        return None
        
    def draw_obstacle(self, x, y, obs_type):
        if int(y) == self.height - 2:
            if obs_type == 'octopus':
                return '🐙'
            elif obs_type == 'squid':
                return '🦑'
        elif int(y) == self.height - 3:
            if obs_type == 'fish':
                return '🐟'
        return None
        
    def render(self):
        self.clear_screen()
        
        print(f"\n  CRAB CRAWL - Score: {self.score}  (Press SPACE to jump, Q to quit)\n")
        
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                char = " "
                
                # Draw crab
                if x == self.crab_pos:
                    crab_char = self.draw_crab(y)
                    if crab_char:
                        line += crab_char
                        continue
                
                # Draw obstacles
                obstacle_drawn = False
                for obstacle in self.obstacles:
                    if int(obstacle['x']) == x:
                        obs_char = self.draw_obstacle(x, y, obstacle['type'])
                        if obs_char:
                            char = obs_char
                            obstacle_drawn = True
                            break
                
                # Draw ground
                if y == self.height - 1:
                    char = "-"
                
                line += char
                
            print("  " + line)
        
        print("\n  Press Q to quit anytime")
        
    def update_score(self):
        self.score += 1
        
        # Increase difficulty
        if self.score % 200 == 0 and self.obstacle_speed < 2:
            self.obstacle_speed += 0.1
        if self.score % 300 == 0 and self.obstacle_frequency > 25:
            self.obstacle_frequency -= 2
            
    def run(self):
        # Set terminal to raw mode for key detection
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            
            print("\n  Starting CRAB CRAWL in 3 seconds...")
            print("  Press SPACE to jump!")
            time.sleep(3)
            
            while not self.game_over:
                # Get input
                key = self.get_key_press()
                if key == ' ':
                    self.jump()
                elif key == 'q' or key == 'Q':
                    break
                    
                # Update game state
                self.update_crab()
                self.add_obstacle()
                self.update_obstacles()
                self.update_score()
                
                # Check collision
                if self.check_collision():
                    self.game_over = True
                    
                # Render
                self.render()
                
                self.frame_count += 1
                time.sleep(0.05)
                
            # Game over screen
            self.clear_screen()
            print("\n" * 5)
            print("  " + "=" * 40)
            print("  " + " " * 15 + "GAME OVER!")
            print("  " + f"      Final Score: {self.score}")
            print("  " + "=" * 40)
            print("\n" * 3)
            
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    game = CrabCrawl()
    game.run()
