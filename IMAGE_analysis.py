import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image
from scipy.fft import fft2, fftshift
from skimage import segmentation, color
from skimage.filters import gabor
from collections import Counter
import warnings
import json
from datetime import datetime
warnings.filterwarnings('ignore')

# Chinese font config removed because output all English text

def imread_cv(path):
    pil_image = Image.open(path).convert('RGB')
    img_np = np.array(pil_image)
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    return img_cv

class ArtworkAnalyzer:
    def __init__(self, image_path, output_root='output'):
        try:
            self.original_image = imread_cv(image_path)
        except Exception as e:
            raise ValueError(f"Failed to read image: {image_path}, Error: {e}")

        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.image = self.original_image.copy()
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        self.image_path = image_path
        self.output_root = output_root
        
        # Initialize analysis results dictionary
        self.analysis_results = {
            "metadata": {
                "image_path": image_path,
                "image_shape": self.image.shape,
                "analysis_timestamp": datetime.now().isoformat()
            },
            "color_analysis": {},
            "texture_analysis": {},
            "structure_analysis": {},
            "light_shadow_analysis": {},
            "frequency_analysis": {}
        }

        print(f"Image loaded successfully: {self.image.shape}")

    def save_figure(self, fig, name, artwork_name):
        # Create subfolder for this artwork
        folder = os.path.join(self.output_root, artwork_name)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, name + '.png')
        fig.savefig(filepath)
        plt.close(fig)
        print(f"Saved figure: {filepath}")

    def preprocess_image(self, denoise=True, enhance_contrast=True):
        if denoise:
            self.image = cv2.bilateralFilter(self.image, 9, 75, 75)
        
        if enhance_contrast:
            lab = cv2.cvtColor(self.image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            self.image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

    def analyze_color_distribution(self, artwork_name):
        fig, axes = plt.subplots(2, 3, figsize=(18,12))
        fig.suptitle('Color Analysis - Revealing Artist\'s Palette', fontsize=16, fontweight='bold')

        axes[0,0].imshow(self.original_image)
        axes[0,0].set_title('Original Artwork')
        axes[0,0].axis('off')

        hsv = cv2.cvtColor(self.image, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1]
        im1 = axes[0,1].imshow(saturation, cmap='jet')
        axes[0,1].set_title('Saturation Heatmap (High = Vivid Colors)')
        axes[0,1].axis('off')
        fig.colorbar(im1, ax=axes[0,1], fraction=0.046)

        # Record saturation statistics
        self.analysis_results["color_analysis"]["saturation"] = {
            "mean": float(np.mean(saturation)),
            "std": float(np.std(saturation)),
            "median": float(np.median(saturation)),
            "min": float(np.min(saturation)),
            "max": float(np.max(saturation))
        }

        value = hsv[:, :, 2]
        im2 = axes[0,2].imshow(value, cmap='gray')
        axes[0,2].set_title('Brightness Distribution')
        axes[0,2].axis('off')
        fig.colorbar(im2, ax=axes[0,2], fraction=0.046)

        # Record brightness statistics
        self.analysis_results["color_analysis"]["brightness"] = {
            "mean": float(np.mean(value)),
            "std": float(np.std(value)),
            "median": float(np.median(value)),
            "min": float(np.min(value)),
            "max": float(np.max(value))
        }

        # RGB histogram
        colors = ('red', 'green', 'blue')
        rgb_stats = {}
        for i, color in enumerate(colors):
            hist = cv2.calcHist([self.image], [i], None, [256], [0, 256])
            axes[1,0].plot(hist, color=color, alpha=0.7, linewidth=2)
            rgb_stats[color] = {
                "mean": float(np.mean(self.image[:,:,i])),
                "std": float(np.std(self.image[:,:,i])),
                "dominant_peak": int(np.argmax(hist))
            }
        
        self.analysis_results["color_analysis"]["rgb_channels"] = rgb_stats
        
        axes[1,0].set_title('RGB Channel Distribution')
        axes[1,0].set_xlabel('Pixel Intensity')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].legend(['Red', 'Green', 'Blue'])
        axes[1,0].grid(True, alpha=0.3)

        # Hue distribution
        hue = hsv[:, :, 0]
        hue_hist, hue_bins = np.histogram(hue.ravel(), bins=180, range=(0, 180))
        axes[1,1].hist(hue.ravel(), bins=180, color='purple', alpha=0.7)
        axes[1,1].set_title('Hue Distribution (0-180°)')
        axes[1,1].set_xlabel('Hue Angle')
        axes[1,1].set_ylabel('Pixel Count')
        axes[1,1].grid(True, alpha=0.3)

        # Record hue statistics
        self.analysis_results["color_analysis"]["hue"] = {
            "mean": float(np.mean(hue)),
            "std": float(np.std(hue)),
            "dominant_hue": int(np.argmax(hue_hist)),
            "hue_diversity": float(np.std(hue_hist))  # Higher = more diverse colors
        }

        # K-means clustering for dominant colors
        pixels = self.image.reshape(-1,3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k=8
        _, labels, palette = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
        counts = Counter(labels.flatten())
        palette = np.uint8(palette)
        sorted_colors = sorted(zip(palette, [counts[i]/len(labels) for i in range(k)]),
                               key=lambda x:x[1], reverse=True)

        # Record dominant colors
        dominant_colors = []
        for i, (color, prop) in enumerate(sorted_colors):
            dominant_colors.append({
                "rank": i + 1,
                "rgb": [int(c) for c in color],
                "proportion": float(prop),
                "percentage": float(prop * 100)
            })
        
        self.analysis_results["color_analysis"]["dominant_colors"] = dominant_colors
        self.analysis_results["color_analysis"]["color_complexity"] = len([c for c in dominant_colors if c["percentage"] > 5.0])

        palette_img = np.zeros((100, 800, 3), dtype=np.uint8)
        x_offset = 0
        for color, prop in sorted_colors:
            width = int(800*prop)
            palette_img[:, x_offset:x_offset+width] = color
            x_offset += width
        axes[1,2].imshow(palette_img)
        axes[1,2].set_title('Dominant Colors (K-means Clustering)')
        axes[1,2].axis('off')

        info_text = "Top Color Proportions:"
        for i, (_, prop) in enumerate(sorted_colors[:5]):
            info_text += f"Color {i+1}: {prop*100:.1f}%"
        axes[1,2].text(0.02, 0.98, info_text, transform=axes[1,2].transAxes,
                       fontsize=9, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        self.save_figure(fig, "Color_Analysis", artwork_name)

    def analyze_texture(self, artwork_name):
        fig, axes = plt.subplots(2, 3, figsize=(18,12))
        fig.suptitle('Texture & Brushstroke Analysis - Decoding Artistic Technique', fontsize=16, fontweight='bold')

        axes[0,0].imshow(self.image)
        axes[0,0].set_title('Original Artwork')
        axes[0,0].axis('off')

        # Gabor filter analysis
        real, imag = gabor(self.gray_image, frequency=0.1, theta=0)
        gabor_response = np.sqrt(real**2 + imag**2)
        im1 = axes[0,1].imshow(gabor_response, cmap='hot')
        axes[0,1].set_title('Gabor Filter Response (0°)')
        axes[0,1].axis('off')
        fig.colorbar(im1, ax=axes[0,1], fraction=0.046)

        # Multi-directional Gabor
        angles = [0, 45, 90, 135]
        gabor_combined = np.zeros_like(self.gray_image, dtype=float)
        gabor_responses = {}
        
        for angle in angles:
            real, imag = gabor(self.gray_image, frequency=0.1, theta=np.deg2rad(angle))
            response = np.sqrt(real**2 + imag**2)
            gabor_combined += response
            gabor_responses[f"{angle}_degrees"] = float(np.mean(response))
        
        gabor_combined /= len(angles)
        
        self.analysis_results["texture_analysis"]["gabor_responses"] = gabor_responses
        self.analysis_results["texture_analysis"]["texture_density"] = {
            "mean": float(np.mean(gabor_combined)),
            "std": float(np.std(gabor_combined)),
            "max": float(np.max(gabor_combined))
        }
        
        im2 = axes[0,2].imshow(gabor_combined, cmap='viridis')
        axes[0,2].set_title('Multi-directional Texture Density')
        axes[0,2].axis('off')
        fig.colorbar(im2, ax=axes[0,2], fraction=0.046)

        # Gradient analysis for brushstroke direction
        gx = cv2.Sobel(self.gray_image, cv2.CV_64F, 1, 0, ksize=5)
        gy = cv2.Sobel(self.gray_image, cv2.CV_64F, 0, 1, ksize=5)
        magnitude = np.sqrt(gx**2 + gy**2)
        direction = np.arctan2(gy, gx)
        
        im3 = axes[1,0].imshow(direction, cmap='hsv')
        axes[1,0].set_title('Brushstroke Direction (Color = Angle)')
        axes[1,0].axis('off')
        fig.colorbar(im3, ax=axes[1,0], fraction=0.046)

        # Direction histogram
        direction_deg = np.degrees(direction) % 180
        hist, bins = np.histogram(direction_deg.ravel(), bins=36, range=(0, 180))
        
        axes[1,1].hist(direction_deg.ravel(), bins=36, color='steelblue', alpha=0.7, edgecolor='black')
        axes[1,1].set_title('Brushstroke Direction Histogram')
        axes[1,1].set_xlabel('Angle (degrees)')
        axes[1,1].set_ylabel('Pixel Count')
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].axvline(0, color='red', linestyle='--', alpha=0.5, label='Horizontal')
        axes[1,1].axvline(90, color='green', linestyle='--', alpha=0.5, label='Vertical')
        axes[1,1].legend()

        # Calculate directional preferences
        horizontal_range = np.sum(hist[0:5]) + np.sum(hist[31:36])  # 0-25° and 155-180°
        vertical_range = np.sum(hist[13:23])  # 65-115°
        diagonal_range = np.sum(hist[5:13]) + np.sum(hist[23:31])  # 25-65° and 115-155°
        total_pixels = np.sum(hist)
        
        self.analysis_results["texture_analysis"]["brushstroke_direction"] = {
            "horizontal_percentage": float(horizontal_range / total_pixels * 100),
            "vertical_percentage": float(vertical_range / total_pixels * 100),
            "diagonal_percentage": float(diagonal_range / total_pixels * 100),
            "dominant_angle": float(bins[np.argmax(hist)]),
            "direction_uniformity": float(np.std(hist))  # Lower = more uniform direction
        }

        # Texture intensity
        self.analysis_results["texture_analysis"]["texture_intensity"] = {
            "mean": float(np.mean(magnitude)),
            "std": float(np.std(magnitude)),
            "max": float(np.max(magnitude))
        }
        
        im4 = axes[1,2].imshow(magnitude, cmap='plasma')
        axes[1,2].set_title('Texture Intensity (Edges and Brushstroke Strength)')
        axes[1,2].axis('off')
        fig.colorbar(im4, ax=axes[1,2], fraction=0.046)

        plt.tight_layout()
        self.save_figure(fig, "Texture_Analysis", artwork_name)

    def analyze_structure(self, artwork_name):
        fig, axes = plt.subplots(2,3, figsize=(18,12))
        fig.suptitle('Structure & Composition Analysis - Discovering Hidden Geometry', fontsize=16, fontweight='bold')

        axes[0,0].imshow(self.image)
        axes[0,0].set_title('Original Artwork')
        axes[0,0].axis('off')

        # Edge detection
        edges = cv2.Canny(self.gray_image, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        self.analysis_results["structure_analysis"]["edge_density"] = float(edge_density * 100)
        
        axes[0,1].imshow(edges, cmap='gray')
        axes[0,1].set_title('Canny Edge Detection')
        axes[0,1].axis('off')

        # Multi-scale edges
        edges1 = cv2.Canny(self.gray_image, 30, 100)
        edges2 = cv2.Canny(self.gray_image, 50, 150)
        edges3 = cv2.Canny(self.gray_image, 100, 200)
        
        edge_combined = np.zeros_like(self.image)
        edge_combined[:,:,0] = edges1
        edge_combined[:,:,1] = edges2
        edge_combined[:,:,2] = edges3
        
        self.analysis_results["structure_analysis"]["multi_scale_edges"] = {
            "fine_detail_percentage": float(np.sum(edges1 > 0) / edges1.size * 100),
            "medium_detail_percentage": float(np.sum(edges2 > 0) / edges2.size * 100),
            "coarse_detail_percentage": float(np.sum(edges3 > 0) / edges3.size * 100)
        }
        
        axes[0,2].imshow(edge_combined)
        axes[0,2].set_title('Multi-scale Edges (R=detail, G=medium, B=main)')
        axes[0,2].axis('off')

        # Superpixel segmentation
        segments = segmentation.slic(self.image, n_segments=200, compactness=10, sigma=1)
        segmented = color.label2rgb(segments, self.image, kind='avg')
        
        num_segments = len(np.unique(segments))
        self.analysis_results["structure_analysis"]["segmentation"] = {
            "num_regions": int(num_segments),
            "average_region_size": float(self.image.shape[0] * self.image.shape[1] / num_segments)
        }
        
        axes[1,0].imshow(segmentation.mark_boundaries(segmented, segments))
        axes[1,0].set_title('Superpixel Segmentation')
        axes[1,0].axis('off')

        # Morphological gradient
        kernel = np.ones((5,5), np.uint8)
        gradient = cv2.morphologyEx(self.gray_image, cv2.MORPH_GRADIENT, kernel)
        
        self.analysis_results["structure_analysis"]["morphological_gradient"] = {
            "mean": float(np.mean(gradient)),
            "std": float(np.std(gradient))
        }
        
        im1 = axes[1,1].imshow(gradient, cmap='hot')
        axes[1,1].set_title('Morphological Gradient')
        axes[1,1].axis('off')
        fig.colorbar(im1, ax=axes[1,1], fraction=0.046)

        # Line detection
        edges_hough = cv2.Canny(self.gray_image, 50, 150)
        lines = cv2.HoughLinesP(edges_hough, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        line_image = self.image.copy()
        
        num_lines = 0
        line_lengths = []
        line_angles = []
        
        if lines is not None:
            num_lines = len(lines)
            for line in lines[:50]:
                x1,y1,x2,y2 = line[0]
                cv2.line(line_image, (x1,y1), (x2,y2), (255,0,0), 2)
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                angle = np.degrees(np.arctan2(y2-y1, x2-x1)) % 180
                line_lengths.append(length)
                line_angles.append(angle)
        
        self.analysis_results["structure_analysis"]["line_detection"] = {
            "num_lines": int(num_lines),
            "average_line_length": float(np.mean(line_lengths)) if line_lengths else 0,
            "line_angle_std": float(np.std(line_angles)) if line_angles else 0,
            "geometric_complexity": "high" if num_lines > 100 else "medium" if num_lines > 50 else "low"
        }

        axes[1,2].imshow(line_image)
        axes[1,2].set_title(f'Line Detection ({num_lines} lines found)')
        axes[1,2].axis('off')

        plt.tight_layout()
        self.save_figure(fig, "Structure_Analysis", artwork_name)

    def analyze_light_shadow(self, artwork_name):
        fig, axes = plt.subplots(2,3, figsize=(18,12))
        fig.suptitle('Light & Shadow Analysis - Chiaroscuro Technique', fontsize=16, fontweight='bold')

        axes[0,0].imshow(self.image)
        axes[0,0].set_title('Original Artwork')
        axes[0,0].axis('off')

        # Luminance statistics
        luminance_stats = {
            "mean": float(np.mean(self.gray_image)),
            "std": float(np.std(self.gray_image)),
            "median": float(np.median(self.gray_image)),
            "min": float(np.min(self.gray_image)),
            "max": float(np.max(self.gray_image)),
            "dynamic_range": float(np.max(self.gray_image) - np.min(self.gray_image))
        }
        
        self.analysis_results["light_shadow_analysis"]["luminance"] = luminance_stats
        
        im1 = axes[0,1].imshow(self.gray_image, cmap='gray')
        axes[0,1].set_title('Luminance Map (Bright=white, Dark=black)')
        axes[0,1].axis('off')
        fig.colorbar(im1, ax=axes[0,1], fraction=0.046)

        # Contrast enhancement
        equalized = cv2.equalizeHist(self.gray_image)
        axes[0,2].imshow(equalized, cmap='gray')
        axes[0,2].set_title('Contrast Enhanced')
        axes[0,2].axis('off')

        # Local contrast
        adaptive_thresh = cv2.adaptiveThreshold(self.gray_image, 255,
                                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY, 11, 2)
        axes[1,0].imshow(adaptive_thresh, cmap='gray')
        axes[1,0].set_title('Local Contrast Zones')
        axes[1,0].axis('off')

        # Light-shadow transitions
        sobelx = cv2.Sobel(self.gray_image, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(self.gray_image, cv2.CV_64F, 0, 1, ksize=5)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        self.analysis_results["light_shadow_analysis"]["transition_intensity"] = {
            "mean": float(np.mean(gradient_magnitude)),
            "std": float(np.std(gradient_magnitude)),
            "max": float(np.max(gradient_magnitude))
        }
        
        im2 = axes[1,1].imshow(gradient_magnitude, cmap='inferno')
        axes[1,1].set_title('Light-Shadow Transition Zones')
        axes[1,1].axis('off')
        fig.colorbar(im2, ax=axes[1,1], fraction=0.046)

        # Tonal distribution
        hist, bins = np.histogram(self.gray_image.ravel(), bins=256, range=[0,256])
        axes[1,2].fill_between(bins[:-1], hist, alpha=0.7, color='skyblue')
        axes[1,2].plot(bins[:-1], hist, color='navy', linewidth=2)
        
        shadow_pixels = np.sum(self.gray_image < 85)
        midtone_pixels = np.sum((self.gray_image >= 85) & (self.gray_image < 170))
        highlight_pixels = np.sum(self.gray_image >= 170)
        total = self.gray_image.size
        
        tonal_distribution = {
            "shadows_percentage": float(shadow_pixels/total*100),
            "midtones_percentage": float(midtone_pixels/total*100),
            "highlights_percentage": float(highlight_pixels/total*100),
            "contrast_ratio": float(highlight_pixels / (shadow_pixels + 1))  # Avoid division by zero
        }
        
        self.analysis_results["light_shadow_analysis"]["tonal_distribution"] = tonal_distribution
        
        axes[1,2].axvspan(0,85, alpha=0.3, color='black', label=f'Shadows {tonal_distribution["shadows_percentage"]:.1f}%')
        axes[1,2].axvspan(85,170, alpha=0.3, color='gray', label=f'Midtones {tonal_distribution["midtones_percentage"]:.1f}%')
        axes[1,2].axvspan(170,255, alpha=0.3, color='yellow', label=f'Highlights {tonal_distribution["highlights_percentage"]:.1f}%')
        axes[1,2].set_title('Tonal Distribution')
        axes[1,2].set_xlabel('Luminance')
        axes[1,2].set_ylabel('Pixel Count')
        axes[1,2].legend()
        axes[1,2].grid(True, alpha=0.3)

        plt.tight_layout()
        self.save_figure(fig, "Light_Shadow_Analysis", artwork_name)

    def analyze_frequency_domain(self, artwork_name):
        fig, axes = plt.subplots(2,2, figsize=(14,14))
        fig.suptitle('Frequency Domain Analysis - Fourier Transform', fontsize=16, fontweight='bold')

        axes[0,0].imshow(self.image)
        axes[0,0].set_title('Original Artwork')
        axes[0,0].axis('off')

        # Fourier transform
        f_transform = fft2(self.gray_image)
        f_shift = fftshift(f_transform)
        magnitude_spectrum = 20*np.log(np.abs(f_shift)+1)
        
        im1 = axes[0,1].imshow(magnitude_spectrum, cmap='hot')
        axes[0,1].set_title('Frequency Spectrum (Center=Low Freq)')
        axes[0,1].axis('off')
        fig.colorbar(im1, ax=axes[0,1], fraction=0.046)

        # Frequency analysis
        rows, cols = self.gray_image.shape
        crow, ccol = rows//2, cols//2
        
        # Calculate energy in different frequency bands
        center_region = magnitude_spectrum[crow-30:crow+30, ccol-30:ccol+30]
        low_freq_energy = float(np.mean(center_region))
        high_freq_energy = float(np.mean(magnitude_spectrum) - low_freq_energy)
        
        self.analysis_results["frequency_analysis"]["frequency_distribution"] = {
            "low_frequency_energy": low_freq_energy,
            "high_frequency_energy": high_freq_energy,
            "detail_level": "high" if high_freq_energy > low_freq_energy * 0.5 else "medium" if high_freq_energy > low_freq_energy * 0.3 else "low"
        }

        # Low-pass filter
        mask = np.zeros((rows,cols), np.uint8)
        r = 30
        x,y = np.ogrid[:rows,:cols]
        mask_area = (x - crow)**2 + (y - ccol)**2 <= r*r
        mask[mask_area] = 1

        f_shift_lowpass = f_shift * mask
        f_ishift = np.fft.ifftshift(f_shift_lowpass)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        axes[1,0].imshow(img_back, cmap='gray')
        axes[1,0].set_title('Low Frequency Reconstruction')
        axes[1,0].axis('off')

        # High-pass filter
        mask_highpass = 1 - mask
        f_shift_highpass = f_shift * mask_highpass
        f_ishift = np.fft.ifftshift(f_shift_highpass)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        axes[1,1].imshow(img_back, cmap='gray')
        axes[1,1].set_title('High Frequency Reconstruction')
        axes[1,1].axis('off')

        plt.tight_layout()
        self.save_figure(fig, "Frequency_Analysis", artwork_name)

    def save_analysis_to_json(self, artwork_name, artist="", period="", style_notes=""):
        """Save all analysis results to a JSON file"""
        # Add artwork metadata
        self.analysis_results["artwork_info"] = {
            "name": artwork_name,
            "artist": artist,
            "period": period,
            "style_notes": style_notes
        }
        
        # Create output folder
        folder = os.path.join(self.output_root, artwork_name)
        os.makedirs(folder, exist_ok=True)
        
        # Save JSON file
        json_path = os.path.join(folder, f"{artwork_name}_analysis.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=4, ensure_ascii=False)
        
        print(f"\n✓ Analysis results saved to: {json_path}")
        return json_path

    def generate_comprehensive_report(self, artwork_name="", artist="", period="", style_notes=""):
        print("" + "="*80)
        print("Artwork Computational Image Analysis Report".center(80))
        print("="*80)
        if artwork_name:
            print(f"Artwork Name: {artwork_name}")
        if artist:
            print(f"Artist: {artist}")
        if period:
            print(f"Period: {period}")
        if style_notes:
            print(f"Style Notes: {style_notes}")
        print("-"*80)
        print("""
Analysis Dimensions:

1. Color Analysis
   - Dominant color extraction via K-means clustering
   - HSV color space distribution analysis

2. Texture Analysis
   - Gabor filter responses reveal brushstroke direction and texture density
   - Gradient direction histogram for strokes' orientations

3. Structure & Composition
   - Edge detection and multi-scale analysis
   - Superpixel segmentation reveals region partitioning
   - Hough transform to discover underlying geometric lines

4. Light & Shadow
   - Tonal contrast exploration (Chiaroscuro technique)
   - Local contrast zones and shadow/midtone/highlight proportions

5. Frequency Domain
   - Fourier transform decomposes image into frequency components
   - Low frequency reconstructs broad shapes; high frequency shows fine detail
""")
        print("="*80)
        print("""
Advanced Image Processing Concepts:

- Gabor Filters simulate human visual cortex texture perception.
- HSV color space aligns with human color perception better than RGB.
- Fourier transforms analyze image frequencies as 'spatial sound waves'.
- Superpixels group pixels into perceptual regions, improving segmentation.
- Canny Edge detection accurately captures important edges amidst noise.
""")
        print("="*80)

    def run_complete_analysis(self, artwork_name="", artist="", period="", style_notes=""):
        print(f"Starting analysis: {artwork_name} by {artist}\n")
        self.preprocess_image(denoise=True, enhance_contrast=True)
        self.analyze_color_distribution(artwork_name)
        self.analyze_texture(artwork_name)
        self.analyze_structure(artwork_name)
        self.analyze_light_shadow(artwork_name)
        self.analyze_frequency_domain(artwork_name)
        self.generate_comprehensive_report(artwork_name, artist, period, style_notes)
        
        # Save analysis results to JSON
        json_path = self.save_analysis_to_json(artwork_name, artist, period, style_notes)
        return json_path

if __name__ == "__main__":
    # Make sure your image paths are raw strings or properly escaped
    renaissance_path = r'E:\薛云起研究生期间课程\艺术与科学\pictures\文艺复兴\威尼斯人画像.jpg'
    baroque_path = r'E:\薛云起研究生期间课程\艺术与科学\pictures\巴洛克艺术\亚伯拉罕lanbeici.jpg'

    print("="*80)
    print("ARTWORK ANALYSIS SYSTEM - Renaissance vs Baroque Comparison".center(80))
    print("="*80)

    # Analyze Renaissance artwork
    print("" + ">"*80)
    print("ANALYZING RENAISSANCE ARTWORK".center(80))
    print(">"*80)
    renaissance_analyzer = ArtworkAnalyzer(renaissance_path, output_root='analysis_results')
    renaissance_json = renaissance_analyzer.run_complete_analysis(
        artwork_name="The_Venetian",
        artist="Leonardo da Vinci",
        period="Renaissance",
        style_notes="Balance, harmony, delicate light and precise anatomy"
    )

    # Analyze Baroque artwork
    print("" + ">"*80)
    print("ANALYZING BAROQUE ARTWORK".center(80))
    print(">"*80)
    baroque_analyzer = ArtworkAnalyzer(baroque_path, output_root='analysis_results')
    baroque_json = baroque_analyzer.run_complete_analysis(
        artwork_name="Abraham",
        artist="Peter Paul Rubens",
        period="Baroque",
        style_notes="Dynamic composition, strong chiaroscuro, dramatic scenes"
    )

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!".center(80))
    print("="*80)
    print(f"\nRenaissance JSON: {renaissance_json}")
    print(f"Baroque JSON: {baroque_json}")
    print("\nNext steps:")
    print("1. Review the generated JSON files")
    print("2. Share the JSON data for presentation script generation")
    print("3. Use the quantitative metrics to support your art historical analysis")
    print("="*80)
