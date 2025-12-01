"""
AIR DRUM KIT - Interactive Computer Vision Drum Set
Created by Arian Khademolghorani

This application turns any blue object (like a drumstick or your finger with a blue marker)
into a virtual drumstick that can trigger drum sounds by moving through defined zones on screen.

Requirements:
- OpenCV (cv2)
- NumPy
- Pygame
- A webcam
- Blue-colored tracking object (recommended: blue drumstick or blue marker)
"""

import cv2
import numpy as np
import pygame

# ==============================================================================
# CONFIGURATION & GLOBAL SETTINGS
# ==============================================================================

# Display resolution - set to comfortable window size
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# Application state management
STATE_MENU = 0  # Main menu screen
STATE_PLAY = 1  # Active drumming mode
current_app_state = STATE_MENU

# ==============================================================================
# AUDIO SYSTEM INITIALIZATION
# ==============================================================================

# Initialize the Pygame mixer for audio playback
pygame.mixer.init()

# Load drum sound samples from the assets folder
drum_sounds = {
    "Kick": pygame.mixer.Sound("assets/Samples/kick-808.wav"),
    "Snare": pygame.mixer.Sound("assets/Samples/snare-808.wav"),
    "Hi-Hat": pygame.mixer.Sound("assets/Samples/hihat-808.wav"),
    "Tom1": pygame.mixer.Sound("assets/Samples/tom-lofi.wav"),
    "Tom2": pygame.mixer.Sound("assets/Samples/tom-rototom.wav"),
    "Crash": pygame.mixer.Sound("assets/Samples/crash-808.wav"),
}

# ==============================================================================
# WEBCAM SETUP
# ==============================================================================

# Initialize webcam and configure resolution
webcam = cv2.VideoCapture(0)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)

# ==============================================================================
# COLOR TRACKING CONFIGURATION
# ==============================================================================

# HSV color range for blue object detection
# These values create a strict blue range to minimize false positives
BLUE_LOWER_BOUND = np.array([100, 150, 100])
BLUE_UPPER_BOUND = np.array([120, 255, 255])

# ==============================================================================
# DRUM ZONE DEFINITIONS
# ==============================================================================

# Dictionary to store all drum pad zones and their properties
drum_zones = {}

# Zone dimensions
ZONE_HEIGHT = 100  # Height of each drum pad
bottom_row_drums = ["Kick", "Snare", "Hi-Hat", "Tom1", "Tom2"]
number_of_drums = len(bottom_row_drums)
zone_width = WINDOW_WIDTH // number_of_drums

# Create the five drum pads along the bottom of the screen
for index, drum_name in enumerate(bottom_row_drums):
    x_position = index * zone_width
    y_position = WINDOW_HEIGHT - ZONE_HEIGHT
    
    drum_zones[drum_name] = {
        'box': (x_position, y_position, x_position + zone_width, WINDOW_HEIGHT),
        'strike_y': None,  # Reserved for future downward motion detection
        'is_crash': False
    }

# Create the crash cymbal in the top-left corner
crash_cymbal_width = WINDOW_WIDTH // 4
drum_zones["Crash"] = {
    'box': (0, 0, crash_cymbal_width, ZONE_HEIGHT),
    'strike_y': None,
    'is_crash': True
}

# ==============================================================================
# IMAGE LOADING SYSTEM
# ==============================================================================

# Dictionary to store loaded drum images
drum_images = {}

def load_drum_image(file_path, target_width, target_height):
    """
    Loads a drum image from disk, resizes it, and ensures proper color format.
    
    Args:
        file_path: Path to the image file
        target_width: Desired width after resizing
        target_height: Desired height after resizing
    
    Returns:
        A 3-channel BGR image ready for OpenCV display
    """
    try:
        # Load image with potential alpha channel
        loaded_image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        
        if loaded_image is not None:
            # Resize to target dimensions
            loaded_image = cv2.resize(loaded_image, (target_width, target_height))
            
            # Handle different channel configurations
            if loaded_image.shape[2] == 4:
                # Convert BGRA to BGR (removes transparency)
                loaded_image = cv2.cvtColor(loaded_image, cv2.COLOR_BGRA2BGR)
            
            if loaded_image.shape[2] == 3:
                return loaded_image
            
    except Exception as error:
        print(f"Error loading image at {file_path}: {error}")
    
    # Create a fallback placeholder image if loading fails
    placeholder = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    cv2.putText(placeholder, "NO IMAGE", (target_width//2 - 50, target_height//2 + 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return placeholder

# Define file paths for drum images
drum_image_paths = {
    "Kick": "assets/images/kick_drum.png",
    "Snare": "assets/images/snare_drum.png",
    "Hi-Hat": "assets/images/hi_hat.png",
    "Tom1": "assets/images/tom.png",
    "Tom2": "assets/images/tom.png",
    "Crash": "assets/images/crash_cymbal.png",
}

# Pre-load all drum images
for drum_name, zone_properties in drum_zones.items():
    x1, y1, x2, y2 = zone_properties['box']
    width = x2 - x1
    height = y2 - y1
    drum_images[drum_name] = load_drum_image(drum_image_paths[drum_name], width, height)

def overlay_drum_image_on_frame(main_frame, drum_image, x_start, y_start, is_being_hit):
    """
    Places a drum image onto the main video frame with visual hit feedback.
    
    Args:
        main_frame: The main video frame
        drum_image: The drum image to overlay
        x_start, y_start: Top-left position for the overlay
        is_being_hit: Whether the drum is currently being struck
    """
    img_height, img_width, _ = drum_image.shape
    
    # Get the region of interest in the main frame
    region_of_interest = main_frame[y_start:y_start+img_height, x_start:x_start+img_width]
    
    if is_being_hit:
        # Create a red tint overlay for visual feedback
        red_overlay = np.zeros_like(drum_image, dtype=np.uint8)
        red_overlay[:, :] = (0, 0, 255)  # Pure red in BGR
        
        # Blend the drum image with red tint (70% original, 30% red)
        blended_image = cv2.addWeighted(drum_image, 0.7, red_overlay, 0.3, 0)
        region_of_interest[:] = blended_image
    else:
        # No hit - display original drum image
        region_of_interest[:] = drum_image

# ==============================================================================
# MENU SYSTEM
# ==============================================================================

# Define menu buttons: (x1, y1, x2, y2, label, action)
menu_buttons = {
    "PLAY": (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 100, 
             WINDOW_WIDTH//2 + 150, WINDOW_HEIGHT//2 - 30, 
             "PLAY DRUMS (P)", STATE_PLAY),
    "CREDITS": (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 10, 
                WINDOW_WIDTH//2 + 150, WINDOW_HEIGHT//2 + 80, 
                "CREDITS (C)", -1),
    "EXIT": (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 120, 
             WINDOW_WIDTH//2 + 150, WINDOW_HEIGHT//2 + 190, 
             "EXIT (Q)", -2)
}

# Flag to toggle credits screen
showing_credits = False

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def is_point_inside_zone(point_x, point_y, zone_boundaries):
    """
    Checks if a point is inside a rectangular zone.
    
    Args:
        point_x, point_y: Coordinates of the point
        zone_boundaries: Tuple of (x1, y1, x2, y2) defining the zone
    
    Returns:
        True if point is inside the zone, False otherwise
    """
    x1, y1, x2, y2 = zone_boundaries
    return x1 <= point_x <= x2 and y1 <= point_y <= y2

# Sound debouncing system - prevents multiple rapid triggers
sound_is_locked = {drum_name: False for drum_name in drum_zones}

# ==============================================================================
# RENDERING FUNCTIONS
# ==============================================================================

def render_main_menu(frame):
    """Draws the main menu interface."""
    # Dark background
    cv2.rectangle(frame, (0, 0), (WINDOW_WIDTH, WINDOW_HEIGHT), (20, 20, 20), -1)
    
    # Title
    cv2.putText(frame, "AIR DRUM KIT", 
                (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

    # Draw each menu button
    for button_key, (x1, y1, x2, y2, label, _) in menu_buttons.items():
        # Button color (green for PLAY, orange for others)
        button_color = (0, 255, 0) if button_key == "PLAY" else (255, 100, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), button_color, -1)
        
        # White border
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 3)
        
        # Centered text
        text_width = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]
        text_x = x1 + (x2 - x1)//2 - text_width//2
        cv2.putText(frame, label, (text_x, y2 - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (20, 20, 20), 2)

def render_credits_screen(frame):
    """Draws the credits screen with project information."""
    cv2.rectangle(frame, (0, 0), (WINDOW_WIDTH, WINDOW_HEIGHT), (20, 20, 20), -1)
    
    # Credits title
    cv2.putText(frame, "CREDITS", (WINDOW_WIDTH//2 - 100, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
    
    # Credits information
    credits_text = [
        "AIR DRUM KIT",
        "",
        "Developed by Arian Khademolghorani",
        "Computer Vision: OpenCV",
        "Sound Engine: Pygame Mixer",
        "Sound Samples: 99Sounds",
        "Tracking Method: HSV Color Filtering",
        "",
        "Press 'B' to go back to the menu."
    ]
    
    y_position = 120
    for line in credits_text:
        cv2.putText(frame, line, (WINDOW_WIDTH//4, y_position), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_position += 40

def render_drum_kit_interface(frame):
    """Draws the interactive drum kit with all drum pads."""
    # Render each drum pad
    for drum_name, zone_properties in drum_zones.items():
        x1, y1, x2, y2 = zone_properties['box']
        
        # Overlay the drum image with hit feedback
        current_drum_image = drum_images[drum_name]
        is_currently_hit = sound_is_locked[drum_name]
        overlay_drum_image_on_frame(frame, current_drum_image, x1, y1, is_currently_hit)

        # Draw drum name label
        text_width = cv2.getTextSize(drum_name, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]
        center_x = x1 + (x2-x1)//2
        center_y = y1 + (y2-y1)//2
        
        # Text color changes based on hit state for better visibility

        text_color = (0, 0, 0) if is_currently_hit else (0, 0, 255)
        text_position =  center_y - 30 if (drum_name != "Crash") else ( center_y + 30)
        cv2.putText(frame, drum_name, (center_x - text_width//2, text_position), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)

    # Instructions
    cv2.putText(frame, "Press 'B' for Menu", (10, 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

# ==============================================================================
# MAIN APPLICATION LOOP
# ==============================================================================

while True:
    # Capture frame from webcam
    frame_captured, video_frame = webcam.read()
    if not frame_captured:
        break

    # Mirror the frame horizontally for natural interaction
    video_frame = cv2.flip(video_frame, 1)
    
    # -------------------------------------------------------------------------
    # MENU STATE - Display main menu or credits
    # -------------------------------------------------------------------------
    if current_app_state == STATE_MENU:
        if showing_credits:
            render_credits_screen(video_frame)
        else:
            render_main_menu(video_frame)
        
        # Handle keyboard input in menu
        key_pressed = cv2.waitKey(1) & 0xFF
        
        if key_pressed == ord('p'):
            current_app_state = STATE_PLAY
            showing_credits = False
        elif key_pressed == ord('c'):
            showing_credits = True
        elif key_pressed == ord('b'):
            showing_credits = False
        elif key_pressed == ord('q'):
            break

    # -------------------------------------------------------------------------
    # PLAY STATE - Active drum kit with object tracking
    # -------------------------------------------------------------------------
    elif current_app_state == STATE_PLAY:
        # Convert frame to HSV color space for better color detection
        hsv_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for blue color detection
        blue_mask = cv2.inRange(hsv_frame, BLUE_LOWER_BOUND, BLUE_UPPER_BOUND)
        blue_mask = cv2.medianBlur(blue_mask, 5)  # Reduce noise

        # Find contours of blue objects
        detected_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, 
                                                cv2.CHAIN_APPROX_SIMPLE)
        
        # Track which drums are currently being hit
        drums_being_hit = {drum_name: False for drum_name in drum_zones}

        # Process each detected blue object
        for contour in detected_contours:
            contour_area = cv2.contourArea(contour)
            
            # Filter out small noise (minimum area threshold)
            if contour_area > 500:
                x, y, w, h = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2

                # Draw tracking visualization
                cv2.circle(video_frame, (center_x, center_y), 5, (255, 0, 0), -1)

                # Check if object is inside any drum zone
                for drum_name, zone_properties in drum_zones.items():
                    zone_boundaries = zone_properties['box']
                    
                    if is_point_inside_zone(center_x, center_y, zone_boundaries):
                        drums_being_hit[drum_name] = True
                        
                        # Play sound only if not already playing (debounce)
                        if not sound_is_locked[drum_name]:
                            drum_sounds[drum_name].play()
                            sound_is_locked[drum_name] = True

        # Reset sound locks when object leaves the zone
        for drum_name in drum_zones:
            if not drums_being_hit[drum_name]:
                sound_is_locked[drum_name] = False

        # Render the drum kit interface
        render_drum_kit_interface(video_frame)
        
        # Handle keyboard input during play
        key_pressed = cv2.waitKey(1) & 0xFF
        if key_pressed == ord('b'):
            current_app_state = STATE_MENU
            showing_credits = False
        elif key_pressed == ord('q'):
            break

    # Display the final frame
    cv2.imshow("Air Drum Kit", video_frame)
    cv2.resizeWindow("Air Drum Kit", WINDOW_WIDTH, WINDOW_HEIGHT)

# ==============================================================================
# CLEANUP
# ==============================================================================

webcam.release()
cv2.destroyAllWindows()