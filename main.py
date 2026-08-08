import os
import logging
import datetime
import random
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    logging.error("TELEGRAM_BOT_TOKEN environment variable not set!")
    exit(1)

bot = TeleBot(BOT_TOKEN)

# Simple in-memory storage (for production, use a database)
user_data = {}  # user_id: {"points": 0, "last_visit": None, "streak": 0, "total_visits": 0}

# Daily tips database
DAILY_TIPS = [
    {
        "title": "🎯 Practice Consistently",
        "tip": "Short daily practice sessions are more effective than long irregular ones. Aim for 15-30 minutes daily."
    },
    {
        "title": "📚 Learn from Pros",
        "tip": "Watch professional players and analyze their decision-making, positioning, and strategies."
    },
    {
        "title": "💪 Master Fundamentals",
        "tip": "Strong fundamentals beat fancy tricks. Focus on basics until they become second nature."
    },
    {
        "title": "🧠 Review Your Gameplay",
        "tip": "Record and review your matches to identify mistakes and areas for improvement."
    },
    {
        "title": "🎮 Optimize Settings",
        "tip": "Fine-tune your sensitivity, graphics, and controls for optimal performance."
    },
    {
        "title": "💧 Stay Hydrated",
        "tip": "Drink water regularly during gaming sessions to maintain focus and reaction time."
    },
    {
        "title": "🔄 Take Smart Breaks",
        "tip": "Take 5-10 minute breaks every hour to rest your eyes and maintain mental sharpness."
    },
    {
        "title": "👥 Join Gaming Communities",
        "tip": "Connect with other players to share strategies, tips, and learn together."
    },
    {
        "title": "📝 Set Clear Goals",
        "tip": "Set specific, measurable goals for each session to track your progress."
    },
    {
        "title": "⚡ Warm Up Properly",
        "tip": "Start each session with a warm-up routine to get your reflexes ready."
    },
    {
        "title": "🎯 Focus on One Skill",
        "tip": "Work on one specific skill at a time for faster and more effective improvement."
    },
    {
        "title": "🧘 Stay Calm Under Pressure",
        "tip": "Maintain composure during intense moments. Emotional control leads to better decisions."
    },
    {
        "title": "📊 Track Your Progress",
        "tip": "Monitor your stats to identify strengths, weaknesses, and measure improvement."
    },
    {
        "title": "🎵 Find Your Focus Music",
        "tip": "Background music or ambient sounds can help maintain concentration during gameplay."
    },
    {
        "title": "💪 Exercise for Better Gaming",
        "tip": "Regular physical exercise improves reaction time, focus, and overall gaming performance."
    },
    {
        "title": "🗺️ Study Game Maps",
        "tip": "Learn map layouts, spawn points, and strategic positions to gain advantage."
    },
    {
        "title": "🎯 Crosshair Placement",
        "tip": "Keep your crosshair at head level and where enemies are likely to appear."
    },
    {
        "tip": "Communication is key. Use clear, concise callouts to coordinate with teammates effectively."
    },
    {
        "title": "⚡ Adapt Your Strategy",
        "tip": "Be flexible and adapt your playstyle based on your opponent's tactics."
    },
    {
        "title": "🎮 Play with Purpose",
        "tip": "Every session should have a specific goal. Play with intention, not just for fun."
    }
]

# Streak multipliers
STREAK_MULTIPLIERS = {
    0: 1.0, 1: 1.0, 2: 1.1, 3: 1.2, 4: 1.3,
    5: 1.5, 7: 2.0, 10: 2.5, 15: 3.0, 30: 5.0
}

# Gaming categories
CATEGORIES = {
    "strategy": {
        "emoji": "🧠",
        "name": "Strategy",
        "tips": [
            "Plan your moves several steps ahead",
            "Anticipate your opponent's strategy",
            "Positioning often beats pure skill",
            "Learn from every defeat"
        ]
    },
    "aim": {
        "emoji": "🎯",
        "name": "Aim Training",
        "tips": [
            "Practice aiming 10-15 minutes daily",
            "Use aim trainers to improve accuracy",
            "Find your perfect sensitivity",
            "Focus on crosshair placement"
        ]
    },
    "mental": {
        "emoji": "🧘",
        "name": "Mental Game",
        "tips": [
            "Stay positive even when losing",
            "Take deep breaths during intense moments",
            "Avoid blaming teammates",
            "Learn from every mistake"
        ]
    },
    "settings": {
        "emoji": "⚙️",
        "name": "Settings",
        "tips": [
            "Optimize graphics for smooth performance",
            "Find your ideal sensitivity",
            "Customize keybindings for comfort",
            "Use quality peripherals"
        ]
    },
    "teamwork": {
        "emoji": "🤝",
        "name": "Teamwork",
        "tips": [
            "Communicate clearly with teammates",
            "Support your team's strategy",
            "Share resources and information",
            "Build team chemistry"
        ]
    }
}

# --- Helper Functions ---

def get_streak_multiplier(streak):
    """Get multiplier based on streak length"""
    if streak >= 30:
        return STREAK_MULTIPLIERS[30]
    elif streak >= 15:
        return STREAK_MULTIPLIERS[15]
    elif streak >= 10:
        return STREAK_MULTIPLIERS[10]
    elif streak >= 7:
        return STREAK_MULTIPLIERS[7]
    elif streak >= 5:
        return STREAK_MULTIPLIERS[5]
    elif streak >= 3:
        return STREAK_MULTIPLIERS[3]
    elif streak >= 2:
        return STREAK_MULTIPLIERS[2]
    else:
        return STREAK_MULTIPLIERS[0]

def get_daily_tip():
    """Get random daily tip"""
    return random.choice(DAILY_TIPS)

def get_category_tips(category):
    """Get tips for specific category"""
    if category in CATEGORIES:
        return CATEGORIES[category]["tips"]
    return []

def can_visit(user_id):
    """Check if user can visit today"""
    if user_id not in user_data:
        return True, None
    
    last_visit = user_data[user_id].get("last_visit")
    if not last_visit:
        return True, None
    
    today = datetime.datetime.now().date()
    last_date = datetime.datetime.fromisoformat(last_visit).date()
    
    if today > last_date:
        return True, None
    elif today == last_date:
        return False, "✅ You already visited today!"
    else:
        return True, None

def calculate_points(user_id):
    """Calculate points with streak multiplier"""
    base_points = random.randint(5, 15)
    streak = user_data.get(user_id, {}).get("streak", 0)
    multiplier = get_streak_multiplier(streak)
    points = int(base_points * multiplier)
    
    # Random bonus (10% chance)
    if random.random() < 0.10:
        points = points * 2
        return points, "🎉 DOUBLE POINTS!"
    
    return points, ""

def format_daily_tip_message(user_id, tip, points, points_type):
    """Format daily tip message"""
    user_name = user_data[user_id].get("name", "User")
    total_points = user_data[user_id]["points"]
    streak = user_data[user_id]["streak"]
    
    message = (
        f"🎮 **Daily Gaming Tip**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Player:** {user_name}\n"
        f"📅 **Day:** {streak}\n\n"
        f"**{tip['title']}**\n"
        f"{tip['tip']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ **Points:** +{points}\n"
        f"{points_type}\n"
        f"📊 **Total:** {total_points} points\n"
        f"🔥 **Streak:** {streak} days\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    # Motivational messages
    if streak >= 30:
        message += "\n🏆 **GAMING LEGEND!** 30-day streak!"
    elif streak >= 15:
        message += "\n🌟 **AMAZING!** 15 days of learning!"
    elif streak >= 7:
        message += "\n⭐ **GREAT!** One week of smart play!"
    elif streak >= 3:
        message += "\n💪 **Keep going!** You're improving!"
    elif streak == 1:
        message += "\n🎯 **Day 1!** Come back for more tips!"
    
    return message

def get_leaderboard():
    """Get top 10 users by points"""
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["points"], reverse=True)
    return sorted_users[:10]

# --- Command Handlers ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Welcome message"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if user_id not in user_data:
        user_data[user_id] = {
            "points": 0,
            "last_visit": None,
            "streak": 0,
            "total_visits": 0,
            "name": user_name
        }
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎯 Daily Tip", callback_data="daily_tip"),
        InlineKeyboardButton("📂 Categories", callback_data="categories")
    )
    markup.add(
        InlineKeyboardButton("📊 My Stats", callback_data="my_stats"),
        InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")
    )
    markup.add(
        InlineKeyboardButton("ℹ️ About", callback_data="about")
    )
    
    welcome_text = (
        f"👋 Welcome, {user_name}!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎮 **Playing Smart**\n\n"
        f"Level up your gaming skills!\n"
        f"• 🎯 Daily gaming tips\n"
        f"• 📂 Strategy categories\n"
        f"• ⭐ Earn points\n"
        f"• 🔥 Build streaks\n"
        f"• 🏆 Compete on leaderboard\n\n"
        f"**Start learning now:**"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['tip'])
def daily_tip_command(message):
    """Get daily tip via command"""
    handle_daily_tip(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['categories'])
def categories_command(message):
    """Show categories via command"""
    handle_categories(message.chat.id)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Show stats via command"""
    handle_stats(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['leaderboard'])
def leaderboard_command(message):
    """Show leaderboard via command"""
    handle_leaderboard(message.chat.id)

@bot.message_handler(commands=['help'])
def send_help(message):
    """Help command"""
    help_text = (
        "📖 **Commands**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "• `/start` - Main menu\n"
        "• `/tip` - Get daily gaming tip\n"
        "• `/categories` - Browse tip categories\n"
        "• `/stats` - Your stats\n"
        "• `/leaderboard` - Top players\n"
        "• `/help` - This message\n\n"
        "🎮 **How it works:**\n"
        "Get daily gaming tips\n"
        "Earn points for learning\n"
        "Build streaks\n"
        "Compete with others\n\n"
        "📌 **Free gaming education!**"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Handle any other messages"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📂 Menu", callback_data="start"))
    
    response = (
        "💡 **Use commands or buttons:**\n\n"
        "• `/start` - Main menu\n"
        "• `/tip` - Daily tip\n"
        "• `/categories` - Browse tips\n"
        "• `/stats` - Your stats\n"
        "• `/leaderboard` - Top players"
    )
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=markup)

# --- Handler Functions ---

def handle_daily_tip(chat_id, user_id):
    """Handle daily tip"""
    if user_id not in user_data:
        bot.send_message(chat_id, "⚠️ Use /start first!", parse_mode='Markdown')
        return
    
    can_visit_now, message = can_visit(user_id)
    if not can_visit_now:
        last_visit = user_data[user_id]["last_visit"]
        last_date = datetime.datetime.fromisoformat(last_visit).date()
        next_date = last_date + datetime.timedelta(days=1)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📊 My Stats", callback_data="my_stats"))
        
        bot.send_message(
            chat_id,
            f"⏰ {message}\n"
            f"📅 **Next tip available:** {next_date.strftime('%B %d, %Y')}",
            parse_mode='Markdown',
            reply_markup=markup
        )
        return
    
    # Get daily tip
    tip = get_daily_tip()
    points, points_type = calculate_points(user_id)
    
    # Update user data
    user_data[user_id]["points"] += points
    user_data[user_id]["total_visits"] += 1
    user_data[user_id]["last_visit"] = datetime.datetime.now().isoformat()
    user_data[user_id]["streak"] += 1
    user_data[user_id]["name"] = user_data[user_id].get("name", "User")
    
    result_message = format_daily_tip_message(user_id, tip, points, points_type)
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📂 Categories", callback_data="categories"),
        InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
    )
    markup.add(InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"))
    markup.add(InlineKeyboardButton("🔄 Tomorrow's Tip", callback_data="daily_tip"))
    
    bot.send_message(
        chat_id,
        result_message,
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_categories(chat_id):
    """Show tip categories"""
    markup = InlineKeyboardMarkup(row_width=2)
    for key, value in CATEGORIES.items():
        markup.add(InlineKeyboardButton(f"{value['emoji']} {value['name']}", callback_data=f"cat_{key}"))
    markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
    
    bot.send_message(
        chat_id,
        "📂 **Choose a Category:**\n"
        "Get specific tips for your gaming style!",
        parse_mode='Markdown',
        reply_markup=markup
    )

def handle_category_tips(chat_id, category):
    """Show tips for specific category"""
    if category not in CATEGORIES:
        return
    
    cat_data = CATEGORIES[category]
    tips = cat_data["tips"]
    
    text = f"{cat_data['emoji']} **{cat_data['name']} Tips**\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, tip in enumerate(tips, 1):
        text += f"{i}. {tip}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━"
    text += "\n💡 **Apply these tips to improve your game!**"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📂 More Categories", callback_data="categories"),
        InlineKeyboardButton("🎯 Daily Tip", callback_data="daily_tip")
    )
    markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
    
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)

def handle_stats(chat_id, user_id):
    """Show user stats"""
    if user_id not in user_data:
        bot.send_message(chat_id, "⚠️ Use /start first!", parse_mode='Markdown')
        return
    
    data = user_data[user_id]
    streak = data["streak"]
    total_points = data["points"]
    total_visits = data["total_visits"]
    multiplier = get_streak_multiplier(streak)
    
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["points"], reverse=True)
    rank = next((i+1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), "N/A")
    
    stats_text = (
        f"📊 **Your Stats**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Player:** {data['name']}\n"
        f"⭐ **Points:** {total_points}\n"
        f"📈 **Total Visits:** {total_visits}\n"
        f"🔥 **Streak:** {streak} days\n"
        f"📈 **Multiplier:** {multiplier}x\n"
        f"🏆 **Rank:** #{rank} of {len(user_data)}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎯 Daily Tip", callback_data="daily_tip"),
        InlineKeyboardButton("📂 Categories", callback_data="categories")
    )
    markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
    
    bot.send_message(chat_id, stats_text, parse_mode='Markdown', reply_markup=markup)

def handle_leaderboard(chat_id):
    """Show leaderboard"""
    top_users = get_leaderboard()
    
    if not top_users:
        leaderboard_text = "🏆 **Leaderboard**\n━━━━━━━━━━━━━━━━━━━━\n\nNo players yet. Be the first!"
    else:
        leaderboard_text = "🏆 **Leaderboard**\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, (user_id, data) in enumerate(top_users, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            name = data.get("name", "Player")
            points = data["points"]
            streak = data.get("streak", 0)
            leaderboard_text += f"{medal} **{name}** - {points} pts (🔥{streak}d)\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎯 Daily Tip", callback_data="daily_tip"),
        InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
    )
    markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
    
    bot.send_message(chat_id, leaderboard_text, parse_mode='Markdown', reply_markup=markup)

# --- Callback Handlers ---

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle button clicks"""
    try:
        if call.data == "start":
            send_welcome(call.message)
            bot.answer_callback_query(call.id)
            
        elif call.data == "daily_tip":
            handle_daily_tip(call.message.chat.id, call.from_user.id)
            bot.answer_callback_query(call.id)
            
        elif call.data == "categories":
            handle_categories(call.message.chat.id)
            bot.answer_callback_query(call.id)
            
        elif call.data.startswith("cat_"):
            category = call.data.replace("cat_", "")
            handle_category_tips(call.message.chat.id, category)
            bot.answer_callback_query(call.id)
            
        elif call.data == "my_stats":
            handle_stats(call.message.chat.id, call.from_user.id)
            bot.answer_callback_query(call.id)
            
        elif call.data == "leaderboard":
            handle_leaderboard(call.message.chat.id)
            bot.answer_callback_query(call.id)
            
        elif call.data == "about":
            about_text = (
                "🤖 **About Playing Smart**\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Level up your gaming skills!\n\n"
                "✅ Daily gaming tips\n"
                "✅ Strategy categories\n"
                "✅ Earn points\n"
                "✅ Build streaks\n"
                "✅ Compete on leaderboard\n\n"
                "📌 **Free gaming education**\n"
                "🎯 **No gambling. Just skills.**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👥 {len(user_data)} players"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Menu", callback_data="start"))
            
            bot.edit_message_text(
                about_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
            bot.answer_callback_query(call.id)
            
    except Exception as e:
        logging.error(f"Callback error: {e}")
        bot.answer_callback_query(call.id, text="❌ Error", show_alert=True)

# --- Main Execution ---

if __name__ == '__main__':
    logging.info("🚀 Playing Smart Bot is starting...")
    logging.info(f"✅ Bot online! Players: {len(user_data)}")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logging.error(f"Bot polling failed: {e}")
