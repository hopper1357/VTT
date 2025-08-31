import pygame
import math
from .view import View
from src.map import GridType
from src.hex import roffset_to_cube, Hex, roffset_from_cube

class MapView(View):
    """A view that renders a map."""

    def __init__(self, app):
        super().__init__(app)
        self.map_manager = self.app.engine.get_map_manager()
        self.cell_size = 40
        self.grid_color = (100, 100, 100)
        self.selected_object = None
        self.dragged_object = None
        self.highlight_color = (255, 255, 0) # Yellow
        self.map_offset = (50, 50)
        self.font = pygame.font.Font(None, 30)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                grid_pos = self._pixel_to_grid(event.pos)
                if grid_pos:
                    active_map = self.map_manager.get_active_map()
                    if active_map:
                        found_obj = None
                        for obj in reversed(active_map.objects):
                            if (obj.x, obj.y) == grid_pos:
                                found_obj = obj
                                break
                        self.selected_object = found_obj
                        self.dragged_object = found_obj
                        if self.selected_object:
                            print(f"Selected object: {self.selected_object.id} at {grid_pos}")
                        else:
                            print(f"No object at {grid_pos}")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.dragged_object:
                    grid_pos = self._pixel_to_grid(event.pos)
                    if grid_pos:
                        active_map = self.map_manager.get_active_map()
                        if active_map:
                            self.app.engine.get_command_handler().parse_and_handle(f"object move {self.dragged_object.id} {active_map.name} {grid_pos[0]} {grid_pos[1]}")
                            print(f"Moved object {self.dragged_object.id} to {grid_pos}")
                    self.dragged_object = None

    def draw(self, screen):
        """Draws the current map on the screen."""
        map_list = self.map_manager.list_maps()
        active_map = None
        if map_list:
            active_map = self.map_manager.get_map(map_list[0])

        if not active_map:
            font = pygame.font.Font(None, 48)
            text_surface = font.render("No active map", True, (150, 150, 150))
            text_rect = text_surface.get_rect(center=screen.get_rect().center)
            screen.blit(text_surface, text_rect)
            return

        if active_map.grid_type == GridType.SQUARE:
            self._draw_square_grid(screen, active_map)
        elif active_map.grid_type == GridType.HEX:
            self._draw_hex_grid(screen, active_map)

        if self.selected_object:
            self._highlight_selected(screen, active_map)

    def _highlight_selected(self, screen, game_map):
        """Draws a highlight around the selected object."""
        if not self.selected_object:
            return

        if game_map.grid_type == GridType.SQUARE:
            rect = pygame.Rect(self.map_offset[0] + self.selected_object.x * self.cell_size,
                               self.map_offset[1] + self.selected_object.y * self.cell_size,
                               self.cell_size, self.cell_size)
            pygame.draw.rect(screen, self.highlight_color, rect, 3)
        elif game_map.grid_type == GridType.HEX:
            pixel_x, pixel_y = self._offset_to_pixel(self.selected_object.x, self.selected_object.y)
            points = self._get_hex_points(pixel_x, pixel_y)
            pygame.draw.polygon(screen, self.highlight_color, points, 3)

    def _draw_square_grid(self, screen, game_map):
        """Draws a square grid and the objects on it."""
        # Draw grid lines
        for x in range(game_map.width + 1):
            start_pos = (self.map_offset[0] + x * self.cell_size, self.map_offset[1])
            end_pos = (self.map_offset[0] + x * self.cell_size, self.map_offset[1] + game_map.height * self.cell_size)
            pygame.draw.line(screen, self.grid_color, start_pos, end_pos)
        for y in range(game_map.height + 1):
            start_pos = (self.map_offset[0], self.map_offset[1] + y * self.cell_size)
            end_pos = (self.map_offset[0] + game_map.width * self.cell_size, self.map_offset[1] + y * self.cell_size)
            pygame.draw.line(screen, self.grid_color, start_pos, end_pos)

        # Draw objects
        for obj in game_map.objects:
            pixel_x = self.map_offset[0] + obj.x * self.cell_size + self.cell_size // 2
            pixel_y = self.map_offset[1] + obj.y * self.cell_size + self.cell_size // 2

            text_surface = self.font.render(obj.display_char, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(pixel_x, pixel_y))
            screen.blit(text_surface, text_rect)

    def _draw_hex_grid(self, screen, game_map):
        """Draws a hexagonal grid and the objects on it."""
        # Draw grid polygons
        for r_offset in range(game_map.height):
            for c_offset in range(game_map.width):
                pixel_x, pixel_y = self._offset_to_pixel(c_offset, r_offset)
                points = self._get_hex_points(pixel_x, pixel_y)
                pygame.draw.polygon(screen, self.grid_color, points, 1)

        # Draw objects
        for obj in game_map.objects:
            pixel_x, pixel_y = self._offset_to_pixel(obj.x, obj.y)
            text_surface = self.font.render(obj.display_char, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(pixel_x, pixel_y))
            screen.blit(text_surface, text_rect)

    def _offset_to_pixel(self, col, row):
        """Converts odd-r offset coordinates to pixel coordinates (pointy-top)."""
        size = self.cell_size
        x = size * math.sqrt(3) * (col + 0.5 * (row & 1))
        y = size * 3/2 * row
        x += self.map_offset[0]
        y += self.map_offset[1]
        return x, y

    def _get_hex_points(self, center_x, center_y):
        """Calculates the 6 points of a hex polygon."""
        points = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.pi / 180 * angle_deg
            x = center_x + self.cell_size * math.cos(angle_rad)
            y = center_y + self.cell_size * math.sin(angle_rad)
            points.append((x, y))
        return points

    def _pixel_to_grid(self, pixel_pos):
        """Converts pixel coordinates to grid coordinates (square or hex)."""
        active_map = self.map_manager.get_active_map()
        if not active_map:
            return None

        if active_map.grid_type == GridType.SQUARE:
            grid_x = (pixel_pos[0] - self.map_offset[0]) // self.cell_size
            grid_y = (pixel_pos[1] - self.map_offset[1]) // self.cell_size
            return (grid_x, grid_y)

        elif active_map.grid_type == GridType.HEX:
            hex_coords = self._pixel_to_hex(pixel_pos)
            offset_coords = roffset_from_cube(hex_coords)
            return (offset_coords.col, offset_coords.row)

        return None

    def _pixel_to_hex(self, pixel_pos):
        """Converts pixel coordinates to hex axial coordinates."""
        size = self.cell_size
        x, y = pixel_pos[0] - self.map_offset[0], pixel_pos[1] - self.map_offset[1]

        q = (math.sqrt(3)/3 * x - 1/3 * y) / size
        r = (2/3 * y) / size

        return self._hex_round(Hex(q, r, -q-r))

    def _hex_round(self, h_frac):
        """Rounds fractional cube coordinates to the nearest hex."""
        q = int(round(h_frac.q))
        r = int(round(h_frac.r))
        s = int(round(h_frac.s))

        q_diff = abs(q - h_frac.q)
        r_diff = abs(r - h_frac.r)
        s_diff = abs(s - h_frac.s)

        if q_diff > r_diff and q_diff > s_diff:
            q = -r - s
        elif r_diff > s_diff:
            r = -q - s
        else:
            s = -q - r

        return Hex(q, r, s)
