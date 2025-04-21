import discord
from discord.ext import tasks, commands
import asyncio
import random
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # To access member details

import discord
from discord.ext import commands
import mysql.connector

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@jayasri15D",
    database="discord_bot"
)

cursor = db.cursor()

# Create Bot
bot = commands.Bot(command_prefix="!", intents=intents)
# Command to Register Users
@bot.command()
async def register(ctx, username: str, role: str, department: str):
    user_id = ctx.author.id
    sql = "INSERT INTO Users (user_id, username, role, department, join_date) VALUES (%s, %s, %s, %s, CURDATE())"
    values = (user_id, username, role, department)
    cursor.execute(sql, values)
    db.commit()
    await ctx.send(f"User {username} registered successfully!")

# Command to Check Attendance
@bot.command()
async def checkin(ctx):
    user_id = ctx.author.id
    sql = "INSERT INTO Attendance (user_id, check_in) VALUES (%s, NOW())"
    cursor.execute(sql, (user_id,))
    db.commit()
    await ctx.send(f"{ctx.author.name}, you have successfully checked in!")
# ==========================
# Task Management & Reminders
# ==========================
assigned_tasks = { 1163126807084671016: ["Complete the monthly report", "Prepare slides for the meeting","Ready for your prsentation"]}
# Dictionary to store tasks per employee

@bot.command()
async def assign_task(ctx, employee: discord.Member, *, task):
    """ Assign a task to an employee and store it. """
    if employee.id not in assigned_tasks:
        assigned_tasks[employee.id] = []
    assigned_tasks[employee.id].append(task)
    await ctx.send(f"✅ Task assigned to {employee.mention}: {task}")

@bot.command()
async def my_tasks(ctx):
    """ Employees can check their assigned tasks. """
    employee_id = ctx.author.id
    if employee_id in assigned_tasks and assigned_tasks[employee_id]:
        tasks = "\n".join([f"- {task}" for task in assigned_tasks[employee_id]])
        await ctx.send(f"📝 **Your Tasks:**\n{tasks}")
    else:
        await ctx.send("✅ You have no assigned tasks!")

@bot.command()
async def complete_task(ctx, *, task):
    """ Mark a task as completed. """
    await ctx.send(f"✅ Task '{task}' has been marked as completed!")

async def task_reminder(channel, task, reminder_time):
    delay = (reminder_time - datetime.now()).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)
    await channel.send(f"⏳ Reminder: {task}")

@bot.command()
async def set_reminder(ctx, task, hours: int, minutes: int):
    reminder_time = datetime.now() + timedelta(hours=hours, minutes=minutes)
    await ctx.send(f"🔔 Reminder for '{task}' set for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.create_task(task_reminder(ctx.channel, task, reminder_time))

# ==========================
# Meetings & Communication
# ==========================
@bot.command()
async def schedule_meeting(ctx, time: str, *, details):
    await ctx.send(f"📅 Meeting scheduled at {time}: {details}")

@bot.command()
async def contact_manager(ctx):
    manager_id = 1324648611295924255 # Replace with actual manager ID
    manager = ctx.guild.get_member(manager_id)
    if manager:
        await ctx.send(f"📞 You can contact your manager {manager.mention}.")
    else:
        await ctx.send("⚠️ Manager contact not available.")

# ==========================
# Motivational Messages & Greetings
# ==========================
motivational_quotes = [
    "Believe in yourself and all that you are! 🚀",
    "Every day is a fresh start! 🌟",
    "Success is not final, failure is not fatal! 💪"
]

greetings = ["hi", "hello", "hey", "good morning", "good evening"]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if any(greet in message.content.lower() for greet in greetings):
        await message.channel.send(f"Hello {message.author.mention}! Hope you're having a great day! 🌟")
    await bot.process_commands(message)

@tasks.loop(hours=4)
async def send_motivational_quote():
    channel_id = 1324648611295924255 
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(f"💡 Motivation: {random.choice(motivational_quotes)}")

# ==========================
# Work Anniversary & Birthday Wishes
# ==========================
work_anniversaries = {"User1": "2020-02-20", "User2": "2021-05-14"}  # Example data
birthdays = {"User1": "1995-06-10", "User2": "1998-09-23"}

@tasks.loop(hours=24)
async def send_special_messages():
    today = datetime.now().strftime('%m-%d')
    channel_id = 1324648611295924255
    channel = bot.get_channel(channel_id)
    if channel:
        for user, date in work_anniversaries.items():
            if date[5:] == today:
                await channel.send(f"🎉 Congratulations {user} on your work anniversary! 🎊")
        for user, date in birthdays.items():
            if date[5:] == today:
                await channel.send(f"🎂 Happy Birthday {user}! 🥳")

# ==========================
# Polls & Employee Feedback
# ==========================
@bot.command()
async def poll(ctx, question: str, *options: str):
    if len(options) < 2:
        await ctx.send("❌ Please provide at least two options for the poll.")
        return
    poll_embed = discord.Embed(title=question, color=discord.Color.blue())
    reactions = ['🇦', '🇧', '🇨', '🇩', '🇪'][:len(options)]
    for emoji, option in zip(reactions, options):
        poll_embed.add_field(name=f"{emoji} {option}", value="​", inline=False)
    msg = await ctx.send(embed=poll_embed)
    for emoji in reactions:
        await msg.add_reaction(emoji)

@bot.command()
async def anonymous_feedback(ctx, *, feedback):
    feedback_channel_id = 123456789012345678  # Replace with actual feedback channel ID
    feedback_channel = bot.get_channel(feedback_channel_id)
    if feedback_channel:
        await feedback_channel.send(f"📩 Anonymous Feedback: {feedback}")
    await ctx.send("✅ Your feedback has been submitted anonymously!")

# ==========================
# Logging & Error Handling
# ==========================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing required arguments! Use `!help` to see command usage.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Invalid command! Use `!help` for available commands.")
    else:
        await ctx.send("❌ An unexpected error occurred.")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}!")
    send_motivational_quote.start()
    send_special_messages.start()

# ==========================
# Attendance Tracking
# ==========================
attendance = {}

@bot.command()
async def check_in(ctx):
    user = ctx.author
    attendance[user.id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await ctx.send(f"✅ {user.mention} checked in at {attendance[user.id]}.")

@bot.command()
async def check_out(ctx):
    user = ctx.author
    if user.id in attendance:
        check_in_time = datetime.strptime(attendance[user.id], "%Y-%m-%d %H:%M:%S")
        check_out_time = datetime.now()
        duration = check_out_time - check_in_time
        await ctx.send(f"✅ {user.mention} checked out at {check_out_time.strftime('%H:%M:%S')}. Worked for {duration}.")
        del attendance[user.id]
    else:
        await ctx.send("⚠️ You haven't checked in yet!")

# ==========================
# Leave Request System
# ==========================
leave_requests = {}

@bot.command()
async def request_leave(ctx, days: int, *, reason):
    user = ctx.author
    leave_requests[user.id] = {"days": days, "reason": reason, "status": "Pending"}
    await ctx.send(f"📌 {user.mention} requested {days} days of leave for: {reason}. Waiting for approval.")

@bot.command()
async def approve_leave(ctx, employee: discord.Member):
    if employee.id in leave_requests:
        leave_requests[employee.id]["status"] = "Approved"
        await ctx.send(f"✅ Leave approved for {employee.mention}.")
    else:
        await ctx.send("⚠️ No leave request found for this employee.")

@bot.command()
async def leave_status(ctx):
    user = ctx.author
    if user.id in leave_requests:
        status = leave_requests[user.id]["status"]
        await ctx.send(f"📌 Your leave request status: {status}.")
    else:
        await ctx.send("⚠️ No leave request found.")

# ==========================
# Performance Evaluation
# ==========================
performance_ratings = {}

@bot.command()
async def rate_employee(ctx, employee: discord.Member, rating: int):
    if 1 <= rating <= 10:
        performance_ratings[employee.id] = rating
        await ctx.send(f"⭐ {employee.mention} has been rated {rating}/10.")
    else:
        await ctx.send("⚠️ Please provide a rating between 1 and 10.")

@bot.command()
async def check_rating(ctx, employee: discord.Member):
    if employee.id in performance_ratings:
        await ctx.send(f"⭐ {employee.mention} has a performance rating of {performance_ratings[employee.id]}/10.")
    else:
        await ctx.send("⚠️ No rating found for this employee.")

# ==========================
# Project Progress Tracking
# ==========================
project_status = {}

@bot.command()
async def update_project(ctx, project_name: str, *, status):
    project_status[project_name] = status
    await ctx.send(f"📌 Project '{project_name}' status updated to: {status}")

@bot.command()
async def check_project(ctx, project_name: str):
    if project_name in project_status:
        await ctx.send(f"📌 Project '{project_name}' is currently: {project_status[project_name]}")
    else:
        await ctx.send("⚠️ No updates found for this project.")

# ==========================
# Call Functionality (Voice Channels)
# ==========================
@bot.command()
async def call_manager(ctx):
    manager_id = 1343100285807099976 # Replace with the actual manager's Discord ID
    manager = ctx.guild.get_member(manager_id)
    if manager:
        voice_channel = await ctx.author.guild.create_voice_channel(f"Call-{ctx.author.name}")
        await ctx.author.move_to(voice_channel)
        await manager.move_to(voice_channel)
        await ctx.send(f"📞 {ctx.author.mention} is calling {manager.mention}. Join the voice channel!")
    else:
        await ctx.send("⚠️ Manager is not available.")

# ==========================
# Google Meet Integration
# ==========================
@bot.command()
async def meet_link(ctx):
    meet_url = f"https://meet.google.com/{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))}"
    await ctx.send(f"📅 Google Meet Link: {meet_url}")

# ==========================
# AI-Based Auto Replies (FAQ)
# ==========================
auto_replies = {
    "salary day": "Salary is processed on the 1st of every month.",
    "holiday list": "You can check the holiday list in the company portal.",
    "leave policy": "Each employee gets 20 paid leaves per year.",
    "manager contact": "Use `!contact_manager` to reach your manager.",
}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for keyword, reply in auto_replies.items():
        if keyword in message.content.lower():
            await message.channel.send(reply)
            return

    await bot.process_commands(message)

# ==========================
# Fun Features (Jokes & Fun Facts)
# ==========================
jokes = [
    "Why did the programmer quit his job? Because he didn't get arrays! 😂",
    "Why do Java developers wear glasses? Because they don’t C#! 🤓",
]

fun_facts = [
    "Did you know? Python was named after 'Monty Python’s Flying Circus'!",
    "The first programmer in history was Ada Lovelace, back in the 1800s!",
]

@bot.command()
async def joke(ctx):
    await ctx.send(random.choice(jokes))

@bot.command()
async def fun_fact(ctx):
    await ctx.send(random.choice(fun_facts))

# ==========================
# Logging & Error Handling
# ==========================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
         await ctx.send(f"⚠️ Missing required argument: {error.param}. Use `!help {ctx.command}` for usage details.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Invalid command! Use `!help` for available commands.")
    else:
        await ctx.send(f"❌ An unexpected error occurred: {error}")
        raise error

bot.run("MTMyNDYyOTc4Nzc5MjM3NTgwOA.Gx4G1b.1ijZUV_2n6PeIgEQcfXUgbAhTIn31DqXX3dpow")  
