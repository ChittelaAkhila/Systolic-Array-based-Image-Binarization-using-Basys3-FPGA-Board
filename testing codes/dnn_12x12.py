import numpy as np
import serial
import time
from PIL import Image, ImageOps

# ----- PARAMETERS -----
SERIAL_PORT = 'COM6'  // Change port accordingly
BAUDRATE = 921600      
IMAGE_SIZE = (12, 12)
OUTPUT_COMPARISON_IMAGE_PATH = "your_path/final_smiley_12x12.png"

# ----- FUNCTIONS -----

def load_and_preprocess_image(image_path):
    img = Image.open(image_path).convert('L')  # Convert RGB to grayscale
    img = img.resize(IMAGE_SIZE)
    img_array = np.array(img, dtype=np.uint8)
    return img, img_array

def relu(x):
    return np.maximum(0, x)

def software_dnn(image_array, weight_matrix):
    output = np.multiply(image_array.astype(np.int32), weight_matrix.astype(np.int32))
    output = relu(output)
    return output

def send_receive_uart(image_array, weight_matrix):
    img_bytes = image_array.flatten().astype(np.uint8).tobytes()
    weight_bytes = weight_matrix.flatten().astype(np.uint8).tobytes()

    send_data = img_bytes + weight_bytes
    assert len(send_data) == 288, f"Expected 288 bytes but got {len(send_data)}"

    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=2)
    time.sleep(1)  # Allow FPGA reset if needed

    # Send data
    ser.write(send_data)

    # Receive 144 outputs (each 4 bytes = 32 bits)
    recv_data = ser.read(144 * 4)
    if len(recv_data) != 576:
        raise Exception(f"Incomplete data received: {len(recv_data)} bytes")

    output_values = np.frombuffer(recv_data, dtype=np.int32)
    output_matrix = output_values.reshape(12, 12)

    ser.close()
    return output_matrix

def create_comparison_image(img_array, software_output, fpga_output, save_path):
    def normalize_to_uint8(matrix):
        matrix = matrix.astype(np.float32)
        matrix = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix) + 1e-5)  # Avoid div by zero
        return (matrix * 255).astype(np.uint8)

    software_img = Image.fromarray(normalize_to_uint8(software_output), mode='L').resize((128, 128), resample=Image.NEAREST)
    fpga_img = Image.fromarray(normalize_to_uint8(fpga_output), mode='L').resize((128, 128), resample=Image.NEAREST)
    resized_input_img = Image.fromarray(img_array, mode='L').resize((128, 128), resample=Image.NEAREST)

    # Combine images side by side
    total_width = 128 * 3
    max_height = 128

    new_img = Image.new('RGB', (total_width, max_height))
    new_img.paste(ImageOps.colorize(resized_input_img, black="black", white="white"), (0, 0))
    new_img.paste(ImageOps.colorize(software_img, black="black", white="blue"), (128, 0))
    new_img.paste(ImageOps.colorize(fpga_img, black="black", white="red"), (256, 0))

    # Save comparison image
    new_img.save(save_path)
    print(f"Comparison image saved at {save_path}")

# ----- MAIN FLOW -----

if __name__ == "__main__":
    image_path = "your_path/smiley.jpeg"  

    # Load and preprocess image
    img, img_array = load_and_preprocess_image(image_path)

    # Call trained weights
    weight_matrix = np.load("your_path/trained_weights_12x12.npy").astype(np.uint8)


    # Software DNN output
    software_output = software_dnn(img_array, weight_matrix)

    # Communicate with FPGA
    try:
        fpga_output = send_receive_uart(img_array, weight_matrix)
    except Exception as e:
        print(f"UART Communication failed: {e}")
        fpga_output = np.zeros((12, 12), dtype=np.int32)  # fallback

    # Show results
    print("\n--- Resized 12x12 Image (Grayscale) ---\n", img_array)
    print("\n--- Software DNN Output (After ReLU) ---\n", software_output)
    print("\n--- FPGA Output (After ReLU) ---\n", fpga_output)

    # Create comparison image
    create_comparison_image(img_array, software_output, fpga_output, OUTPUT_COMPARISON_IMAGE_PATH)
