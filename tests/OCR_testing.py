import os
from OCR_test_cases import test_cases
from OCR_testing_helper import process_image

# ANSI escape codes for colors
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

def run_tests(min_num=None, max_num=None, analyzeAllRaces=False):
    """
    Run OCR tests on a specified range of images or all images.

    Args:
        min_num (int): Minimum number in the range (e.g., 1 for "race1").
        max_num (int): Maximum number in the range (e.g., 22 for "race22").
        analyzeAllRaces (bool): Whether to ignore range input and analyze all images.
    """
    # Base path for race screenshots
    base_dir = os.path.dirname(__file__)
    screenshots_dir = os.path.join(base_dir, "Race_Screenshots")

    # Ensure the directory exists
    if not os.path.exists(screenshots_dir):
        print(f"{RED}Error: Race_Screenshots folder does not exist.{RESET}")
        return

    # Collect image files based on analyzeAllRaces or range
    if analyzeAllRaces:
        image_list = [f for f in os.listdir(screenshots_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    elif min_num is not None and max_num is not None:
        image_list = [f"race{i}.png" for i in range(min_num, max_num + 1) if os.path.exists(os.path.join(screenshots_dir, f"race{i}.png"))]
    else:
        print(f"{RED}Error: Provide either a valid range or set analyzeAllRaces=True.{RESET}")
        return

    total = len(image_list)
    passed = 0
    skipped = 0
    failed = 0

    print(f"\nRunning OCR tests on {total} images...\n")

    for img_name in image_list:
        print("=" * 80)  # Divider line between test cases
        print(f"Processing: {img_name}")

        img_path = os.path.join(screenshots_dir, img_name)
        expected_output = test_cases.get(img_name)

        if expected_output is None:
            print(f"{RED}Warning: No test case found for {img_name}. Skipping...{RESET}")
            skipped += 1
            continue

        # Process the image
        processed_output = process_image(img_path)

        # Compare output
        if processed_output == expected_output:
            passed += 1
            print(f"{GREEN}Test passed for {img_name}.{RESET}")
        else:
            failed += 1
            print(f"{RED}Test failed for {img_name}.{RESET}")
            print(f"{RED}Expected: {expected_output}{RESET}")
            print(f"{RED}Got: {processed_output}{RESET}")

    print("=" * 80)  # Final divider

    # Summary
    print(f"\n{GREEN}Testing complete on {total} images.{RESET}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    print(f"{RED}Skipped: {skipped}{RESET}")

if __name__ == "__main__":
    # Example: Test specific range
    run_tests(min_num=25, max_num=28, analyzeAllRaces=False)

    # Example: Test all images
    # run_tests(analyzeAllRaces=True)
