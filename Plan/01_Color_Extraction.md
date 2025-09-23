# Color Extraction Algorithm

This document outlines the full data pipeline and algorithms used for extracting a perceptually accurate color palette from an image.

## Color Processing Data Flow
Luminol follows a structured pipeline to ensure high-quality, perceptually accurate color extraction.

1.  **RGB Image Loading**: Load the source image and access its raw pixel data in 8-bit RGB format (0-255).
2.  **Preprocessing**: Resize the image for performance, apply a light blur to reduce noise, and sample a representative subset of pixels.
3.  **RGB → LAB Conversion**: Convert all sampled RGB pixels into the perceptually uniform LAB color space. This is a critical step for ensuring the accuracy of the clustering algorithm.
4.  **K-Means Clustering**: Perform K-Means clustering on the LAB pixel data to identify the dominant color centroids.
5.  **Color Object Creation**: For each dominant LAB color, create a rich `Color` object that contains the original LAB value and automatically computes and caches its RGB and HSL representations for later use.
6.  **Quality Scoring**: Score and rank the extracted colors based on properties like pixel coverage and perceptual uniqueness (using distance in LAB space).
7.  **Semantic Assignment**: Use the intuitive HSL color space (from the `Color` object) to classify the ranked colors into semantic roles like `bg-primary`, `accent-primary`, etc.
8.  **Transformations**: If configured, apply color transformations (e.g., brightness, saturation) using the HSL representation for predictable, visually appealing results.
9.  **Export**: Convert the final colors to the application-specific formats (e.g., hex, rgba) using their RGB representation.

## Multi-Method Color Extraction

### 1. Enhanced K-Means Clustering
This is the primary method for identifying dominant colors, performed in the perceptually uniform LAB color space for higher accuracy.

```
Algorithm: Perceptual K-Means in LAB Space
1. Preprocessing:
   - Resize image to a max width of 800px, maintaining aspect ratio.
   - Apply a light gaussian blur to reduce image noise.
   - Convert the image's pixels from RGB to the LAB color space.

2. Sampling Strategy:
   - Sample a representative subset of pixels for performance.
   - Skip transparent pixels (alpha < 128).
   - Weight center pixels higher to avoid edge artifacts.

3. Clustering Process:
   - Perform k-means++ clustering directly on the LAB pixel data.
   - Iterate until cluster centroids converge (max 20 iterations).
   - Merge visually similar clusters (ΔE < 12).
   - Result: 5-8 dominant colors, represented in LAB space.

Color Distance (LAB space):
ΔE = √[(L₁-L₂)² + (a₁-a₂)² + (b₁-b₂)²]
```

### 2. Histogram-Based Analysis
This method acts as a secondary check to ensure no significant colors were missed.

```
Algorithm: Frequency Analysis
1. Generate color histogram with 64 bins per channel
2. Find peaks in histogram representing dominant colors
3. Group nearby peaks to avoid oversegmentation
4. Weight by spatial distribution (center vs edges)
5. Combine with k-means results for validation

Spatial Weight Calculation:
weight(x,y) = 1.0 - distance_from_center / max_distance * 0.3
```

## Color Quality Assessment
After extraction, each potential color is scored to select the best 10-15 colors for the final palette. The scoring system leverages the properties of the LAB color space to rank colors.

```
Quality Scoring System:
1. **Coverage Score**: `log(pixel_count) / log(total_pixels)`
   (Measures how much of the image the color represents).
2. **Uniqueness Score**: `min_deltaE_to_other_colors / 50`
   (Ensures colors are visually distinct from each other).
3. **Chroma Score**: `sqrt(a² + b²) / 140`
   (Chroma is the LAB equivalent of saturation/vibrancy).
4. **Lightness Balance**: `1 - |L - 50| / 50`
   (Favors colors that are not extreme black or white).

Final Color Score = weighted_sum(all_scores)
```
