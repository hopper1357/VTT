import pygame
import pygame_gui
from .map_view import MapView

class App:
    """The main GUI application."""

    def __init__(self, engine):
        # Ensure Pygame and font system initialized
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        self.engine = engine
        self.is_running = False
        self.screen = None
        self.clock = None
        self.width = 1280
        self.height = 720

        # Map view
        self.map_view = MapView(self)

        # UI state
        self.ui_manager = None
        self.create_char_window = None
        self.char_name_input = None
        self.char_hp_input = None
        self.is_placing_token = False
        self.token_to_place_id = None

        # Ensure a default map exists
        try:
            self.engine.get_command_handler().parse_and_handle("map create testmap 20 15")
        except Exception as e:
            print(f"Warning: Could not create default map: {e}")

    def run(self):
        """Starts the main application loop."""
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Modular VTT")
        self.clock = pygame.time.Clock()
        self.is_running = True

        self.ui_manager = pygame_gui.UIManager((self.width, self.height))

        # GUI Buttons and Panels
        self.create_hex_map_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.width - 170, 10), (160, 40)),
            text='Create Hex Map',
            manager=self.ui_manager
        )

        info_panel_rect = pygame.Rect(10, self.height - 160, 300, 150)
        info_panel = pygame_gui.elements.UIPanel(
            relative_rect=info_panel_rect,
            starting_height=1,
            manager=self.ui_manager
        )
        self.info_text_box = pygame_gui.elements.UITextBox(
            html_text="No object selected.",
            relative_rect=pygame.Rect(0, 0, 280, 110),
            manager=self.ui_manager,
            container=info_panel
        )

        # Character panel
        char_panel_rect = pygame.Rect(self.width - 210, 60, 200, 300)
        char_panel = pygame_gui.elements.UIPanel(
            relative_rect=char_panel_rect,
            starting_height=1,
            manager=self.ui_manager
        )
        self.char_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(0, 0, 180, 200),
            item_list=[],
            manager=self.ui_manager,
            container=char_panel
        )
        self.create_char_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 220, 160, 30),
            text='Create Character',
            manager=self.ui_manager,
            container=char_panel
        )
        self.place_token_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 260, 160, 30),
            text='Place Token',
            manager=self.ui_manager,
            container=char_panel
        )
        self.place_token_button.disable()

        # Initiative panel
        init_panel_rect = pygame.Rect(self.width - 210, 370, 200, 300)
        init_panel = pygame_gui.elements.UIPanel(
            relative_rect=init_panel_rect,
            starting_height=1,
            manager=self.ui_manager
        )
        self.init_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(0, 0, 180, 200),
            item_list=[],
            manager=self.ui_manager,
            container=init_panel
        )
        self.add_to_init_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 220, 160, 30),
            text='Add to Initiative',
            manager=self.ui_manager,
            container=init_panel
        )
        self.roll_init_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 260, 160, 30),
            text='Roll Initiative',
            manager=self.ui_manager,
            container=init_panel
        )

        # Safe font initialization
        self.font = pygame.font.Font(None, 36)

        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self._handle_button_press(event)

                if event.type == pygame_gui.UI_WINDOW_CLOSE:
                    if event.ui_element == self.create_char_window:
                        self.create_char_window = None

                self.map_view.handle_event(event)
                self.ui_manager.process_events(event)

            self.ui_manager.update(time_delta)
            self.screen.fill((20, 20, 20))
            self.map_view.draw(self.screen)

            # Display active module safely
            module_name = getattr(self.engine.active_module, 'name', 'No module loaded')
            text_surface = self.font.render(f"Active Module: {module_name}", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.width // 2, 30))
            self.screen.blit(text_surface, text_rect)

            self.ui_manager.draw_ui(self.screen)

            # Update info and lists
            self._update_info_box()
            self._update_char_list()
            self._update_init_list()

            # Enable/disable place token button
            if self.char_list.get_single_selection():
                self.place_token_button.enable()
            else:
                self.place_token_button.disable()

            pygame.display.flip()

        pygame.quit()

    # --- Helper Methods ---
    def _handle_button_press(self, event):
        if event.ui_element == self.create_hex_map_button:
            try:
                self.engine.get_command_handler().parse_and_handle("map create hexmap 15 10 type=hex")
                print("Created a new hex map.")
            except Exception as e:
                print(f"Failed to create hex map: {e}")
        elif event.ui_element == self.create_char_button:
            self._open_create_char_window()
        elif self.create_char_window and event.ui_element == self.create_char_submit_button:
            self._handle_create_char_submission()
        elif event.ui_element == self.add_to_init_button:
            self._handle_add_to_initiative()
        elif event.ui_element == self.roll_init_button:
            try:
                self.engine.get_command_handler().parse_and_handle("init")
            except Exception as e:
                print(f"Failed to roll initiative: {e}")
        elif event.ui_element == self.place_token_button:
            self._enter_placing_mode()

    def _update_info_box(self):
        selected = getattr(self.map_view, 'selected_object', None)
        if selected:
            info_html = f"<b>ID:</b> {selected.id}<br><b>Pos:</b> ({selected.x}, {selected.y})<br><b>Layer:</b> {selected.layer}"
            self.info_text_box.set_text(info_html)
        else:
            self.info_text_box.set_text("No object selected.")

    # All other helper methods (_enter_placing_mode, _handle_add_to_initiative,
    # _update_char_list, _update_init_list, _open_create_char_window,
    # _handle_create_char_submission) remain unchanged.
