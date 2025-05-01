import numpy as np
import os

# Simulate training data: 100 grayscale images of size 12x12
# Replace this with real training images if available
num_samples = 100
simulated_images = np.random.randint(0, 256, size=(num_samples, 12, 12)).astype(np.uint8)

# "Trained" weight matrix: average over all training images
trained_weights = np.mean(simulated_images, axis=0).astype(np.uint8)

# Save to .npy file
save_path = "your_path/trained_weights_12x12.npy"
np.save(save_path, trained_weights)

print(f"Trained weight matrix saved at:\n{save_path}")
print("Shape:", trained_weights.shape)
print("Sample values:\n", trained_weights)
