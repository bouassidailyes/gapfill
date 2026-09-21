import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

dayStartEnd ="09:00 - 00:00"
schedule = '''Task Name Sleep
Priority High
Estimated Time 8 hours daily
Focus Level Casual
Ideal Time Night
Deadline None

Task Name Eat Meal
Priority High
Estimated Time 30 minutes daily
Focus Level Casual
Ideal Time Morning Midday Evening
Deadline None

Task Name Edit Gameplay Video for YouTube
Priority High
Estimated Time 1 hour 30 minutes daily
Focus Level Deep
Ideal Time Afternoon or Evening
Deadline Daily Upload Schedule

Task Name Free Time relaxation
Priority Low
Estimated Time 1 hour daily
Focus Level Casual
Ideal Time Late Evening
Deadline None

Cooking and Meal Prep Tasks

Task Name Weekday Dinner Cooking
Priority High
Estimated Time 25 minutes per session
Focus Level Casual
Ideal Time Weekday evenings Monday to Friday
Deadline None
Notes Occurs 5 times per week

Task Name Weekend Dinner Cooking
Priority High
Estimated Time 25 minutes per session
Focus Level Casual
Ideal Time Weekend evenings Saturday and Sunday
Deadline None
Notes Occurs 2 times per week

Task Name Weekend Lunch Cooking
Priority High
Estimated Time 25 minutes per session
Focus Level Casual
Ideal Time Midday Saturday and Sunday
Deadline None
Notes Occurs 2 times per week

Commuting Tasks

Task Name Travel to Class
Priority Medium
Estimated Time 15 minutes per trip
Focus Level Casual
Ideal Time Immediately before class start times
Deadline None

Task Name Travel from Class
Priority Medium
Estimated Time 15 minutes per trip
Focus Level Casual
Ideal Time Immediately after class end times
Deadline None

Fixed Class Schedule Tasks Weeks 36 to 41

Task Name Procedural Programming Lecture BCS1120 Monday
Priority High
Start Time 11 00
End Time 13 00
Focus Level Deep
Deadline None
Reoccurrence Monday Weeks 36 to 40

Task Name Procedural Programming Lecture BCS1120 Thursday
Priority High
Start Time 16 00
End Time 18 00
Focus Level Deep
Deadline None
Reoccurrence Thursday Weeks 36 to 41

Task Name Procedural Programming Lecture BCS1120 Wednesday Week 36 only
Priority High
Start Time 11 00
End Time 13 00
Focus Level Deep
Deadline None
Reoccurrence Wednesday Week 36

Task Name Procedural Programming Tutorial BCS1120 Wednesday
Priority High
Start Time 13 30
End Time 15 30
Focus Level Deep
Deadline None
Reoccurrence Wednesday Weeks 37 to 41

Task Name Discrete Mathematics Lecture BCS1130 Monday
Priority High
Start Time 13 30
End Time 15 30
Focus Level Deep
Deadline None
Reoccurrence Monday Weeks 36 to 41

Task Name Discrete Mathematics Lecture BCS1130 Tuesday
Priority High
Start Time 13 30
End Time 15 30
Focus Level Deep
Deadline None
Reoccurrence Tuesday Weeks 36 to 41

Task Name Discrete Mathematics Tutorial BCS1130 Thursday
Priority High
Start Time 13 30
End Time 15 30
Focus Level Deep
Deadline None
Reoccurrence Thursday Weeks 36 to 41

Task Name Introduction to Computer Science Lecture BCS1110 Tuesday
Priority High
Start Time 16 00
End Time 18 00
Focus Level Deep
Deadline None
Reoccurrence Tuesday Weeks 36 37 39 40 41

Task Name Introduction to Computer Science Lecture BCS1110 Tuesday Week 38 only
Priority High
Start Time 08 30
End Time 10 30
Focus Level Deep
Deadline None
Reoccurrence Tuesday Week 38

Task Name Introduction to Computer Science Lecture BCS1110 Wednesday Week 36 only
Priority High
Start Time 08 30
End Time 10 30
Focus Level Deep
Deadline None
Reoccurrence Wednesday Week 36

Task Name Introduction to Computer Science Lecture BCS1110 Wednesday
Priority High
Start Time 11 00
End Time 13 00
Focus Level Deep
Deadline None
Reoccurrence Wednesday Weeks 37 to 41

Task Name Introduction to Computer Science Tutorial BCS1110 Thursday
Priority High
Start Time 11 00
End Time 13 00
Focus Level Deep
Deadline None
Reoccurrence Thursday Weeks 36 to 41

Task Name Project Meeting BCS1300 Friday
Priority High
Start Time 08 30
End Time 18 00
Focus Level Deep
Deadline None
Reoccurrence Friday Weeks 36 to 40

Task Name Project Opening BCS1300 Wednesday Week 41 only
Priority High
Start Time 16 00
End Time 17 00
Focus Level Deep
Deadline None
Reoccurrence Wednesday Week 41

Exam Schedule Tasks Week 42

Task Name Discrete Mathematics Exam BCS1130
Priority Critical
Start Time 12 00
End Time 14 00
Focus Level Deep
Deadline Monday October 12 2026 14 00

Task Name Procedural Programming Exam BCS1120
Priority Critical
Start Time 12 00
End Time 14 00
Focus Level Deep
Deadline Wednesday October 14 2026 14 00

Task Name Introduction to Computer Science Exam BCS1110
Priority Critical
Start Time 09 00
End Time 11 00
Focus Level Deep
Deadline Friday October 16 2026 11 00

University Administration Deadlines

Task Name DACS Course Registration Period 2 Close
Priority High
Estimated Time 10 minutes
Focus Level Casual
Ideal Time Evening before deadline
Deadline Friday September 11 2026 17 00

Task Name DACS Resit Registration BAY2 Y3 Ma P1 Close
Priority High
Estimated Time 10 minutes
Focus Level Casual
Ideal Time Evening before deadline
Deadline Monday November 16 2026 23 59

Task Name DACS Course Registration Period 4 Close
Priority High
Estimated Time 10 minutes
Focus Level Casual
Ideal Time Evening before deadline
Deadline Friday November 27 2026 17 00

Task Name DACS Project Registration Semester 2 Close
Priority High
Estimated Time 10 minutes
Focus Level Casual
Ideal Time Evening before deadline
Deadline Friday November 27 2026 17 00

Task Name DACS Resit Registration BAY1 Semester 1 Close
Priority High
Estimated Time 10 minutes
Focus Level Casual
Ideal Time Evening before deadline
Deadline Tuesday January 12 2027 12 00

Task Name DACS Resit Registration BAY2 Y3 Ma P2 Close
Priority High
Estimated Time 10 minutes
Focus Level Casual
Ideal Time Evening before deadline
Deadline Monday February 8 2027 23 59

Task Name DACS Course Registration Period 5 Close
Priority High
Estimated Time 10 minutes
Focus Level Casual
Ideal Time Evening before deadline
Deadline Friday February 19 2027 17 00

Task Name DACS Resit Registration Masters Period 4 Close
Priority High
Estimated Time 10 minutes
Focus Level Casual
Ideal Time Evening before deadline
Deadline Thursday April 22 2027 23 59

Task Name DACS Resit Registration BA Semester 2 Close
Priority High
Estimated Time 10 minutes
Focus Level Casual
Ideal Time Evening before deadline
Deadline Monday June 7 2027 23 59'''

response = client.models.generate_content(
    model=os.getenv("LLM_MODEL"),
    contents=[
        schedule,
        """Create an iCalendar (.ics) file containing all these tasks. Allocate them taking all factors into account to determine their optimal placement.
The time range is the range where all tasks requiring high focus and free time/relaxation should fit in, they should not be before or after.
Return ONLY the raw iCalendar content.
Do not use Markdown.
Do not put the result inside ``` code fences.
Start with BEGIN:VCALENDAR and end with END:VCALENDAR."""
    ]
)

ics_content = response.text.strip()

with open("schedule.ics", "w", encoding="utf-8") as f:
    f.write(ics_content)

print("Created schedule.ics")