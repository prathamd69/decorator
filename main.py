from models.validation import ReportValidator
from models.classification import ReportRouter

def main():
    """
    Main function to validate and classify a civic issue report.
    - Prompts user for image URL and description.
    - Validates if the image and description are semantically similar.
    - If valid, classifies and routes the report to the appropriate department.
    """

    # Prompt user for image URL and issue description
    # Later this will fetch data from database

    print("\n")
    print("\n")
    print("\n")
    print("*"*120)
    print("-"*120)
    print("\n")
    print("\n")
    print("Enter the details of the issue:")
    image_url = input("Enter the image URL: ")
    description = input("Enter the description of the issue: ")

    # Initialize the validator and router
    validator = ReportValidator(image_url)
    router = ReportRouter("categories.json", "departments.json")

    # Validate the report (image and description similarity)
    print("\n")
    print("\n")
    print("\n")
    print("-"*120)
    is_valid = validator.validate(image_url, description)

    if is_valid:
        # If valid, classify and route the report
        print("\n")
        print("\n")
        print("\n")
        print("-"*120)
        assigned = router.classify_and_route(description)
        print(assigned)
    else:
        # If invalid, notify the user
        print("Complaint is invalid.")

if __name__ == "__main__":
    main()