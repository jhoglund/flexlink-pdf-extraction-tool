#!/usr/bin/env python3
"""
FlexLink Image Extractor Tool
Extracts images (blueprint drawings) from FlexLink catalog PDFs
"""
import os
import re
import json
import base64
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import io
from PIL import Image
import fitz  # PyMuPDF
from dotenv import load_dotenv


@dataclass
class ExtractedImage:
    image_data: bytes
    image_hash: str
    page_number: int
    x_coord: float
    y_coord: float
    width: float
    height: float
    image_format: str
    associated_text: str = ""
    product_code: str = ""
    component_type: str = ""


class FlexLinkImageExtractor:
    def __init__(self):
        load_dotenv()

        # Supabase configuration
        self.supabase_url = os.getenv('SUPABASE_URL', '')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY', '')

        # Blueprint detection patterns
        self.technical_terms = [
            'dimension', 'mm', 'drawing', 'technical', 'specification',
            'chain', 'sprocket', 'bearing', 'roller', 'link', 'drive',
            'pitch', 'diameter', 'width', 'length', 'height', 'thickness',
            'material', 'steel', 'aluminum', 'plastic', 'nylon',
            'tolerance', 'tolerance', 'clearance', 'fit', 'assembly'
        ]

        # Product code patterns (FlexLink specific)
        self.product_patterns = [
            r'\bX\d+\b',  # X45, X65, etc.
            r'\bXS\b',    # XS series
            r'\bXH\b',    # XH series
            r'\b[0-9]{3,4}[A-Z]?\b',  # 3-4 digit codes
            r'\b[A-Z]{1,3}\d{1,3}\b'  # Letter + number combinations
        ]

        # Component type patterns
        self.component_patterns = [
            r'\bchain\b', r'\bsprocket\b', r'\bbearing\b', r'\broller\b',
            r'\blink\b', r'\bdrive\b', r'\bmotor\b', r'\bgear\b',
            r'\bwheel\b', r'\bplate\b', r'\bbracket\b', r'\bsupport\b',
            r'\bguide\b', r'\btrack\b', r'\bcarrier\b', r'\battachment\b'
        ]

        # Quality thresholds
        self.min_image_size = 100  # Minimum width/height in pixels
        self.quality_threshold = 0.6  # Blueprint detection threshold
        self.min_aspect_ratio = 0.5  # Minimum aspect ratio
        self.max_aspect_ratio = 3.0  # Maximum aspect ratio

    def extract_images_from_pdf(self, pdf_path: str) -> List[ExtractedImage]:
        """Extract all images from PDF"""
        images = []

        try:
            doc = fitz.open(pdf_path)
            print(f"📄 Processing PDF: {pdf_path}")
            print(f"📊 Total pages: {len(doc)}")

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_images = self._extract_images_from_page(page, page_num)
                images.extend(page_images)

                if page_num % 50 == 0 and page_num > 0:
                    print(f"📄 Processed {page_num + 1}/{len(doc)} pages...")

            doc.close()
            print(f"✅ Extracted {len(images)} images from PDF")

        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return []

        return images

    def _extract_images_from_page(self, page: fitz.Page, page_num: int) -> List[ExtractedImage]:
        """Extract images from a single page"""
        images = []

        try:
            # Get image list from page - try different methods
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]

                    # Try to get pixmap
                    try:
                        pix = fitz.Pixmap(page.parent, xref)
                    except Exception as e:
                        # Try alternative method for problematic images
                        try:
                            pix = fitz.Pixmap(
                                page.parent, xref, page.parent.extract_image(xref)["image"])
                        except:
                            continue

                    # Skip if image is too small
                    if pix.width < self.min_image_size or pix.height < self.min_image_size:
                        pix = None
                        continue

                    # Convert to PIL Image for processing
                    try:
                        img_data = pix.tobytes("png")
                        pil_image = Image.open(io.BytesIO(img_data))
                    except Exception as e:
                        # Try alternative format if PNG fails
                        try:
                            img_data = pix.tobytes("jpeg")
                            pil_image = Image.open(io.BytesIO(img_data))
                        except:
                            pix = None
                            continue

                    # Get image coordinates and dimensions
                    try:
                        img_rect = page.get_image_bbox(img)
                        x_coord = img_rect.x0
                        y_coord = img_rect.y0
                        width = img_rect.width
                        height = img_rect.height
                    except:
                        # Use default coordinates if bbox not available
                        x_coord = 0
                        y_coord = 0
                        width = pix.width
                        height = pix.height

                    # Generate hash
                    image_hash = hashlib.md5(img_data).hexdigest()

                    # Get surrounding text
                    associated_text = self._get_surrounding_text(
                        page, img_rect if 'img_rect' in locals() else fitz.Rect(0, 0, width, height))

                    # Extract product and component information
                    product_code = self._extract_product_code(associated_text)
                    component_type = self._extract_component_type(
                        associated_text)

                    # Create ExtractedImage object
                    extracted_image = ExtractedImage(
                        image_data=img_data,
                        image_hash=image_hash,
                        page_number=page_num + 1,
                        x_coord=x_coord,
                        y_coord=y_coord,
                        width=width,
                        height=height,
                        image_format='png',
                        associated_text=associated_text,
                        product_code=product_code,
                        component_type=component_type
                    )

                    images.append(extracted_image)

                    # Clean up
                    pix = None

                except Exception as e:
                    # Skip problematic images but continue processing
                    print(
                        f"⚠️ Error processing image {img_index} on page {page_num + 1}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error processing page {page_num + 1}: {e}")

        return images

    def _get_surrounding_text(self, page: fitz.Page, img_rect: fitz.Rect) -> str:
        """Extract text surrounding the image"""
        try:
            # Expand the rectangle to capture more surrounding text
            # Add 50 points in each direction
            expanded_rect = img_rect + (50, 50, 50, 50)

            # Get text blocks in the expanded area
            text_blocks = page.get_text("dict")["blocks"]
            surrounding_text = []

            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            span_rect = fitz.Rect(span["bbox"])
                            if span_rect.intersects(expanded_rect):
                                surrounding_text.append(span["text"])

            return " ".join(surrounding_text)

        except Exception as e:
            print(f"⚠️ Error extracting surrounding text: {e}")
            return ""

    def _extract_product_code(self, text: str) -> str:
        """Extract product code from text"""
        text_upper = text.upper()

        for pattern in self.product_patterns:
            matches = re.findall(pattern, text_upper)
            if matches:
                return matches[0]

        return ""

    def _extract_component_type(self, text: str) -> str:
        """Extract component type from text"""
        text_lower = text.lower()

        for pattern in self.component_patterns:
            if re.search(pattern, text_lower):
                return re.search(pattern, text_lower).group()

        return ""

    def filter_blueprint_images(self, images: List[ExtractedImage]) -> List[ExtractedImage]:
        """Filter images to identify blueprint drawings"""
        blueprint_images = []

        for image in images:
            try:
                # Convert image data to PIL Image
                pil_image = Image.open(io.BytesIO(image.image_data))

                # Check if it's likely a blueprint drawing
                if self._is_blueprint_drawing(pil_image, image.associated_text):
                    blueprint_images.append(image)

            except Exception as e:
                print(
                    f"⚠️ Error processing image for blueprint detection: {e}")
                continue

        return blueprint_images

    def _is_blueprint_drawing(self, image: Image.Image, associated_text: str) -> bool:
        """Determine if an image is likely a blueprint drawing"""
        try:
            # Convert to grayscale for analysis
            gray_image = image.convert('L')

            # Calculate image properties
            width, height = gray_image.size
            aspect_ratio = width / height if height > 0 else 0

            # Check aspect ratio (blueprints are often rectangular)
            if aspect_ratio < self.min_aspect_ratio or aspect_ratio > self.max_aspect_ratio:
                return False

            # Calculate brightness and contrast
            pixels = list(gray_image.getdata())
            avg_brightness = sum(pixels) / len(pixels)

            # Calculate contrast (standard deviation)
            variance = sum((p - avg_brightness) **
                           2 for p in pixels) / len(pixels)
            contrast = variance ** 0.5

            # Check for technical text indicators
            text_score = 0
            text_lower = associated_text.lower()
            for term in self.technical_terms:
                if term in text_lower:
                    text_score += 1

            # Calculate overall blueprint score
            brightness_score = 1.0 if 50 <= avg_brightness <= 200 else 0.5
            contrast_score = 1.0 if contrast > 30 else 0.5
            text_score = min(text_score / 3, 1.0)  # Normalize text score

            blueprint_score = (brightness_score +
                               contrast_score + text_score) / 3

            return blueprint_score >= self.quality_threshold

        except Exception as e:
            print(f"⚠️ Error in blueprint detection: {e}")
            return False

    def save_images_locally(self, images: List[ExtractedImage], output_dir: str) -> Dict[str, str]:
        """Save extracted images to local directory"""
        saved_files = {}

        try:
            os.makedirs(output_dir, exist_ok=True)

            for i, image in enumerate(images):
                filename = f"image_{image.page_number:03d}_{i:03d}_{image.image_hash[:8]}.png"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(image.image_data)

                saved_files[image.image_hash] = filepath

            print(f"💾 Saved {len(saved_files)} images to {output_dir}")

        except Exception as e:
            print(f"❌ Error saving images: {e}")

        return saved_files

    def prepare_images_for_database(self, images: List[ExtractedImage]) -> List[Dict[str, Any]]:
        """Prepare images for database upload"""
        db_images = []

        for image in images:
            try:
                # Convert image data to base64
                image_base64 = base64.b64encode(
                    image.image_data).decode('utf-8')

                # Create database record
                db_record = {
                    'image_hash': image.image_hash,
                    'page_number': image.page_number,
                    'x_coord': float(image.x_coord),
                    'y_coord': float(image.y_coord),
                    'width': float(image.width),
                    'height': float(image.height),
                    'image_format': image.image_format,
                    'image_data': image_base64,
                    'associated_text': image.associated_text,
                    'product_code': image.product_code,
                    'component_type': image.component_type,
                    'is_blueprint': True,  # All images passed through filter are blueprints
                    'image_quality_score': 0.8  # Default quality score
                }

                db_images.append(db_record)

            except Exception as e:
                print(f"⚠️ Error preparing image for database: {e}")
                continue

        return db_images

    def process_pdf_images(self, pdf_path: str, save_local: bool = True,
                           output_dir: str = "extracted_images") -> Dict[str, Any]:
        """Main method to process PDF and extract blueprint images"""
        print(f"🚀 Starting image extraction from: {pdf_path}")

        # Extract all images
        all_images = self.extract_images_from_pdf(pdf_path)

        if not all_images:
            print("❌ No images found in PDF")
            return {
                'total_images': 0,
                'blueprint_images': 0,
                'saved_files': {},
                'database_records': []
            }

        # Filter for blueprint images
        blueprint_images = self.filter_blueprint_images(all_images)

        print(
            f"🔍 Identified {len(blueprint_images)} blueprint images out of {len(all_images)} total images")

        # Save images locally if requested
        saved_files = {}
        if save_local and blueprint_images:
            saved_files = self.save_images_locally(
                blueprint_images, output_dir)

        # Prepare for database
        database_records = self.prepare_images_for_database(blueprint_images)

        # Print summary
        product_codes = set(
            img.product_code for img in blueprint_images if img.product_code)
        component_types = set(
            img.component_type for img in blueprint_images if img.component_type)

        print(f"📊 Extraction Summary:")
        print(f"   Total images: {len(all_images)}")
        print(f"   Blueprint images: {len(blueprint_images)}")
        print(f"   Product codes found: {len(product_codes)}")
        print(f"   Component types found: {len(component_types)}")

        if product_codes:
            print(f"   Product codes: {', '.join(product_codes)}")
        if component_types:
            print(f"   Component types: {', '.join(component_types)}")

        return {
            'total_images': len(all_images),
            'blueprint_images': len(blueprint_images),
            'saved_files': saved_files,
            'database_records': database_records,
            'product_codes': list(product_codes),
            'component_types': list(component_types)
        }


def main():
    """Main function for testing the image extractor"""
    extractor = FlexLinkImageExtractor()

    # Example usage
    pdf_path = input("Enter PDF path: ").strip()

    if not pdf_path:
        print("❌ No PDF path provided")
        return

    # Process the PDF
    result = extractor.process_pdf_images(pdf_path)

    if result:
        print(
            f"✅ Successfully processed {result['blueprint_images']} blueprint images")

        # Show some statistics
        if result['product_codes']:
            print(
                f"📋 Product codes found: {', '.join(result['product_codes'])}")

        if result['component_types']:
            print(
                f"🔧 Component types found: {', '.join(result['component_types'])}")
    else:
        print("❌ No images were extracted")


if __name__ == "__main__":
    main()
