"""
Test script to verify all imports work correctly in the modular structure.
"""
import sys
import traceback

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing modular structure imports...")
    
    try:
        print("✓ Importing models...")
        from models import TimeSlot, Room, Instructor, Course, Assignment
        print("  - TimeSlot, Room, Instructor, Course, Assignment imported successfully")
        
        print("✓ Importing data_loader...")
        from data_loader import load_timeslots, load_rooms, load_instructors, load_courses
        print("  - CSV loading functions imported successfully")
        
        print("✓ Importing csp...")
        from csp import generate_schedule_from_memory, build_domains, is_consistent
        print("  - CSP solver functions imported successfully")
        
        print("✓ Importing output_utils...")
        from output_utils import write_schedule_csv, print_schedule, get_proper_sort_key
        print("  - Output utility functions imported successfully")
        
        print("✓ Importing htmlexport...")
        from htmlexport import export_schedule_html, export_instructor_html, export_grid_html
        print("  - HTML export functions imported successfully")
        
        print("✓ Importing gui...")
        from gui import run_gui
        print("  - GUI application imported successfully")
        
        print("\n🎉 All imports successful! The modular structure is working correctly.")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ Modular structure test passed!")
        sys.exit(0)
    else:
        print("\n❌ Modular structure test failed!")
        sys.exit(1)
