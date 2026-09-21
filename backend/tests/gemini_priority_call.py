import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

myfile = client.files.upload(
    file=r"C:\Users\root\Downloads\Timetable.csv"
)

tasks = "I need to edit 1hr of gameplay every day for my youtube channel, i dont really have any more stuff to do"

food="30"

sleep="8"

cooking = "9"

freetime = "1"

commutetime = "15"

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=[
        myfile,
        tasks,
        food,
        sleep,
        cooking,
        freetime,
        commutetime,
        "Using the previous information, create a list as a string without special characters of all tasks that need to be completed. Include level of priority, estimated time to complete (You can use the user inputted info when available), level of focus required (deep/casual), ideal time of day to do it, deadline (when relevant), for fixed events such as classes replace ideal time of day and expected time to complete by the start time and end time. The input is as follows: classes calendar file, time spent eating daily (mins), time spent sleeping daily(hrs), times person cooks every week(units, assume 25mins per cook, assign each cook to slots prioritising in this manner:weekday dinners>weekend dinners>weekend lunches>weekday lunches), preferred amount of daily free time(hrs, prioritise other tasks over this), time to commute from home to class"
    ]
)

print(response.text)