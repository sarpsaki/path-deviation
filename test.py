import cv2
import numpy as np

def generate_test_video():
    # Video specifications
    width, height = 640, 480
    fps = 30
    duration_sec = 10
    total_frames = fps * duration_sec
    half_frames = total_frames // 2  # 5 seconds mark

    # Initialize OpenCV VideoWriter
    # 'mp4v' is a good cross-platform codec for .mp4 files
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('test_path_deviation.mp4', fourcc, fps, (width, height))

    print(f"Generating video ({total_frames} frames)...")

    for frame_idx in range(total_frames):
        # 1. Create a white background (255 for all color channels)
        frame = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # 2. Draw the thin red horizontal reference line at y=240
        # OpenCV uses BGR (Blue, Green, Red) format, so Red is (0, 0, 255)
        cv2.line(frame, (0, 240), (width, 240), (0, 0, 255), 1)
        
        # 3. Calculate X coordinate (0 to 640 smoothly across all 10 seconds)
        x_center = int((frame_idx / total_frames) * width)
        
        # 4. Calculate Y coordinate based on time
        if frame_idx <= half_frames:
            # First 5 seconds: moves horizontally along y=240
            y_center = 240
        else:
            # Last 5 seconds: drifts upward from 240 to 120
            # Calculate how far along we are in the last 5 seconds (0.0 to 1.0)
            drift_progress = (frame_idx - half_frames) / half_frames
            # Y decreases as it moves "up" the screen
            y_center = int(240 - (drift_progress * 120))
            
        # 5. Calculate rectangle coordinates (60x60 pixels)
        rect_w, rect_h = 60, 60
        top_left = (x_center - rect_w // 2, y_center - rect_h // 2)
        bottom_right = (x_center + rect_w // 2, y_center + rect_h // 2)
        
        # 6. Draw the filled blue rectangle
        # Blue in BGR is (255, 0, 0). Thickness = -1 means filled.
        cv2.rectangle(frame, top_left, bottom_right, (255, 0, 0), -1)
        
        # Write the finalized frame to the video file
        out.write(frame)

    # Clean up
    out.release()
    print("Done! Video saved to 'test_path_deviation.mp4' in the current working directory.")

if __name__ == "__main__":
    generate_test_video()