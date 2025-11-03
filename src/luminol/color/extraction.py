from typing import Dict, Tuple
from pathlib import Path
import time
import logging


def get_colors(
    image_path: str, num_colors: int = 8, preset: str = "balanced"
) -> Dict[Tuple[int, int, int], float]:
    SUPPORTED_PRESET = ["high", "balanced", "fast"]
    if preset not in SUPPORTED_PRESET:
        raise ValueError(
            f"{preset} is not a valid Preset. Select something from {', '.join(SUPPORTED_PRESET)}"
        )

    resize_dim: Tuple[int, int]
    pixel_sample_count: int
    kmeans_iteration: int

    if preset == "fast":
        resize_dim = (100, 100)
        pixel_sample_count = 1000
        kmeans_iteration = 5

    elif preset == "high":
        resize_dim = (300, 300)
        pixel_sample_count = 10000
        kmeans_iteration = 20
    else:  # balanced
        resize_dim = (150, 150)
        pixel_sample_count = 4000
        kmeans_iteration = 10

    extracted_colors: dict = extract_colors(
        image_path=image_path,
        num_colors=num_colors,
        resize_dim=resize_dim,
        pixel_sample_count=pixel_sample_count,
        kmeans_iteration=kmeans_iteration,
    )
    return extracted_colors


def extract_colors(
    image_path: str | Path,
    num_colors: int = 8,
    resize_dim: Tuple = (300, 300),
    pixel_sample_count: int = 4000,
    kmeans_iteration: int = 10,
    validate_unique_colors: bool = False,
) -> Dict[Tuple[int, int, int], float]:
    """
    Extract dominant colors using K-means clustering algorithm.

    Args:
        num_colors: Number of colors to extract.

    Returns:
        Dict[Tuple[int, int, int], float]: Dictionary mapping RGB color tuples to coverage percentages.
                                            Format: (255, 128, 0) -> 0.45
    """
    start = time.perf_counter()
    import numpy as np
    from PIL import Image

    end = time.perf_counter()
    logging.info(f"Numpy and Pillow took {end - start} to import")

    try:
        # Set seed at the very beginning for consistency
        np.random.seed(69)

        with Image.open(image_path) as img:
            # Convert to RGB
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize image based on quality setting
            img.thumbnail(resize_dim, Image.Resampling.LANCZOS)

            # Convert to numpy array
            img_array = np.array(img, dtype=np.float32)
            # Reshape to 2D array (pixels x RGB)
            pixels = img_array.reshape(-1, 3)

            # Validate num_colors
            if validate_unique_colors is True:
                unique_colors = len(np.unique(pixels, axis=0))
                num_colors = min(num_colors, unique_colors, len(pixels))
            else:
                num_colors = min(num_colors, len(pixels))

            # NOTE: might think about this in the future
            # Only validate if image is very small
            # if len(pixels) < num_colors * 10:  # Rule of thumb
            #     unique_colors = len(np.unique(pixels, axis=0))
            #     num_colors = min(num_colors, unique_colors)

            if num_colors < 1:
                raise ValueError("Image must contain at least one color")

            # Sample pixels for speed based on quality setting
            if len(pixels) > pixel_sample_count:
                indices = np.random.choice(
                    len(pixels), pixel_sample_count, replace=False
                )
                sampled_pixels = pixels[indices]
            else:
                sampled_pixels = pixels

            # K-means++ initialization for better starting centroids
            centroids = np.zeros((num_colors, 3), dtype=np.float32)
            centroids[0] = sampled_pixels[np.random.choice(len(sampled_pixels))]

            for i in range(1, num_colors):
                # Use squared distances (no sqrt needed)
                distances_sq = np.min(
                    ((sampled_pixels[:, np.newaxis, :] - centroids[:i]) ** 2).sum(
                        axis=2
                    ),
                    axis=1,
                )

                # Avoid division by zero
                total_distance = distances_sq.sum()
                if total_distance > 0:
                    probabilities = distances_sq / total_distance
                else:
                    probabilities = np.ones(len(sampled_pixels)) / len(sampled_pixels)

                centroids[i] = sampled_pixels[
                    np.random.choice(len(sampled_pixels), p=probabilities)
                ]

            # K-means iterations based on quality setting
            for _ in range(kmeans_iteration):
                # Use squared distances (faster, same result for argmin)
                distances_sq = (
                    (sampled_pixels[:, np.newaxis, :] - centroids) ** 2
                ).sum(axis=2)
                assignments = np.argmin(distances_sq, axis=1)

                # Update centroids
                new_centroids = np.zeros_like(centroids)
                cluster_has_points = np.zeros(num_colors, dtype=bool)

                for i in range(num_colors):
                    mask = assignments == i
                    if mask.any():
                        new_centroids[i] = sampled_pixels[mask].mean(axis=0)
                        cluster_has_points[i] = True
                    else:
                        # Reinitialize empty cluster to the farthest point
                        farthest_idx = np.argmax(distances_sq.min(axis=1))
                        new_centroids[i] = sampled_pixels[farthest_idx]
                        cluster_has_points[i] = True

                # Check convergence
                if np.allclose(centroids, new_centroids, atol=1e-4):
                    centroids = new_centroids
                    break

                centroids = new_centroids

            # Final assignment to get accurate coverage
            distances_sq = ((sampled_pixels[:, np.newaxis, :] - centroids) ** 2).sum(
                axis=2
            )
            assignments = np.argmin(distances_sq, axis=1)

            # Calculate coverage for each color
            counts = np.bincount(assignments, minlength=num_colors)
            coverages = counts / len(sampled_pixels)

            # Sort colors by dominance
            sorted_indices = np.argsort(counts)[::-1]

            # Build result dictionary with RGB colors and coverage
            result = {}
            for idx in sorted_indices:
                if counts[idx] > 0:  # Only include colors that appear
                    color_rgb = tuple(int(c) for c in np.clip(centroids[idx], 0, 255))
                    coverage = float(coverages[idx])  # Ensure it's a Python float
                    result[color_rgb] = coverage

            return result

    except Exception as e:
        raise RuntimeError(f"Error extracting colors: {str(e)}")
