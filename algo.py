from PIL import Image
from Crypto.Cipher import DES
import numpy as np
import os
import json


def pad(data):
    """Pad data to make its length a multiple of 8 (block size for DES)."""
    while len(data) % 8 != 0:
        data += b"\x00"
    return data


def encrypt_grayscale_into_rgb(
    grayscale_path, rgb_path, output_path, key, metadata_path
):
    """
    Encrypts a grayscale image and hides it inside an RGB image using DES with randomized embedding.

    :param grayscale_path: Path to the grayscale image
    :param rgb_path: Path to the RGB image
    :param output_path: Path to save the output image
    :param key: 8-byte key for DES encryption
    :param metadata_path: Path to save metadata (random indices)
    """
    if len(key) != 8:
        raise ValueError("Key must be 8 bytes long.")

    # Open the grayscale and RGB images
    grayscale_img = Image.open(grayscale_path).convert("L")
    rgb_img = Image.open(rgb_path).convert("RGB")

    # Ensure the images have the same dimensions
    if grayscale_img.size != rgb_img.size:
        raise ValueError("Grayscale and RGB images must have the same dimensions.")

    # Convert the grayscale image to bytes
    grayscale_bytes = np.array(grayscale_img).tobytes()

    # Pad the grayscale bytes
    padded_grayscale_bytes = pad(grayscale_bytes)

    # Encrypt the grayscale bytes using DES
    cipher = DES.new(key, DES.MODE_ECB)
    encrypted_bytes = cipher.encrypt(padded_grayscale_bytes)

    # Convert the RGB image to a NumPy array
    rgb_array = np.array(rgb_img)

    # Flatten the RGB array and get its total size
    flat_rgb = rgb_array.flatten()
    total_size = flat_rgb.size

    # Ensure there's enough room in the RGB image to store encrypted data
    if len(encrypted_bytes) > total_size:
        raise ValueError("RGB image is too small to store the encrypted data.")

    # Generate a random permutation of indices
    random_indices = np.random.permutation(total_size)[: len(encrypted_bytes)]

    # Embed the encrypted grayscale bytes into the RGB image
    for i, idx in enumerate(random_indices):
        flat_rgb[idx] = encrypted_bytes[i]

    # Save the random indices to metadata
    with open(metadata_path, "w") as f:
        json.dump(random_indices.tolist(), f)

    # Reshape the RGB array back to its original shape
    encrypted_rgb_array = flat_rgb.reshape(rgb_array.shape)

    # Save the resulting image
    encrypted_img = Image.fromarray(encrypted_rgb_array.astype("uint8"), "RGB")
    encrypted_img.save(output_path)


# Example usage
if __name__ == "__main__":
    grayscale_image_path = "grayscale_image.jpg"
    rgb_image_path = "rgb_image.jpg"
    output_image_path = "output_image.jpg"
    metadata_path = "encryption_metadata.json"

    # Generate a random 8-byte key for DES
    des_key = os.urandom(8)

    print(f"Using DES key: {des_key.hex()}")

    encrypt_grayscale_into_rgb(
        grayscale_image_path, rgb_image_path, output_image_path, des_key, metadata_path
    )
    print(f"Encrypted image saved to {output_image_path}")
    print(f"Metadata saved to {metadata_path}")
