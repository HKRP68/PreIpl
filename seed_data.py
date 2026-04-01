"""Seed the database with IPL 2026 schedule and squads."""
from database import init_db, get_or_create_team, add_player, add_match

TEAMS = {
    "Chennai Super Kings": "CSK",
    "Delhi Capitals": "DC",
    "Gujarat Titans": "GT",
    "Kolkata Knight Riders": "KKR",
    "Lucknow Super Giants": "LSG",
    "Mumbai Indians": "MI",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Royal Challengers Bengaluru": "RCB",
    "Sunrisers Hyderabad": "SRH",
}

SQUADS = {
    "Chennai Super Kings": {
        "Batter": ["Ruturaj Gaikwad", "MS Dhoni", "Sanju Samson", "Dewald Brevis", "Ayush Mhatre", "Kartik Sharma", "Sarfaraz Khan", "Urvil Patel"],
        "All-Rounder": ["Jamie Overton", "Ramakrishna Ghosh", "Prashant Veer", "Matthew Short", "Aman Khan", "Zak Foulkes", "Shivam Dube"],
        "Bowler": ["Khaleel Ahmed", "Noor Ahmad", "Anshul Kamboj", "Mukesh Choudhary", "Shreyas Gopal", "Gurjapneet Singh", "Akeal Hosein", "Matt Henry", "Rahul Chahar", "Spencer Johnson"],
    },
    "Delhi Capitals": {
        "Batter": ["KL Rahul", "Karun Nair", "David Miller", "Pathum Nissanka", "Sahil Parakh", "Prithvi Shaw", "Abishek Porel", "Tristan Stubbs"],
        "All-Rounder": ["Axar Patel", "Sameer Rizvi", "Ashutosh Sharma", "Vipraj Nigam", "Ajay Mandal", "Tripurana Vijay", "Madhav Tiwari", "Nitish Rana"],
        "Bowler": ["Mitchell Starc", "T. Natarajan", "Mukesh Kumar", "Dushmantha Chameera", "Auqib Nabi", "Lungisani Ngidi", "Kyle Jamieson", "Kuldeep Yadav"],
    },
    "Gujarat Titans": {
        "Batter": ["Shubman Gill", "Jos Buttler", "Kumar Kushagra", "Anuj Rawat", "Tom Banton", "Glenn Phillips", "Sai Sudharsan"],
        "All-Rounder": ["Nishant Sindhu", "Washington Sundar", "Mohd. Arshad Khan", "Sai Kishore", "Jayant Yadav", "Jason Holder", "Rahul Tewatia", "Shahrukh Khan"],
        "Bowler": ["Kagiso Rabada", "Mohammed Siraj", "Prasidh Krishna", "Manav Suthar", "Gurnoor Singh Brar", "Ishant Sharma", "Ashok Sharma", "Luke Wood", "Kulwant Khejroliya", "Rashid Khan"],
    },
    "Kolkata Knight Riders": {
        "Batter": ["Ajinkya Rahane", "Rinku Singh", "Angkrish Raghuvanshi", "Manish Pandey", "Finn Allen", "Tejasvi Singh", "Rahul Tripathi", "Tim Seifert", "Rovman Powell"],
        "All-Rounder": ["Anukul Roy", "Cameron Green", "Sarthak Ranjan", "Daksh Kamra", "Rachin Ravindra", "Ramandeep Singh", "Sunil Narine"],
        "Bowler": ["Blessing Muzarabani", "Vaibhav Arora", "Matheesha Pathirana", "Kartik Tyagi", "Prashant Solanki", "Saurabh Dubey", "Navdeep Saini", "Umran Malik", "Varun Chakaravarthy"],
    },
    "Lucknow Super Giants": {
        "Batter": ["Rishabh Pant", "Aiden Markram", "Himmat Singh", "Matthew Breetzke", "Mukul Choudhary", "Akshat Raghuwanshi", "Josh Inglis", "Nicholas Pooran"],
        "All-Rounder": ["Mitchell Marsh", "Abdul Samad", "Shahbaz Ahamad", "Arshin Kulkarni", "Wanindu Hasaranga", "Ayush Badoni"],
        "Bowler": ["Mohammad Shami", "Avesh Khan", "M. Siddharth", "Digvesh Singh", "Akash Singh", "Prince Yadav", "Arjun Tendulkar", "Anrich Nortje", "Naman Tiwari", "Mayank Yadav", "Mohsin Khan"],
    },
    "Mumbai Indians": {
        "Batter": ["Rohit Sharma", "Suryakumar Yadav", "Robin Minz", "Sherfane Rutherford", "Ryan Rickelton", "Quinton de Kock", "Danish Malewar", "N. Tilak Varma"],
        "All-Rounder": ["Hardik Pandya", "Naman Dhir", "Mitchell Santner", "Raj Angad Bawa", "Atharva Ankolekar", "Mayank Rawat", "Corbin Bosch", "Will Jacks", "Shardul Thakur"],
        "Bowler": ["Trent Boult", "Mayank Markande", "Deepak Chahar", "Ashwani Kumar", "Raghu Sharma", "Mohammad Izhar", "Allah Ghazanfar", "Jasprit Bumrah"],
    },
    "Punjab Kings": {
        "Batter": ["Shreyas Iyer", "Nehal Wadhera", "Vishnu Vinod", "Harnoor Pannu", "Pyla Avinash", "Prabhsimran Singh", "Shashank Singh"],
        "All-Rounder": ["Marcus Stoinis", "Harprett Brar", "Marco Jansen", "Azmatullah Omarzai", "Priyansh Arya", "Musheer Khan", "Suryansh Shedge", "Mitch Owen", "Cooper Connolly", "Ben Dwarshuis"],
        "Bowler": ["Arshdeep Singh", "Yuzvendra Chahal", "Vyshak Vijaykumar", "Yash Thakur", "Xavier Bartlett", "Pravin Dubey", "Vishal Nishad", "Lockie Ferguson"],
    },
    "Rajasthan Royals": {
        "Batter": ["Shubham Dubey", "Vaibhav Suryavanshi", "Donovan Ferreira", "Lhuan-Dre Pretorious", "Ravi Singh", "Aman Rao Perala", "Shimron Hetmyer", "Yashasvi Jaiswal", "Dhruv Jurel"],
        "All-Rounder": ["Riyan Parag", "Yudhvir Singh Charak", "Ravindra Jadeja", "Dasun Shanaka"],
        "Bowler": ["Jofra Archer", "Tushar Deshpande", "Kwena Maphaka", "Ravi Bishnoi", "Sushant Mishra", "Yash Raj Punja", "Vignesh Puthur", "Brijesh Sharma", "Adam Milne", "Kuldeep Sen", "Sandeep Sharma", "Nandre Burger"],
    },
    "Royal Challengers Bengaluru": {
        "Batter": ["Rajat Patidar", "Devdutt Padikkal", "Virat Kohli", "Phil Salt", "Jitesh Sharma", "Jordan Cox"],
        "All-Rounder": ["Krunal Pandya", "Swapnil Singh", "Tim David", "Romario Shepherd", "Jacob Bethell", "Venkatesh Iyer", "Satvik Deswal", "Mangesh Yadav", "Vicky Ostwal", "Vihaan Malhotra", "Kanishk Chouhan"],
        "Bowler": ["Josh Hazlewood", "Rasikh Dar", "Suyash Sharma", "Bhuvneshwar Kumar", "Nuwan Thushara", "Abinandan Singh", "Jacob Duffy", "Yash Dayal"],
    },
    "Sunrisers Hyderabad": {
        "Batter": ["Ishan Kishan", "Aniket Verma", "Smaran Ravichandran", "Salil Arora", "Heinrich Klaasen", "Travis Head"],
        "All-Rounder": ["Harshal Patel", "Kamindu Mendis", "Harsh Dubey", "Brydon Carse", "Shivang Kumar", "Krains Fuletra", "Liam Livingstone", "David Payne", "Abhishek Sharma", "Nitish Kumar Reddy"],
        "Bowler": ["Pat Cummins", "Zeeshan Ansari", "Jaydev Unadkat", "Eshan Malinga", "Sakib Hussain", "Onkar Tarmale", "Amit Kumar", "Praful Hinge", "Shivam Mavi"],
    },
}

# Match schedule: (number, date, time, home, away, venue)
MATCHES = [
    (1, "2026-03-28", "19:30", "Sunrisers Hyderabad", "Royal Challengers Bengaluru", "Bengaluru"),
    (2, "2026-03-29", "19:30", "Kolkata Knight Riders", "Mumbai Indians", "Mumbai"),
    (3, "2026-03-30", "19:30", "Chennai Super Kings", "Rajasthan Royals", "Guwahati"),
    (4, "2026-03-31", "19:30", "Gujarat Titans", "Punjab Kings", "New Chandigarh"),
    (5, "2026-04-01", "19:30", "Delhi Capitals", "Lucknow Super Giants", "Lucknow"),
    (6, "2026-04-02", "19:30", "Sunrisers Hyderabad", "Kolkata Knight Riders", "Kolkata"),
    (7, "2026-04-03", "19:30", "Punjab Kings", "Chennai Super Kings", "Chennai"),
    (8, "2026-04-04", "15:30", "Mumbai Indians", "Delhi Capitals", "Delhi"),
    (9, "2026-04-04", "19:30", "Rajasthan Royals", "Gujarat Titans", "Ahmedabad"),
    (10, "2026-04-05", "15:30", "Lucknow Super Giants", "Sunrisers Hyderabad", "Hyderabad"),
    (11, "2026-04-05", "19:30", "Chennai Super Kings", "Royal Challengers Bengaluru", "Bengaluru"),
    (12, "2026-04-06", "19:30", "Punjab Kings", "Kolkata Knight Riders", "Kolkata"),
    (13, "2026-04-07", "19:30", "Mumbai Indians", "Rajasthan Royals", "Guwahati"),
    (14, "2026-04-08", "19:30", "Gujarat Titans", "Delhi Capitals", "Delhi"),
    (15, "2026-04-09", "19:30", "Lucknow Super Giants", "Kolkata Knight Riders", "Kolkata"),
    (16, "2026-04-10", "19:30", "Royal Challengers Bengaluru", "Rajasthan Royals", "Guwahati"),
    (17, "2026-04-11", "15:30", "Sunrisers Hyderabad", "Punjab Kings", "New Chandigarh"),
    (18, "2026-04-11", "19:30", "Delhi Capitals", "Chennai Super Kings", "Chennai"),
    (19, "2026-04-12", "15:30", "Gujarat Titans", "Lucknow Super Giants", "Lucknow"),
    (20, "2026-04-12", "19:30", "Royal Challengers Bengaluru", "Mumbai Indians", "Mumbai"),
    (21, "2026-04-13", "19:30", "Rajasthan Royals", "Sunrisers Hyderabad", "Hyderabad"),
    (22, "2026-04-14", "19:30", "Kolkata Knight Riders", "Chennai Super Kings", "Chennai"),
    (23, "2026-04-15", "19:30", "Lucknow Super Giants", "Royal Challengers Bengaluru", "Bengaluru"),
    (24, "2026-04-16", "19:30", "Punjab Kings", "Mumbai Indians", "Mumbai"),
    (25, "2026-04-17", "19:30", "Kolkata Knight Riders", "Gujarat Titans", "Ahmedabad"),
    (26, "2026-04-18", "15:30", "Delhi Capitals", "Royal Challengers Bengaluru", "Bengaluru"),
    (27, "2026-04-18", "19:30", "Chennai Super Kings", "Sunrisers Hyderabad", "Hyderabad"),
    (28, "2026-04-19", "15:30", "Rajasthan Royals", "Kolkata Knight Riders", "Kolkata"),
    (29, "2026-04-19", "19:30", "Lucknow Super Giants", "Punjab Kings", "New Chandigarh"),
    (30, "2026-04-20", "19:30", "Mumbai Indians", "Gujarat Titans", "Ahmedabad"),
    (31, "2026-04-21", "19:30", "Delhi Capitals", "Sunrisers Hyderabad", "Hyderabad"),
    (32, "2026-04-22", "19:30", "Rajasthan Royals", "Lucknow Super Giants", "Lucknow"),
    (33, "2026-04-23", "19:30", "Chennai Super Kings", "Mumbai Indians", "Mumbai"),
    (34, "2026-04-24", "19:30", "Gujarat Titans", "Royal Challengers Bengaluru", "Bengaluru"),
    (35, "2026-04-25", "15:30", "Punjab Kings", "Delhi Capitals", "Delhi"),
    (36, "2026-04-25", "19:30", "Sunrisers Hyderabad", "Rajasthan Royals", "Jaipur"),
    (37, "2026-04-26", "15:30", "Chennai Super Kings", "Gujarat Titans", "Ahmedabad"),
    (38, "2026-04-26", "19:30", "Kolkata Knight Riders", "Lucknow Super Giants", "Lucknow"),
    (39, "2026-04-27", "19:30", "Royal Challengers Bengaluru", "Delhi Capitals", "Delhi"),
    (40, "2026-04-28", "19:30", "Rajasthan Royals", "Punjab Kings", "New Chandigarh"),
    (41, "2026-04-29", "19:30", "Sunrisers Hyderabad", "Mumbai Indians", "Mumbai"),
    (42, "2026-04-30", "19:30", "Royal Challengers Bengaluru", "Gujarat Titans", "Ahmedabad"),
    (43, "2026-05-01", "19:30", "Delhi Capitals", "Rajasthan Royals", "Jaipur"),
    (44, "2026-05-02", "19:30", "Mumbai Indians", "Chennai Super Kings", "Chennai"),
    (45, "2026-05-03", "15:30", "Kolkata Knight Riders", "Sunrisers Hyderabad", "Hyderabad"),
    (46, "2026-05-03", "19:30", "Punjab Kings", "Gujarat Titans", "Ahmedabad"),
    (47, "2026-05-04", "19:30", "Lucknow Super Giants", "Mumbai Indians", "Mumbai"),
    (48, "2026-05-05", "19:30", "Chennai Super Kings", "Delhi Capitals", "Delhi"),
    (49, "2026-05-06", "19:30", "Punjab Kings", "Sunrisers Hyderabad", "Hyderabad"),
    (50, "2026-05-07", "19:30", "Royal Challengers Bengaluru", "Lucknow Super Giants", "Lucknow"),
    (51, "2026-05-08", "19:30", "Kolkata Knight Riders", "Delhi Capitals", "Delhi"),
    (52, "2026-05-09", "19:30", "Gujarat Titans", "Rajasthan Royals", "Jaipur"),
    (53, "2026-05-10", "15:30", "Lucknow Super Giants", "Chennai Super Kings", "Chennai"),
    (54, "2026-05-10", "19:30", "Mumbai Indians", "Royal Challengers Bengaluru", "Raipur"),
    (55, "2026-05-11", "19:30", "Delhi Capitals", "Punjab Kings", "Dharamshala"),
    (56, "2026-05-12", "19:30", "Sunrisers Hyderabad", "Gujarat Titans", "Ahmedabad"),
    (57, "2026-05-13", "19:30", "Kolkata Knight Riders", "Royal Challengers Bengaluru", "Raipur"),
    (58, "2026-05-14", "19:30", "Mumbai Indians", "Punjab Kings", "Dharamshala"),
    (59, "2026-05-15", "19:30", "Chennai Super Kings", "Lucknow Super Giants", "Lucknow"),
    (60, "2026-05-16", "19:30", "Gujarat Titans", "Kolkata Knight Riders", "Kolkata"),
    (61, "2026-05-17", "15:30", "Royal Challengers Bengaluru", "Punjab Kings", "Dharamshala"),
    (62, "2026-05-17", "19:30", "Rajasthan Royals", "Delhi Capitals", "Delhi"),
    (63, "2026-05-18", "19:30", "Sunrisers Hyderabad", "Chennai Super Kings", "Chennai"),
    (64, "2026-05-19", "19:30", "Lucknow Super Giants", "Rajasthan Royals", "Jaipur"),
    (65, "2026-05-20", "19:30", "Mumbai Indians", "Kolkata Knight Riders", "Kolkata"),
    (66, "2026-05-21", "19:30", "Gujarat Titans", "Chennai Super Kings", "Chennai"),
    (67, "2026-05-22", "19:30", "Royal Challengers Bengaluru", "Sunrisers Hyderabad", "Hyderabad"),
    (68, "2026-05-23", "19:30", "Punjab Kings", "Lucknow Super Giants", "Lucknow"),
    (69, "2026-05-24", "15:30", "Rajasthan Royals", "Mumbai Indians", "Mumbai"),
    (70, "2026-05-24", "19:30", "Delhi Capitals", "Kolkata Knight Riders", "Kolkata"),
]


def seed():
    print("Initializing database...")
    init_db()

    print("Adding teams...")
    team_ids = {}
    for name, short in TEAMS.items():
        team_ids[name] = get_or_create_team(name, short)
        print(f"  {short}: id={team_ids[name]}")

    print("Adding players...")
    for team_name, roles in SQUADS.items():
        tid = team_ids[team_name]
        for role, players in roles.items():
            for p in players:
                add_player(p, tid, role)
        print(f"  {TEAMS[team_name]}: {sum(len(v) for v in roles.values())} players")

    print("Adding matches...")
    for m in MATCHES:
        num, date, time, home, away, venue = m
        add_match(num, date, time, team_ids[home], team_ids[away], venue)
    print(f"  {len(MATCHES)} matches added")

    print("\nDatabase seeded successfully!")


if __name__ == "__main__":
    seed()
