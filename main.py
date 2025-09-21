from models.validation import ReportValidator
from models.classification import ReportRouter

def main():

    image_url = input("Enter the image URL: ")
    description = input("Enter the description of the issue: ")

    validator = ReportValidator(image_url)
    router = ReportRouter("categories.json", "departments.json")

    is_valid = validator.validate(image_url, description)

    if is_valid:
        assigned = router.classify_and_route(description)
        print(assigned)
    
    else:
        print("Complaint is invalid.")

if __name__ == "__main__":
    main()