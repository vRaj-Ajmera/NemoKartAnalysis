import os
from OCR_test_cases import test_cases
from OCR_testing_helper import process_image

# ANSI escape codes for colors
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

def run_tests():
    # Base path for race screenshots
    base_dir = os.path.dirname(__file__)
    screenshots_dir = os.path.join(base_dir, "Race_Screenshots")

    # Ensure the directory exists
    if not os.path.exists(screenshots_dir):
        print("Error: Race_Screenshots folder does not exist.")
        return

    # Collect all test cases and files
    images = [f for f in os.listdir(screenshots_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    total = len(images)
    passed = 0

    print(f"Running OCR tests on {total} images...\n")

    for img_name in images:
        print("=" * 80)  # Divider line between test cases
        print(f"Processing: {img_name}")

        img_path = os.path.join(screenshots_dir, img_name)
        expected_output = test_cases.get(img_name)

        if expected_output is None:
            print(f"Warning: No test case found for {img_name}. Skipping...")
            continue

        # Process the image
        processed_output = process_image(img_path)

        # Compare output
        if processed_output == expected_output:
            passed += 1
            print(f"{GREEN}Test passed for {img_name}.{RESET}")
        else:
            print(f"{RED}Test failed for {img_name}.{RESET}")
            print(f"Expected: {expected_output}")
            print(f"Got: {processed_output}")

    print("=" * 80)  # Final divider
    print(f"\nTesting complete. {GREEN}Passed {passed}/{total} tests.{RESET}")

if __name__ == "__main__":
    run_tests()
