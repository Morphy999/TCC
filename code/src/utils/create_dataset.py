import argparse
import os

import cv2
from tqdm import tqdm


def create_dataset(dataset_path, n_frames, limit_image, output_path=None):
    """
    Process images from dataset_path, taking one image every n_frames
    up to a maximum of limit_image images.

    Args:
        dataset_path (str): Path to the dataset
        n_frames (int): Number of frames to skip
        limit_image (int): Maximum number of images to process
        output_path (str, optional): Path where to save processed images. If None, will create a "processed_dataset" folder next to the dataset.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset path not found: {dataset_path}")

    if output_path is None:
        output_dir = os.path.join(os.path.dirname(dataset_path), "processed_dataset")
    else:
        output_dir = output_path

    os.makedirs(output_dir, exist_ok=True)

    valid_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
    image_files = []

    for file in os.listdir(dataset_path):
        file_path = os.path.join(dataset_path, file)
        if os.path.isfile(file_path) and any(
            file.lower().endswith(ext) for ext in valid_extensions
        ):
            image_files.append(file_path)

    image_files.sort()

    selected_images = image_files[::n_frames]

    # Limit the number of images if needed
    if limit_image > 0:
        selected_images = selected_images[:limit_image]

    print(f"Processing {len(selected_images)} images...")
    for i, img_path in enumerate(tqdm(selected_images)):
        # Read the image
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Could not read image {img_path}")
            continue

        filename = f"image_{i:04d}{os.path.splitext(img_path)[1]}"
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, img)

    print(f"Processing complete. {len(selected_images)} images saved to {output_dir}")
    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Create a processed dataset by selecting images at intervals"
    )
    parser.add_argument("dataset_path", type=str, help="Path to the dataset directory")
    parser.add_argument("n_frames", type=int, help="Number of frames to skip")
    parser.add_argument(
        "limit_image", type=int, help="Maximum number of images to process (0 for no limit)"
    )
    parser.add_argument(
        "--output_path",
        "-o",
        type=str,
        help='Path where to save processed images. Default is "processed_dataset" folder next to dataset.',
    )

    args = parser.parse_args()

    try:
        output_dir = create_dataset(
            args.dataset_path, args.n_frames, args.limit_image, args.output_path
        )
        print(f"Processed dataset saved to: {output_dir}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
