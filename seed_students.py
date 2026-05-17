"""One-time seed script for sample student records."""

from database import init_database
from crud import add_student, student_id_exists

STUDENTS = [
    (3, "Alice", "Johnson", "Female", "B.Tech", "ECE", "alicej@gmail.com", "9876501234", "Telangana", "Hyderabad", "500001"),
    (4, "Rahul", "Sharma", "Male", "B.Tech", "ME", "rahuls@gmail.com", "9876512345", "Maharashtra", "Pune", "411001"),
    (5, "Priya", "Reddy", "Female", "B.Tech", "CSE", "priyareddy@gmail.com", "9876523456", "Andhra Pradesh", "Vijayawada", "520001"),
    (6, "Arjun", "Mehta", "Male", "B.Tech", "EEE", "arjunm@gmail.com", "9876534567", "Gujarat", "Ahmedabad", "380001"),
    (7, "Sneha", "Iyer", "Female", "B.Tech", "IT", "snehai@gmail.com", "9876545678", "Tamil Nadu", "Chennai", "600001"),
    (8, "Vikram", "Singh", "Male", "B.Tech", "Civil", "vikrams@gmail.com", "9876556789", "Rajasthan", "Jaipur", "302001"),
    (9, "Neha", "Patel", "Female", "B.Tech", "CSE", "nehap@gmail.com", "9876567890", "Gujarat", "Surat", "395003"),
    (10, "Rohan", "Das", "Male", "B.Tech", "ECE", "rohandas@gmail.com", "9876578901", "West Bengal", "Kolkata", "700001"),
    (11, "Kavya", "Nair", "Female", "B.Tech", "IT", "kavyan@gmail.com", "9876589012", "Kerala", "Kochi", "682001"),
    (12, "Aditya", "Verma", "Male", "B.Tech", "CSE", "adityav@gmail.com", "9876590123", "Uttar Pradesh", "Lucknow", "226001"),
    (13, "Pooja", "Yadav", "Female", "B.Tech", "EEE", "poojay@gmail.com", "9876601234", "Haryana", "Gurgaon", "122001"),
    (14, "Karan", "Malhotra", "Male", "B.Tech", "ME", "karanm@gmail.com", "9876612345", "Delhi", "New Delhi", "110001"),
    (15, "Divya", "Rao", "Female", "B.Tech", "CSE", "divyarao@gmail.com", "9876623456", "Karnataka", "Bangalore", "560002"),
    (16, "Sanjay", "Kumar", "Male", "B.Tech", "Civil", "sanjayk@gmail.com", "9876634567", "Bihar", "Patna", "800001"),
    (17, "Meera", "Menon", "Female", "B.Tech", "ECE", "meeram@gmail.com", "9876645678", "Kerala", "Trivandrum", "695001"),
    (18, "Aman", "Gupta", "Male", "B.Tech", "IT", "amangupta@gmail.com", "9876656789", "Punjab", "Amritsar", "143001"),
    (19, "Anjali", "Saxena", "Female", "B.Tech", "CSE", "anjalis@gmail.com", "9876667890", "Madhya Pradesh", "Bhopal", "462001"),
    (20, "Ritesh", "Jain", "Male", "B.Tech", "EEE", "riteshj@gmail.com", "9876678901", "Rajasthan", "Udaipur", "313001"),
    (21, "Nisha", "Chowdary", "Female", "B.Tech", "CSE", "nishac@gmail.com", "9876689012", "Andhra Pradesh", "Guntur", "522001"),
    (22, "Varun", "Shetty", "Male", "B.Tech", "ME", "varuns@gmail.com", "9876690123", "Karnataka", "Mangalore", "575001"),
    (23, "Tanya", "Khanna", "Female", "B.Tech", "IT", "tanyak@gmail.com", "9876701234", "Delhi", "New Delhi", "110002"),
    (24, "Deepak", "Mishra", "Male", "B.Tech", "Civil", "deepakm@gmail.com", "9876712345", "Uttar Pradesh", "Kanpur", "208001"),
    (25, "Reshma", "Pillai", "Female", "B.Tech", "ECE", "reshmap@gmail.com", "9876723456", "Kerala", "Kozhikode", "673001"),
    (26, "Harish", "Raj", "Male", "B.Tech", "CSE", "harishr@gmail.com", "9876734567", "Telangana", "Warangal", "506001"),
    (27, "Swati", "Agarwal", "Female", "B.Tech", "EEE", "swatia@gmail.com", "9876745678", "West Bengal", "Durgapur", "713201"),
    (28, "Nitin", "Bansal", "Male", "B.Tech", "IT", "nitinb@gmail.com", "9876756789", "Punjab", "Ludhiana", "141001"),
    (29, "Lavanya", "Krishnan", "Female", "B.Tech", "CSE", "lavanyak@gmail.com", "9876767890", "Tamil Nadu", "Coimbatore", "641001"),
    (30, "Abhishek", "Roy", "Male", "B.Tech", "ME", "abhishekr@gmail.com", "9876778901", "Jharkhand", "Ranchi", "834001"),
    (31, "Shreya", "Mukherjee", "Female", "B.Tech", "Civil", "shreyam@gmail.com", "9876789012", "West Bengal", "Siliguri", "734001"),
    (32, "Manoj", "Naidu", "Male", "B.Tech", "CSE", "manojn@gmail.com", "9876790123", "Andhra Pradesh", "Tirupati", "517501"),
]


def main() -> None:
    init_database()
    added = skipped = 0
    for row in STUDENTS:
        data = {
            "student_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "gender": row[3],
            "course": row[4],
            "branch": row[5],
            "mail": row[6],
            "contact": row[7],
            "state": row[8],
            "address": row[9],
            "areapincode": row[10],
        }
        if student_id_exists(row[0]):
            skipped += 1
            continue
        add_student(data)
        added += 1
    print(f"Done: {added} inserted, {skipped} skipped (already exist).")


if __name__ == "__main__":
    main()
