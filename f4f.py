#!/usr/bin/env python3
"""
VPS Control Bot - All-in-One Telegram Bot
Setup + Run everything in one file
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# ============================================================================
# SETUP PHASE
# ============================================================================

def setup():
    """Create folder, install dependencies, setup everything"""
    
    # Create 'l' folder if doesn't exist
    folder_name = "l"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"✓ Created folder: {folder_name}")
    
    # Change to folder
    os.chdir(folder_name)
    
    # Create venv if doesn't exist
    venv_path = "venv"
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        print(f"✓ Virtual environment created")
    
    # Get venv python path
    venv_python = os.path.join(venv_path, "bin", "python")
    
    # Create requirements.txt
    requirements_path = "requirements.txt"
    if not os.path.exists(requirements_path):
        with open(requirements_path, "w") as f:
            f.write("python-telegram-bot==20.0\n")
            f.write("psutil==5.9.5\n")
            f.write("requests==2.31.0\n")
            f.write("phonenumbers==8.13.0\n")
        print(f"✓ Created {requirements_path}")
    
    # Install requirements
    print("Installing dependencies...")
    try:
        subprocess.check_call(
            [venv_python, "-m", "pip", "install", "-q", "-r", requirements_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✓ Dependencies installed")
    except:
        print("⚠️ Installing dependencies with output...")
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", requirements_path])

# ============================================================================
# CONFIGURATION
# ============================================================================

API_TOKEN = "8139451866:AAHWYH0RQUvfHeTpIolO-3LFh6ze_59ASe0"
ADMIN_ID = "6348414703"  # Admin user ID

WELCOME_MESSAGE = """
╔════════════════════════════════════════╗
║   📱 PHONE NUMBER INFO BOT 📱           ║
║   24/7 Mobile Number Intelligence      ║
╚════════════════════════════════════════╝

Welcome! I'm your phone number intelligence bot for mobile number lookup and analysis.

👮 **Main Features:**
  • 📱 Phone Number Lookup & Validation
  • 🌍 Country & Region Detection
  • 📡 Carrier/Provider Information
  • 🎯 Number Type Detection
  • 📊 Format Verification
  • 🔍 Batch Number Lookup
  • 🗺️ Location Information
  • ✅ Number Status Check

🎯 **Quick Start:**
  Type /help to see all available commands
  Type /phone <number> to lookup a number

⚠️ **Security Note:**
  This bot has admin restrictions. Only authorized users can execute commands.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready to lookup phone numbers! 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

HELP_MESSAGE = """
📋 **AVAILABLE COMMANDS:**

**Phone Number Lookup:**
  /phone <number> - Complete phone number lookup
  /validate <number> - Validate phone number format
  /carrier <number> - Get carrier/provider info
  /location <number> - Get location info
  /type <number> - Detect number type (mobile/landline)
  /country <number> - Country & region info
  /batch <numbers> - Bulk lookup (space separated)
  /format <number> - Check format & details

**Secondary - VPS Control:**

**System Monitoring:**
  /status - System status
  /cpu - CPU info
  /memory - Memory usage
  /disk - Disk space
  /processes - Top processes
  /uptime - Uptime
  /netstat - Network stats
  /free - Memory usage (detailed)

**System Control:**
  /restart - Restart VPS
  /shutdown - Shutdown VPS
  /reboot - Reboot VPS
  /cmd <command> - Execute command
  /shell <command> - Custom shell command

**File Management:**
  /ls <path> - List directory
  /pwd - Current directory

**File Reading:**
  /cat <file> - Read entire file
  /read <file> [start] [end] - Read specific lines
  /head <file> [lines] - First N lines
  /tail <file> [lines] - Last N lines
  /wc <file> - Count lines/words/bytes
  /hexdump <file> - View in hex

**File Writing:**
  /write <file> <content> - Create/overwrite file
  /append <file> <content> - Add to file
  /edit <file> <content> - Create/edit file
  /sed <file> <search> <replace> - Replace text

**File Operations:**
  /mkdir <dir> - Create directory
  /touch <file> - Create empty file
  /rm <target> - Delete (needs confirmation)
  /rmconfirm <target> - Delete (confirmed)
  /chmod <perms> <file> - Change permissions
  /chown <owner:group> <file> - Change owner
  /find <pattern> - Find files
  /grep <text> <file> - Search in file
  /du <path> - Disk usage
  /ps <pattern> - Process list

**Download & Install:**
  /install <url> - Download & execute script
  /wget <url> <output> - Download file
  /curl <url> - HTTP request

**Process Management:**
  /kill <pid> - Kill process
  /ping <host> - Ping host

**System Access & Navigation:**
  /home - Home directory & tools
  /tools - Available tools
  /dirs - Directory structure
  /browse <path> - Browse any folder

**Other:**
  /help - Show this help
  /start - Show welcome
  /logs - View logs

⚠️ Commands require admin authorization.
"""

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_admin(user_id: int) -> bool:
    """Check if user is authorized admin"""
    try:
        return int(user_id) == int(ADMIN_ID)
    except:
        return False

def run_command(cmd: str) -> str:
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "⏱️ Command timeout (>10s)"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================================================
# BOT HANDLERS
# ============================================================================

# ============================================================================
# PHONE NUMBER HANDLERS
# ============================================================================

async def phone_lookup(update, context):
    """Complete phone number lookup"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /phone <number>")
        return
    
    number = context.args[0]
    await update.message.reply_text(f"📱 Looking up: `{number}`", parse_mode="Markdown")
    
    try:
        import requests
        import phonenumbers
        
        parsed = phonenumbers.parse(number, None)
        carrier = phonenumbers.carrier.name_for_number(parsed, "en_US")
        region = phonenumbers.geocoder.description_for_number(parsed, "en_US")
        number_type = phonenumbers.number_type(parsed)
        
        type_map = {0: "Fixed Line", 1: "Mobile", 2: "Toll Free", 3: "Premium", 4: "VoIP", 5: "Unknown"}
        num_type = type_map.get(number_type, "Unknown")
        
        result = f"""
📱 **PHONE NUMBER REPORT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 Number: `{phonenumbers.format_number(parsed, 1)}`
🌍 Country: {region}
📡 Carrier: {carrier if carrier else "Unknown"}
🎯 Type: {num_type}
✅ Valid: {phonenumbers.is_valid_number(parsed)}
"""
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def validate_number(update, context):
    """Validate phone number"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /validate <number>")
        return
    
    number = context.args[0]
    try:
        import phonenumbers
        parsed = phonenumbers.parse(number, None)
        is_valid = phonenumbers.is_valid_number(parsed)
        
        result = f"""
✅ **VALIDATION RESULT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 Number: `{number}`
✅ Valid: {'Yes' if is_valid else 'No'}
📍 Possible: {phonenumbers.is_possible_number(parsed)}
🎯 Format: {phonenumbers.format_number(parsed, 1)}
"""
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def carrier_info(update, context):
    """Get carrier information"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /carrier <number>")
        return
    
    number = context.args[0]
    try:
        import phonenumbers
        parsed = phonenumbers.parse(number, None)
        carrier = phonenumbers.carrier.name_for_number(parsed, "en_US")
        
        result = f"""
📡 **CARRIER INFORMATION**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 Number: `{number}`
📡 Carrier: {carrier if carrier else "Unknown"}
🌍 Country: {phonenumbers.region_code_for_number(parsed)}
"""
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def location_info(update, context):
    """Get location information"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /location <number>")
        return
    
    number = context.args[0]
    try:
        import phonenumbers
        parsed = phonenumbers.parse(number, None)
        location = phonenumbers.geocoder.description_for_number(parsed, "en_US")
        
        result = f"""
🗺️ **LOCATION INFORMATION**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 Number: `{number}`
🗺️ Location: {location if location else "Unknown"}
🌍 Country: {phonenumbers.region_code_for_number(parsed)}
"""
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def number_type(update, context):
    """Detect number type"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /type <number>")
        return
    
    number = context.args[0]
    try:
        import phonenumbers
        parsed = phonenumbers.parse(number, None)
        num_type = phonenumbers.number_type(parsed)
        
        type_map = {0: "Fixed Line", 1: "Mobile", 2: "Toll Free", 3: "Premium", 4: "VoIP", 5: "Unknown"}
        type_name = type_map.get(num_type, "Unknown")
        
        result = f"""
🎯 **NUMBER TYPE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 Number: `{number}`
🎯 Type: {type_name}
"""
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def country_info(update, context):
    """Get country information"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /country <number>")
        return
    
    number = context.args[0]
    try:
        import phonenumbers
        parsed = phonenumbers.parse(number, None)
        country_code = phonenumbers.region_code_for_number(parsed)
        
        result = f"""
🌍 **COUNTRY INFORMATION**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 Number: `{number}`
🌍 Country Code: {country_code}
🔢 Country Calling Code: +{parsed.country_code}
"""
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def batch_lookup(update, context):
    """Bulk phone number lookup"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /batch <number1> <number2> ...")
        return
    
    numbers = context.args
    try:
        import phonenumbers
        results = "🔍 **BATCH LOOKUP RESULTS**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for num in numbers[:10]:
            parsed = phonenumbers.parse(num, None)
            carrier = phonenumbers.carrier.name_for_number(parsed, "en_US")
            valid = phonenumbers.is_valid_number(parsed)
            
            results += f"\n📞 `{num}` → Valid: {'✅' if valid else '❌'} | Carrier: {carrier or 'Unknown'}"
        
        await update.message.reply_text(results, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def format_check(update, context):
    """Check number format and details"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /format <number>")
        return
    
    number = context.args[0]
    try:
        import phonenumbers
        parsed = phonenumbers.parse(number, None)
        
        result = f"""
📊 **FORMAT DETAILS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 Original: `{number}`
📱 E164: {phonenumbers.format_number(parsed, 1)}
🌐 International: {phonenumbers.format_number(parsed, 0)}
📍 National: {phonenumbers.format_number(parsed, 2)}
📟 RFC3966: {phonenumbers.format_number(parsed, 3)}
"""
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ============================================================================
# VPS CONTROL HANDLERS (SECONDARY)
# ============================================================================

async def start(update, context):
    """Handle /start command"""
    user = update.effective_user
    logger.info(f"User {user.id} started bot")
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")

async def help_command(update, context):
    """Handle /help command"""
    await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")

async def status(update, context):
    """Get full system status"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    await update.message.reply_text("⏳ Gathering system status...")
    
    try:
        uptime = run_command("uptime -p")
        cpu = run_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
        mem = run_command("free -h | grep Mem | awk '{print \"Used: \" $3 \" / \" $2}'")
        disk = run_command("df -h / | tail -1 | awk '{print \"Used: \" $3 \" / \" $2}'")
        hostname = run_command("hostname")
        ip = run_command("hostname -I")
        
        status_msg = f"""
📊 **SYSTEM STATUS** 📊
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏠 Hostname: `{hostname}`
🌐 IP Address: `{ip}`
⏰ Uptime: {uptime}

💻 **Resources:**
  CPU Usage: {cpu}
  Memory: {mem}
  Disk: {disk}

⏱️ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await update.message.reply_text(status_msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def cpu(update, context):
    """Get CPU information"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    cpu_info = run_command("lscpu | head -10")
    cpu_usage = run_command("top -bn1 | grep 'Cpu(s)'")
    
    msg = f"💻 **CPU INFORMATION**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{cpu_info}\n\n📈 Current Usage:\n{cpu_usage}"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def memory(update, context):
    """Get memory information"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    mem_info = run_command("free -h")
    msg = f"💾 **MEMORY INFORMATION**\n```\n{mem_info}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def disk(update, context):
    """Get disk information"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    disk_info = run_command("df -h")
    msg = f"💿 **DISK INFORMATION**\n```\n{disk_info}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def processes(update, context):
    """Get top processes"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    procs = run_command("ps aux --sort=-%cpu | head -11")
    msg = f"⚙️ **TOP PROCESSES**\n```\n{procs}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def uptime(update, context):
    """Get system uptime"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    uptime_info = run_command("uptime")
    msg = f"⏰ **UPTIME**\n```\n{uptime_info}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def netstat(update, context):
    """Get network statistics"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    net_info = run_command("netstat -i")
    msg = f"🌐 **NETWORK STATISTICS**\n```\n{net_info}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def ping(update, context):
    """Ping a host"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ping <hostname>")
        return
    
    host = context.args[0]
    ping_result = run_command(f"ping -c 4 {host}")
    msg = f"🏓 **PING {host}**\n```\n{ping_result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def logs(update, context):
    """View bot logs"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    try:
        with open("bot.log", "r") as f:
            logs_content = f.readlines()[-20:]
        msg = f"📝 **BOT LOGS** (last 20 lines)\n```\n{''.join(logs_content)}\n```"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error reading logs: {str(e)}")

async def cmd(update, context):
    """Execute custom command (DANGEROUS - admin only)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /cmd <command>")
        return
    
    command = " ".join(context.args)
    await update.message.reply_text(f"⏳ Executing: `{command}`", parse_mode="Markdown")
    
    result = run_command(command)
    msg = f"📤 **COMMAND OUTPUT**\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def restart(update, context):
    """Restart VPS"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    await update.message.reply_text("⚠️ Restart initiated. VPS will restart in 10 seconds.")
    logger.warning(f"Restart command issued by user {update.effective_user.id}")
    run_command("sudo shutdown -r +10 'Restart initiated by VPS Bot'")

async def shutdown(update, context):
    """Shutdown VPS"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    await update.message.reply_text("⚠️ Shutdown initiated. VPS will shutdown in 10 seconds.")
    logger.warning(f"Shutdown command issued by user {update.effective_user.id}")
    run_command("sudo shutdown +10 'Shutdown initiated by VPS Bot'")

async def reboot(update, context):
    """Reboot VPS"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    await update.message.reply_text("⚠️ Reboot initiated. VPS will reboot in 10 seconds.")
    logger.warning(f"Reboot command issued by user {update.effective_user.id}")
    run_command("sudo shutdown -r +10 'Reboot initiated by VPS Bot'")

async def ls_cmd(update, context):
    """List directory contents"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    path = " ".join(context.args) if context.args else "."
    result = run_command(f"ls -lah {path}")
    msg = f"📁 **DIRECTORY LISTING: {path}**\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def pwd_cmd(update, context):
    """Print working directory"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    result = run_command("pwd")
    await update.message.reply_text(f"📂 Current Directory: `{result}`", parse_mode="Markdown")

async def cat_cmd(update, context):
    """Read file contents"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /cat <filepath>")
        return
    
    filepath = " ".join(context.args)
    
    # Check if file exists and get size
    file_info = run_command(f"file {filepath}")
    file_size = run_command(f"wc -c < {filepath} 2>/dev/null || echo 0")
    
    # Read file with line numbers
    result = run_command(f"cat {filepath} 2>/dev/null || echo 'Error reading file'")
    
    # Limit output to avoid message size limits
    if len(result) > 4000:
        result = result[:3900] + "\n... (truncated - file too large)"
    
    msg = f"""
📄 **FILE: {filepath}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Size: {file_size.strip()} bytes
📋 Info: {file_info}

📖 **CONTENTS:**
```
{result}
```
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def read_cmd(update, context):
    """Read file with line numbers"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /read <filepath> [start_line] [end_line]")
        return
    
    filepath = context.args[0]
    start = context.args[1] if len(context.args) > 1 else "1"
    end = context.args[2] if len(context.args) > 2 else ""
    
    if end:
        result = run_command(f"sed -n '{start},{end}p' {filepath}")
    else:
        result = run_command(f"sed -n '{start},$p' {filepath} | head -50")
    
    if not result:
        result = "Empty or file not found"
    
    msg = f"""
📖 **READ FILE: {filepath}** (lines {start}-{end or 'end'})
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
{result}
```
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def write_cmd(update, context):
    """Write content to file"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "✍️ **WRITE TO FILE**\n\n"
            "Usage: /write <filepath> <content>\n\n"
            "Example:\n"
            "  /write test.txt Hello World\n"
            "  /write config.sh #!/bin/bash\n\n"
            "⚠️ This OVERWRITES the file!\n"
            "Use /append to add to file"
        )
        return
    
    filepath = context.args[0]
    content = " ".join(context.args[1:])
    
    # Escape content for shell
    result = run_command(f"echo '{content}' > {filepath} && echo 'Written'")
    
    await update.message.reply_text(
        f"✅ **FILE WRITTEN**\n\n"
        f"📝 File: `{filepath}`\n"
        f"📄 Content: `{content[:100]}...`\n"
        f"✨ Status: {result}",
        parse_mode="Markdown"
    )

async def append_cmd(update, context):
    """Append content to file"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "✍️ **APPEND TO FILE**\n\n"
            "Usage: /append <filepath> <content>\n\n"
            "Example:\n"
            "  /append test.txt New Line\n"
            "  /append config.sh export PATH=$PATH:/usr/local/bin\n\n"
            "💡 This ADDS to the file, doesn't overwrite"
        )
        return
    
    filepath = context.args[0]
    content = " ".join(context.args[1:])
    
    result = run_command(f"echo '{content}' >> {filepath} && echo 'Appended'")
    
    await update.message.reply_text(
        f"✅ **CONTENT APPENDED**\n\n"
        f"📝 File: `{filepath}`\n"
        f"📄 Added: `{content[:100]}...`\n"
        f"✨ Status: {result}",
        parse_mode="Markdown"
    )

async def edit_cmd(update, context):
    """Edit file (create/update file with content)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "✏️ **EDIT FILE**\n\n"
            "Usage: /edit <filepath> <content>\n\n"
            "Example:\n"
            "  /edit script.sh #!/bin/bash\\necho Hello\n"
            "  /edit test.py print('Hello')\n\n"
            "💡 Use \\\\n for newlines in content"
        )
        return
    
    filepath = context.args[0]
    content = " ".join(context.args[1:])
    
    # Replace \\n with actual newlines
    content = content.replace("\\n", "\n")
    
    # Write using printf to handle newlines
    result = run_command(f"printf '%s' '{content.replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39)+chr(39))}' > {filepath} && echo 'Updated'")
    
    await update.message.reply_text(
        f"✏️ **FILE UPDATED**\n\n"
        f"📝 File: `{filepath}`\n"
        f"📋 Lines: {content.count(chr(10)) + 1}\n"
        f"✨ Status: File saved",
        parse_mode="Markdown"
    )

async def head_cmd(update, context):
    """Show first lines of file"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /head <filepath> [lines]")
        return
    
    filepath = context.args[0]
    lines = context.args[1] if len(context.args) > 1 else "10"
    
    result = run_command(f"head -n {lines} {filepath}")
    msg = f"📄 **HEAD: {filepath}** (first {lines} lines)\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def tail_cmd(update, context):
    """Show last lines of file"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /tail <filepath> [lines]")
        return
    
    filepath = context.args[0]
    lines = context.args[1] if len(context.args) > 1 else "10"
    
    result = run_command(f"tail -n {lines} {filepath}")
    msg = f"📄 **TAIL: {filepath}** (last {lines} lines)\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def wc_cmd(update, context):
    """Count lines, words, bytes"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /wc <filepath>")
        return
    
    filepath = " ".join(context.args)
    
    lines = run_command(f"wc -l < {filepath}")
    words = run_command(f"wc -w < {filepath}")
    bytes_count = run_command(f"wc -c < {filepath}")
    
    msg = f"""
📊 **FILE STATISTICS: {filepath}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📏 Lines: {lines.strip()}
💬 Words: {words.strip()}
📦 Bytes: {bytes_count.strip()}
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def sed_cmd(update, context):
    """Replace text in file (sed)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "🔄 **REPLACE TEXT IN FILE (SED)**\n\n"
            "Usage: /sed <filepath> <search> <replace>\n\n"
            "Example:\n"
            "  /sed config.txt old new\n"
            "  /sed script.sh localhost 127.0.0.1\n\n"
            "⚠️ Creates backup file .bak"
        )
        return
    
    filepath = context.args[0]
    search = context.args[1]
    replace = context.args[2]
    
    result = run_command(f"sed -i.bak 's/{search}/{replace}/g' {filepath} && echo 'Replaced'")
    
    await update.message.reply_text(
        f"✅ **TEXT REPLACED**\n\n"
        f"📝 File: `{filepath}`\n"
        f"🔍 Search: `{search}`\n"
        f"✏️ Replace: `{replace}`\n"
        f"💾 Backup: `{filepath}.bak`",
        parse_mode="Markdown"
    )

async def hexdump_cmd(update, context):
    """View file in hex"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /hexdump <filepath>")
        return
    
    filepath = " ".join(context.args)
    result = run_command(f"hexdump -C {filepath} | head -20")
    msg = f"🔢 **HEXDUMP: {filepath}**\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def mkdir_cmd(update, context):
    """Create directory"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /mkdir <directory_name>")
        return
    
    dirname = " ".join(context.args)
    result = run_command(f"mkdir -p {dirname}")
    await update.message.reply_text(f"✅ Directory created: `{dirname}`", parse_mode="Markdown")

async def rm_cmd(update, context):
    """Remove file/directory"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /rm <file_or_directory>")
        return
    
    target = " ".join(context.args)
    await update.message.reply_text(f"⚠️ Deleting: `{target}`\nConfirm with /rmconfirm {target}")

async def rmconfirm_cmd(update, context):
    """Confirm remove"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /rmconfirm <file_or_directory>")
        return
    
    target = " ".join(context.args)
    result = run_command(f"rm -rf {target}")
    await update.message.reply_text(f"✅ Deleted: `{target}`", parse_mode="Markdown")

async def touch_cmd(update, context):
    """Create empty file"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /touch <filename>")
        return
    
    filename = " ".join(context.args)
    result = run_command(f"touch {filename}")
    await update.message.reply_text(f"✅ File created: `{filename}`", parse_mode="Markdown")

async def chmod_cmd(update, context):
    """Change file permissions"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /chmod <permissions> <file>")
        return
    
    perms = context.args[0]
    filepath = " ".join(context.args[1:])
    result = run_command(f"chmod {perms} {filepath}")
    await update.message.reply_text(f"✅ Permissions changed: `{filepath}` → `{perms}`", parse_mode="Markdown")

async def chown_cmd(update, context):
    """Change file owner"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /chown <owner:group> <file>")
        return
    
    owner = context.args[0]
    filepath = " ".join(context.args[1:])
    result = run_command(f"sudo chown {owner} {filepath}")
    await update.message.reply_text(f"✅ Owner changed: `{filepath}` → `{owner}`", parse_mode="Markdown")

async def find_cmd(update, context):
    """Find files"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /find <pattern>")
        return
    
    pattern = " ".join(context.args)
    result = run_command(f"find . -name '*{pattern}*' 2>/dev/null | head -20")
    msg = f"🔍 **FIND: {pattern}**\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def grep_cmd(update, context):
    """Search in files"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /grep <search_text> <filepath>")
        return
    
    search = context.args[0]
    filepath = " ".join(context.args[1:])
    result = run_command(f"grep -n '{search}' {filepath} 2>/dev/null | head -20")
    msg = f"🔍 **GREP: {search}** in `{filepath}`\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def install_cmd(update, context):
    """Install and execute script via wget"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /install <url>")
        return
    
    url = context.args[0]
    await update.message.reply_text(f"⏳ Downloading and executing: `{url}`", parse_mode="Markdown")
    
    try:
        result = run_command(f"wget -q -O - {url} | bash")
        msg = f"✅ **INSTALL COMPLETE**\n```\n{result}\n```"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def wget_cmd(update, context):
    """Download file"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /wget <url> [output_filename]")
        return
    
    url = context.args[0]
    output = context.args[1] if len(context.args) > 1 else ""
    
    cmd = f"wget {url}"
    if output:
        cmd += f" -O {output}"
    
    await update.message.reply_text(f"⏳ Downloading: `{url}`", parse_mode="Markdown")
    result = run_command(cmd)
    msg = f"✅ **DOWNLOAD COMPLETE**\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def curl_cmd(update, context):
    """Send HTTP request"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /curl <url>")
        return
    
    url = context.args[0]
    result = run_command(f"curl -s {url} | head -50")
    msg = f"🌐 **CURL: {url}**\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def du_cmd(update, context):
    """Check disk usage"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    path = " ".join(context.args) if context.args else "."
    result = run_command(f"du -sh {path}")
    msg = f"💾 **DISK USAGE: {path}**\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def free_cmd(update, context):
    """Check memory usage"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    result = run_command("free -h")
    msg = f"🧠 **MEMORY USAGE**\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def ps_cmd(update, context):
    """List running processes"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    pattern = " ".join(context.args) if context.args else ""
    if pattern:
        result = run_command(f"ps aux | grep {pattern} | grep -v grep")
    else:
        result = run_command("ps aux | head -15")
    
    msg = f"⚙️ **PROCESSES**\n```\n{result}\n```"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def kill_cmd(update, context):
    """Kill process"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /kill <pid>")
        return
    
    pid = context.args[0]
    result = run_command(f"kill {pid}")
    await update.message.reply_text(f"✅ Process killed: `{pid}`", parse_mode="Markdown")

async def shell_cmd(update, context):
    """Execute custom shell command"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **SHELL COMMAND EXECUTION**\n\n"
            "Usage: /shell <command>\n\n"
            "Examples:\n"
            "  /shell whoami\n"
            "  /shell uname -a\n"
            "  /shell env | grep PATH\n"
            "  /shell systemctl status nginx\n\n"
            "⚠️ Be careful with powerful commands!",
            parse_mode="Markdown"
        )
        return
    
    command = " ".join(context.args)
    await update.message.reply_text(f"⏳ Executing: `{command}`", parse_mode="Markdown")
    
    try:
        result = run_command(command)
        
        # Limit output to avoid Telegram message size limits
        if len(result) > 4000:
            result = result[:3900] + "\n... (truncated)"
        
        if not result:
            result = "(No output)"
        
        msg = f"""
🖥️ **SHELL COMMAND RESULT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Command: `{command}`

📤 Output:
```
{result}
```
"""
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error executing command: {str(e)}", parse_mode="Markdown")

async def browse_cmd(update, context):
    """Browse any folder/path"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    # Default to home if no args
    path = " ".join(context.args) if context.args else "~"
    
    # Expand ~ to home directory
    expanded_path = run_command(f"echo {path}")
    
    # Check if path exists
    exists = run_command(f"test -d {path} && echo 'exists' || echo 'not'")
    
    if "not" in exists:
        await update.message.reply_text(f"❌ Path not found: `{path}`", parse_mode="Markdown")
        return
    
    # Get folder info
    path_info = run_command(f"ls -lah {path}")
    dir_size = run_command(f"du -sh {path}")
    file_count = run_command(f"find {path} -type f 2>/dev/null | wc -l")
    
    msg = f"""
📁 **FOLDER BROWSER**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Path: `{expanded_path}`
💾 Size: {dir_size}
📄 Files: {file_count}

📋 **CONTENTS:**
```
{path_info}
```

💡 **QUICK COMMANDS:**
  /browse /home - Browse home folder
  /browse /Desktop - Browse Desktop
  /browse /tmp - Browse tmp
  /browse /opt - Browse opt
  /browse / - Browse root
  /ls {path} - List with details
  /cat {path}/file - Read file
  /find {path} pattern - Search files
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def home_cmd(update, context):
    """Access home directory and shell tools"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    # Get home directory info
    home_dir = run_command("echo $HOME")
    home_size = run_command(f"du -sh {home_dir}")
    home_files = run_command(f"ls -lah {home_dir} | head -20")
    
    # Get Desktop if exists
    desktop = run_command(f"test -d {home_dir}/Desktop && ls -lah {home_dir}/Desktop | head -10 || echo 'No Desktop folder'")
    
    # Get available tools
    tools = run_command("which bash sh python python3 node ruby perl java gcc git docker wget curl 2>/dev/null | head -20")
    
    # Get environment info
    user = run_command("whoami")
    shell = run_command("echo $SHELL")
    
    msg = f"""
🏠 **HOME DIRECTORY ACCESS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 User: `{user}`
📂 Home: `{home_dir}`
💾 Size: {home_size}
🐚 Shell: `{shell}`

📁 **HOME CONTENTS (first 20):**
```
{home_files}
```

🖥️ **DESKTOP:**
```
{desktop}
```

🛠️ **AVAILABLE TOOLS:**
```
{tools}
```

📝 **QUICK COMMANDS:**
  /browse ~ - Browse home
  /browse ~/Desktop - Browse Desktop
  /browse /home - Browse /home folder
  /ls ~ - List home
  /cat ~/.bashrc - View bash config
  /find ~ <pattern> - Find in home
  /shell env - Show environment
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def tools_cmd(update, context):
    """List all installed tools and utilities"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    # Get all available commands
    tools_output = run_command("which bash sh python python3 node npm ruby perl java gcc g++ make git docker docker-compose kubectl wget curl nmap netcat nc tcpdump wireshark aircrack-ng sqlmap metasploit msfconsole nikto gobuster hydra john hashcat ffmpeg imagemagick 2>/dev/null | head -30")
    
    installed = run_command("dpkg -l | grep -E '(python|node|ruby|perl|java|git|docker|wget|curl|nmap)' | wc -l")
    
    msg = f"""
🛠️ **SYSTEM TOOLS & UTILITIES**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Total Installed: ~{installed} packages

🔍 **KEY TOOLS:**
```
{tools_output}
```

📝 **USEFUL COMMANDS:**
  /shell apt list --installed - All packages
  /shell pip list - Python packages
  /shell npm list -g - Node packages
  /shell gem list - Ruby packages
  /shell ls /usr/local/bin - Local tools
  /shell which <tool> - Find tool location

🎯 **QUICK INFO:**
  /shell uname -a - System info
  /shell lsb_release -a - OS info
  /shell gcc --version - Compiler version
  /shell python3 --version - Python version
  /shell node --version - Node version
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def dirs_cmd(update, context):
    """List and navigate important system directories"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized access")
        return
    
    # Check important directories
    dirs_info = run_command("""
echo "=== HOME DIRECTORIES ===" && ls -d ~/* 2>/dev/null | head -15 && \
echo "" && \
echo "=== SYSTEM DIRECTORIES ===" && ls -d /home/* 2>/dev/null | head -10 && \
echo "" && \
echo "=== IMPORTANT PATHS ===" && \
ls -ld /etc /opt /usr /var /tmp /root 2>/dev/null
""")
    
    msg = f"""
📂 **DIRECTORY STRUCTURE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
{dirs_info}
```

🗺️ **NAVIGATE WITH:**
  /browse ~ - Home directory
  /browse ~/Desktop - Desktop
  /browse /home - All users
  /browse /opt - Optional software
  /browse /etc - Config files
  /browse /var - Variable data
  /browse /tmp - Temporary files
  /browse /root - Root home
  /browse /usr/local - Local binaries
  /browse /usr/local/bin - Local tools

💡 **FOLDER SIZE:**
  /du ~ - Home size
  /du /home - All homes size
  /du /opt - Opt size
  /du / - Root size
  
📁 **TREE VIEW:**
  /shell tree ~ - Home tree
  /shell tree /opt - Opt tree
  /shell find ~ -type d - Find dirs
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_message(update, context):
    """Handle regular messages"""
    await update.message.reply_text("I don't understand that. Type /help for available commands.")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Start the bot"""
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    
    if not API_TOKEN or API_TOKEN == "YOUR_TELEGRAM_BOT_API_KEY_HERE":
        print("\n" + "="*50)
        print("❌ ERROR: API_TOKEN not configured!")
        print("="*50)
        print("\nEdit this file (bot.py) and set:")
        print('  API_TOKEN = "your_token_here"')
        print('  ADMIN_ID = "your_id_here"')
        print("\nGet token from: @BotFather on Telegram")
        print("Get ID from: @userinfobot on Telegram")
        print("="*50 + "\n")
        return
    

    
    if not ADMIN_ID or ADMIN_ID == "YOUR_TELEGRAM_USER_ID_HERE":
        print("\n⚠️ WARNING: ADMIN_ID not configured!")
        print("Edit bot.py and add your Telegram user ID\n")
    
    print("\n" + "="*50)
    print("🚀 Starting VPS Control Bot...")
    print("="*50 + "\n")
    
    # Create the Application
    application = Application.builder().token(API_TOKEN).build()
    
    # Register Phone Number handlers
    application.add_handler(CommandHandler("phone", phone_lookup))
    application.add_handler(CommandHandler("validate", validate_number))
    application.add_handler(CommandHandler("carrier", carrier_info))
    application.add_handler(CommandHandler("location", location_info))
    application.add_handler(CommandHandler("type", number_type))
    application.add_handler(CommandHandler("country", country_info))
    application.add_handler(CommandHandler("batch", batch_lookup))
    application.add_handler(CommandHandler("format", format_check))
    
    # Register general handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # VPS System Monitoring
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("cpu", cpu))
    application.add_handler(CommandHandler("memory", memory))
    application.add_handler(CommandHandler("disk", disk))
    application.add_handler(CommandHandler("processes", processes))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("netstat", netstat))
    application.add_handler(CommandHandler("free", free_cmd))
    application.add_handler(CommandHandler("ping", ping))
    
    # VPS System Control
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("shutdown", shutdown))
    application.add_handler(CommandHandler("reboot", reboot))
    application.add_handler(CommandHandler("cmd", cmd))
    application.add_handler(CommandHandler("shell", shell_cmd))
    
    # File Management & Navigation
    application.add_handler(CommandHandler("ls", ls_cmd))
    application.add_handler(CommandHandler("pwd", pwd_cmd))
    
    # File Reading
    application.add_handler(CommandHandler("cat", cat_cmd))
    application.add_handler(CommandHandler("read", read_cmd))
    application.add_handler(CommandHandler("head", head_cmd))
    application.add_handler(CommandHandler("tail", tail_cmd))
    application.add_handler(CommandHandler("wc", wc_cmd))
    application.add_handler(CommandHandler("hexdump", hexdump_cmd))
    
    # File Writing
    application.add_handler(CommandHandler("write", write_cmd))
    application.add_handler(CommandHandler("append", append_cmd))
    application.add_handler(CommandHandler("edit", edit_cmd))
    application.add_handler(CommandHandler("sed", sed_cmd))
    
    # File Operations
    application.add_handler(CommandHandler("mkdir", mkdir_cmd))
    application.add_handler(CommandHandler("touch", touch_cmd))
    application.add_handler(CommandHandler("rm", rm_cmd))
    application.add_handler(CommandHandler("rmconfirm", rmconfirm_cmd))
    application.add_handler(CommandHandler("chmod", chmod_cmd))
    application.add_handler(CommandHandler("chown", chown_cmd))
    application.add_handler(CommandHandler("find", find_cmd))
    application.add_handler(CommandHandler("grep", grep_cmd))
    application.add_handler(CommandHandler("du", du_cmd))
    application.add_handler(CommandHandler("ps", ps_cmd))
    
    # Download & Install
    application.add_handler(CommandHandler("install", install_cmd))
    application.add_handler(CommandHandler("wget", wget_cmd))
    application.add_handler(CommandHandler("curl", curl_cmd))
    
    # Process Management
    application.add_handler(CommandHandler("kill", kill_cmd))
    
    # Logging
    application.add_handler(CommandHandler("logs", logs))
    
    # System Access & Navigation
    application.add_handler(CommandHandler("home", home_cmd))
    application.add_handler(CommandHandler("tools", tools_cmd))
    application.add_handler(CommandHandler("dirs", dirs_cmd))
    application.add_handler(CommandHandler("browse", browse_cmd))
    
    # Handle messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot started successfully")
    print("✓ Bot connected and listening...\n")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    setup()
    main()
