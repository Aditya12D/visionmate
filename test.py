from camera.camera import Camera

cam = Camera()

frame = cam.capture()

cam.save_frame(frame, "images/live.jpg")

cam.release()

print("Image saved successfully.")