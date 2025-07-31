#!/usr/bin/env python3
"""
FlexLink Image Database Uploader
Uploads extracted images and blueprint drawings to the database
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from image_extractor import FlexLinkImageExtractor, ExtractedImage


class FlexLinkImageUploader:
    def __init__(self):
        """Initialize the image uploader"""
        load_dotenv()
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ Missing Supabase credentials in .env file")

        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }

        self.image_extractor = FlexLinkImageExtractor()

    def upload_images_to_database(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload a list of images to the database"""
        if not images:
            print("❌ No images to upload")
            return {'success': False, 'message': 'No images provided'}

        print(f"🔄 Uploading {len(images)} images to database...")

        success_count = 0
        error_count = 0
        errors = []

        for i, image_data in enumerate(images):
            try:
                # Upload single image
                result = self._upload_single_image(image_data)
                if result['success']:
                    success_count += 1
                    print(
                        f"✅ Uploaded image {i+1}/{len(images)}: {image_data.get('product_code', 'Unknown')}")
                else:
                    error_count += 1
                    errors.append(f"Image {i+1}: {result['message']}")
                    print(
                        f"❌ Failed to upload image {i+1}/{len(images)}: {result['message']}")

            except Exception as e:
                error_count += 1
                error_msg = f"Image {i+1}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ Error uploading image {i+1}/{len(images)}: {e}")

        # Create summary
        summary = {
            'success': error_count == 0,
            'total_images': len(images),
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }

        print(f"📊 Upload Summary:")
        print(f"   Total images: {summary['total_images']}")
        print(f"   Successfully uploaded: {summary['success_count']}")
        print(f"   Failed uploads: {summary['error_count']}")

        return summary

    def _upload_single_image(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a single image to the database"""
        try:
            # Prepare the data for upload
            upload_data = {
                'image_hash': image_data['image_hash'],
                'page_number': image_data['page_number'],
                'x_coord': image_data['x_coord'],
                'y_coord': image_data['y_coord'],
                'width': image_data['width'],
                'height': image_data['height'],
                'image_format': image_data['image_format'],
                'image_data': image_data['image_data'],  # Base64 encoded
                'associated_text': image_data.get('associated_text', ''),
                'product_code': image_data.get('product_code', ''),
                'component_type': image_data.get('component_type', ''),
                'is_blueprint': image_data.get('is_blueprint', True),
                'image_quality_score': image_data.get('image_quality_score', 0.8)
            }

            # Make the API call
            response = requests.post(
                f"{self.supabase_url}/rest/v1/product_images",
                headers=self.headers,
                json=upload_data
            )

            if response.status_code == 201:
                return {'success': True, 'message': 'Image uploaded successfully'}
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                return {'success': False, 'message': error_msg}

        except Exception as e:
            return {'success': False, 'message': str(e)}

    def process_and_upload_pdf(self, pdf_path: str, save_local: bool = True) -> Dict[str, Any]:
        """Process PDF and upload extracted images to database"""
        print(f"🔄 Processing PDF: {pdf_path}")

        # Extract images from PDF
        extraction_result = self.image_extractor.process_pdf_images(
            pdf_path,
            save_local=save_local
        )

        if not extraction_result or not extraction_result.get('database_images'):
            print("❌ No images extracted from PDF")
            return {'success': False, 'message': 'No images extracted'}

        # Upload images to database
        upload_result = self.upload_images_to_database(
            extraction_result['database_images'])

        # Combine results
        combined_result = {
            'extraction': extraction_result,
            'upload': upload_result,
            'success': upload_result['success']
        }

        return combined_result

    def get_image_statistics(self) -> Dict[str, Any]:
        """Get statistics about images in the database"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/rpc/get_image_stats",
                headers=self.headers
            )

            if response.status_code == 200:
                stats = response.json()
                if stats:
                    return stats[0]  # Return first row
                else:
                    return {'error': 'No statistics available'}
            else:
                return {'error': f'HTTP {response.status_code}: {response.text}'}

        except Exception as e:
            return {'error': str(e)}

    def search_images(self, product_code: Optional[str] = None,
                      component_type: Optional[str] = None,
                      is_blueprint: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Search for images in the database"""
        try:
            # Build query parameters
            params = {}
            if product_code:
                params['p_product_code'] = product_code
            if component_type:
                params['p_component_type'] = component_type
            if is_blueprint is not None:
                params['p_is_blueprint'] = is_blueprint

            response = requests.get(
                f"{self.supabase_url}/rest/v1/rpc/search_product_images",
                headers=self.headers,
                params=params
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error searching images: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error searching images: {e}")
            return []

    def get_product_images(self, product_code: str) -> List[Dict[str, Any]]:
        """Get all images for a specific product"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/rpc/get_product_images",
                headers=self.headers,
                params={'p_product_code': product_code}
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"❌ Error getting product images: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error getting product images: {e}")
            return []

    def get_blueprint_images(self, component_type: str) -> List[Dict[str, Any]]:
        """Get blueprint images for a specific component type"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/rpc/get_blueprint_images",
                headers=self.headers,
                params={'p_component_type': component_type}
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"❌ Error getting blueprint images: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error getting blueprint images: {e}")
            return []

    def delete_image(self, image_hash: str) -> bool:
        """Delete an image from the database"""
        try:
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/product_images?image_hash=eq.{image_hash}",
                headers=self.headers
            )

            if response.status_code == 204:
                print(f"✅ Deleted image with hash: {image_hash}")
                return True
            else:
                print(f"❌ Error deleting image: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error deleting image: {e}")
            return False

    def clear_all_images(self) -> bool:
        """Clear all images from the database (use with caution!)"""
        try:
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/product_images",
                headers=self.headers
            )

            if response.status_code == 204:
                print("✅ Cleared all images from database")
                return True
            else:
                print(f"❌ Error clearing images: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error clearing images: {e}")
            return False


def main():
    """Main function for testing the image uploader"""
    uploader = FlexLinkImageUploader()

    print("🔄 FlexLink Image Uploader")
    print("1. Process PDF and upload images")
    print("2. Get image statistics")
    print("3. Search images")
    print("4. Get product images")
    print("5. Get blueprint images")
    print("6. Delete image")
    print("7. Clear all images")

    choice = input("\nEnter your choice (1-7): ").strip()

    if choice == "1":
        pdf_path = input("Enter PDF path: ").strip()
        if pdf_path:
            result = uploader.process_and_upload_pdf(pdf_path)
            if result['success']:
                print("✅ Successfully processed and uploaded images")
            else:
                print("❌ Failed to process and upload images")
        else:
            print("❌ No PDF path provided")

    elif choice == "2":
        stats = uploader.get_image_statistics()
        if 'error' not in stats:
            print(f"📊 Image Statistics:")
            print(f"   Total images: {stats.get('total_images', 0)}")
            print(f"   Blueprint images: {stats.get('blueprint_images', 0)}")
            print(
                f"   Products with images: {stats.get('products_with_images', 0)}")
            print(
                f"   Component types with images: {stats.get('component_types_with_images', 0)}")
            print(
                f"   Average image size: {stats.get('avg_image_size_kb', 0):.2f} KB")
            print(
                f"   Average quality score: {stats.get('avg_quality_score', 0):.2f}")
        else:
            print(f"❌ Error getting statistics: {stats['error']}")

    elif choice == "3":
        product_code = input(
            "Enter product code (or press Enter to skip): ").strip() or None
        component_type = input(
            "Enter component type (or press Enter to skip): ").strip() or None
        is_blueprint_input = input(
            "Search only blueprints? (y/n, or press Enter to skip): ").strip()
        is_blueprint = None
        if is_blueprint_input.lower() == 'y':
            is_blueprint = True
        elif is_blueprint_input.lower() == 'n':
            is_blueprint = False

        images = uploader.search_images(
            product_code, component_type, is_blueprint)
        print(f"🔍 Found {len(images)} images")
        for img in images:
            print(
                f"   - {img.get('product_code', 'Unknown')} ({img.get('component_type', 'Unknown')}) on page {img.get('page_number', 0)}")

    elif choice == "4":
        product_code = input("Enter product code: ").strip()
        if product_code:
            images = uploader.get_product_images(product_code)
            print(f"📋 Found {len(images)} images for product {product_code}")
            for img in images:
                print(
                    f"   - Page {img.get('page_number', 0)}: {img.get('component_type', 'Unknown')} (Blueprint: {img.get('is_blueprint', False)})")
        else:
            print("❌ No product code provided")

    elif choice == "5":
        component_type = input("Enter component type: ").strip()
        if component_type:
            images = uploader.get_blueprint_images(component_type)
            print(
                f"🔧 Found {len(images)} blueprint images for {component_type}")
            for img in images:
                print(
                    f"   - {img.get('product_code', 'Unknown')} on page {img.get('page_number', 0)} (Quality: {img.get('image_quality_score', 0):.2f})")
        else:
            print("❌ No component type provided")

    elif choice == "6":
        image_hash = input("Enter image hash to delete: ").strip()
        if image_hash:
            success = uploader.delete_image(image_hash)
            if not success:
                print("❌ Failed to delete image")
        else:
            print("❌ No image hash provided")

    elif choice == "7":
        confirm = input(
            "⚠️ Are you sure you want to clear ALL images? (yes/no): ").strip()
        if confirm.lower() == 'yes':
            success = uploader.clear_all_images()
            if not success:
                print("❌ Failed to clear images")
        else:
            print("❌ Operation cancelled")

    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
