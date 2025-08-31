import pygame
import pygame_gui
from .map_view import MapView

class App:
    """The main GUI application."""

    def __init__(self, engine):
        pygame.init()
        self.engine = engine
        self.is_running = False
        self.screen = None
        self.clock = None
        self.width = 1280
        self.height = 720
        self.map_view = MapView(self)
        self.ui_manager = None
        self.create_char_window = None
        self.char_name_input = None
        self.char_hp_input = None

        # Create a default map for testing
        self.engine.get_command_handler().parse_and_handle("map create testmap 20 15")

    def run(self):
        """Starts the main application loop."""
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Modular VTT")
        self.clock = pygame.time.Clock()
        self.is_running = True

        self.ui_manager = pygame_gui.UIManager((self.width, self.height))

        self.create_hex_map_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.width - 170, 10), (160, 40)),
                                                                   text='Create Hex Map',
                                                                   manager=self.ui_manager)

        info_panel_rect = pygame.Rect(10, self.height - 160, 300, 150)
        info_panel = pygame_gui.elements.UIPanel(relative_rect=info_panel_rect,
                                                  starting_height=1,
                                                  manager=self.ui_manager)

        self.info_text_box = pygame_gui.elements.UITextBox(html_text="No object selected.",
                                                           relative_rect=pygame.Rect(0, 0, 280, 110),
                                                           manager=self.ui_manager,
                                                           container=info_panel)

        char_panel_rect = pygame.Rect(self.width - 210, 60, 200, 300)
        char_panel = pygame_gui.elements.UIPanel(relative_rect=char_panel_rect,
                                                  starting_height=1,
                                                  manager=self.ui_manager)

        self.char_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect(0, 0, 180, 200),
                                                             item_list=[],
                                                             manager=self.ui_manager,
                                                             container=char_panel)

        self.create_char_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(10, 220, 160, 30),
                                                               text='Create Character',
                                                               manager=self.ui_manager,
                                                               container=char_panel)

        init_panel_rect = pygame.Rect(self.width - 210, 370, 200, 300)
        init_panel = pygame_gui.elements.UIPanel(relative_rect=init_panel_rect,
                                                 starting_height=1,
                                                 manager=self.ui_manager)

        self.init_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect(0, 0, 180, 200),
                                                            item_list=[],
                                                            manager=self.ui_manager,
                                                            container=init_panel)

        self.add_to_init_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(10, 220, 160, 30),
                                                              text='Add to Initiative',
                                                              manager=self.ui_manager,
                                                              container=init_panel)

        self.roll_init_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(10, 260, 160, 30),
                                                            text='Roll Initiative',
                                                            manager=self.ui_manager,
                                                            container=init_panel)


        font = pygame.font.Font(None, 36)  # Default font, size 36

        while self.is_running:
            time_delta = self.clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.create_hex_map_button:
                        self.engine.get_command_handler().parse_and_handle("map create hexmap 15 10 type=hex")
                        print("Created a new hex map.")
                    elif event.ui_element == self.create_char_button:
                        self._open_create_char_window()
                    elif self.create_char_window and event.ui_element == self.create_char_submit_button:
                        self._handle_create_char_submission()
                    elif event.ui_element == self.add_to_init_button:
                        self._handle_add_to_initiative()
                    elif event.ui_element == self.roll_init_button:
                        self.engine.get_command_handler().parse_and_handle("init")

                if event.type == pygame_gui.UI_WINDOW_CLOSE:
                    if event.ui_element == self.create_char_window:
                        self.create_char_window = None

                self.map_view.handle_event(event)
                self.ui_manager.process_events(event)

            self.ui_manager.update(time_delta)

            self.screen.fill((20, 20, 20))  # Dark grey background

            # Draw the map view
            self.map_view.draw(self.screen)

            # Get active module name from the engine
            if self.engine.active_module:
                module_name = self.engine.active_module.name
            else:
                module_name = "No module loaded"

            # Render the text
            text_surface = font.render(f"Active Module: {module_name}", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.width // 2, 30))
            self.screen.blit(text_surface, text_rect)

            self.ui_manager.draw_ui(self.screen)

            # Update info box
            selected = self.map_view.selected_object
            if selected:
                info_html = f"<b>ID:</b> {selected.id}<br>"
                info_html += f"<b>Pos:</b> ({selected.x}, {selected.y})<br>"
                info_html += f"<b>Layer:</b> {selected.layer}"
                self.info_text_box.set_text(info_html)
            else:
                self.info_text_box.set_text("No object selected.")

            self._update_char_list()
            self._update_init_list()

            pygame.display.flip()

        pygame.quit()

    def _handle_add_to_initiative(self):
        selection = self.char_list.get_single_selection()
        if selection:
            # selection is a tuple: (display_text, entity_id)
            entity_id = selection[1]
            em = self.engine.get_entity_manager()
            entity = em.get_entity(entity_id)
            if entity:
                char_name = entity.attributes.get('name', '')
                self.engine.get_command_handler().parse_and_handle(f"add {char_name}")
                print(f"Added {char_name} to initiative.")

    def _update_init_list(self):
        """Updates the initiative list from the engine."""
        tracker = self.engine.get_initiative_tracker()
        em = self.engine.get_entity_manager()

        turn_order = tracker.get_turn_order()
        init_items = []
        for entity_id in turn_order:
            entity = em.get_entity(entity_id)
            if entity:
                name = entity.attributes.get('name', 'Unnamed')
                score = tracker.combatants.get(entity_id)
                init_items.append(f"{score}: {name}")

        # Add combatants not in turn order
        for entity_id in tracker.combatants:
            if entity_id not in turn_order:
                entity = em.get_entity(entity_id)
                if entity:
                    name = entity.attributes.get('name', 'Unnamed')
                    init_items.append(f"??: {name}")

        self.init_list.set_item_list(init_items)

    def _update_char_list(self):
        """Updates the character list from the engine."""
        em = self.engine.get_entity_manager()
        char_items = []
        for entity in em.list_entities(entity_type="character"):
            name = entity.attributes.get('name', 'Unnamed')
            hp = entity.attributes.get('hp', 'N/A')
            display_text = f"{name} (HP: {hp})"
            char_items.append((display_text, entity.id))

        self.char_list.set_item_list(char_items)

    def _open_create_char_window(self):
        if self.create_char_window:
            return

        self.create_char_window = pygame_gui.elements.UIWindow(rect=pygame.Rect((self.width // 2 - 150, self.height // 2 - 100), (300, 200)),
                                                                manager=self.ui_manager,
                                                                window_display_title='Create Character')

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 10, 80, 25), text='Name:', manager=self.ui_manager, container=self.create_char_window)
        self.char_name_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(100, 10, 150, 25), manager=self.ui_manager, container=self.create_char_window)

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 50, 80, 25), text='HP:', manager=self.ui_manager, container=self.create_char_window)
        self.char_hp_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(100, 50, 150, 25), manager=self.ui_manager, container=self.create_char_window)

        self.create_char_submit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(100, 100, 100, 40), text='Create', manager=self.ui_manager, container=self.create_char_window)

    def _handle_create_char_submission(self):
        name = self.char_name_input.get_text()
        hp = self.char_hp_input.get_text()

        if name:
            command = f"create char {name}"
            if hp:
                command += f" hp={hp}"

            self.engine.get_command_handler().parse_and_handle(command)
            print(f"Created character: {name}")
            self.create_char_window.kill()
            self.create_char_window = None
