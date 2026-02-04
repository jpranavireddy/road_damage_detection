#!/usr/bin/env python3
"""
Simple test to verify the batch processing works
"""

from batch_processor import BatchRoadDamageProcessor
import os

def test_batch_processing():
    print("🧪 Testing Batch Processing System")
    
    # Initialize processor
    processor = BatchRoadDamageProcessor(confidence_threshold=0.3)
    
    # Test with sample images
    input_folder = "sample_drone_images"
    flight_name = "Test_Flight"
    
    if not os.path.exists(input_folder):
        print(f"❌ Sample images folder not found: {input_folder}")
        return False
    
    try:
        # Process the folder
        results = processor.process_folder(input_folder, flight_name)
        
        print("✅ Batch processing completed successfully!")
        print(f"📊 Results:")
        print(f"   - Total images: {results['summary']['total_images']}")
        print(f"   - Damaged roads: {results['summary']['damaged_count']}")
        print(f"   - Clean roads: {results['summary']['clean_count']}")
        
        # Check if area analysis exists
        if 'area_analysis' in results:
            area_analysis = results['area_analysis']
            print(f"   - Overall condition: {area_analysis.get('overall_condition', 'Unknown')}")
            print(f"   - Area name: {area_analysis.get('area_name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during batch processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_batch_processing()
    if success:
        print("\n🎉 All tests passed! The system is working correctly.")
    else:
        print("\n💥 Tests failed. Please check the errors above.")