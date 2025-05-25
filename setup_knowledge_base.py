#!/usr/bin/env python3
"""
Script to populate the knowledge base with common IT support solutions
"""

import asyncio
from app.services.vector_service import vector_service

async def populate_knowledge_base():
    """Add common IT support knowledge to the vector database"""
    
    # Common IT issues and solutions
    knowledge_entries = [
        {
            "question": "computer running slow laptop performance issue",
            "answer": """Here are steps to fix a slow computer:

1. **Restart your computer** - This clears temporary files and resets processes
2. **Check available storage** - Ensure you have at least 15% free disk space
3. **Close unnecessary programs** - Use Task Manager (Ctrl+Shift+Esc) to end resource-heavy applications
4. **Run Disk Cleanup** - Search for 'Disk Cleanup' in Start menu and clean temporary files
5. **Update Windows** - Go to Settings > Update & Security > Windows Update
6. **Check for malware** - Run Windows Defender full scan
7. **Disable startup programs** - In Task Manager, go to Startup tab and disable unnecessary programs

If these steps don't help, the issue might be hardware-related.""",
            "category": "IT"
        },
        {
            "question": "wifi connection problem internet not working",
            "answer": """To fix WiFi connection issues:

1. **Check WiFi is enabled** - Look for WiFi icon in system tray
2. **Restart network adapter**:
   - Right-click WiFi icon > Open Network & Internet settings
   - Go to Change adapter options
   - Right-click WiFi adapter > Disable, then Enable
3. **Forget and reconnect to network**:
   - Go to WiFi settings
   - Click on your network > Forget
   - Reconnect by entering password
4. **Reset network settings**:
   - Open Command Prompt as administrator
   - Run: ipconfig /release
   - Run: ipconfig /flushdns
   - Run: ipconfig /renew
5. **Restart router** - Unplug for 30 seconds, then plug back in
6. **Update WiFi drivers** - Go to Device Manager > Network adapters > Update driver""",
            "category": "IT"
        },
        {
            "question": "printer not working printing problem",
            "answer": """To troubleshoot printer issues:

1. **Check connections** - Ensure USB/network cable is securely connected
2. **Check printer status** - Make sure it's powered on and not showing error lights
3. **Restart print spooler**:
   - Press Win+R, type 'services.msc'
   - Find 'Print Spooler' service
   - Right-click > Restart
4. **Clear print queue**:
   - Go to Settings > Printers & scanners
   - Click your printer > Open queue
   - Cancel all pending jobs
5. **Update printer drivers**:
   - Go to manufacturer's website
   - Download latest drivers for your model
6. **Run printer troubleshooter**:
   - Settings > Update & Security > Troubleshoot
   - Run printer troubleshooter""",
            "category": "IT"
        },
        {
            "question": "password reset login issue account locked",
            "answer": """For password and login issues:

1. **Use self-service password reset**:
   - Go to company login page
   - Click 'Forgot Password'
   - Follow email instructions
2. **Check Caps Lock** - Ensure Caps Lock is off
3. **Try different browser** - Clear cache or use incognito mode
4. **Check account status** - Account might be locked due to multiple failed attempts
5. **Contact IT if self-service fails** - We can unlock your account manually
6. **For multi-factor authentication issues**:
   - Ensure your phone has signal
   - Check if authenticator app time is synced
   - Try backup codes if available

Note: Passwords must be at least 8 characters with uppercase, lowercase, numbers, and symbols.""",
            "category": "IT"
        },
        {
            "question": "email not working outlook issues",
            "answer": """To fix email problems:

1. **Check internet connection** - Ensure you can browse websites
2. **Restart Outlook** - Close completely and reopen
3. **Check server settings**:
   - File > Account Settings > Account Settings
   - Verify incoming/outgoing server settings
4. **Test email in web browser** - Try accessing email via web interface
5. **Clear Outlook cache**:
   - Close Outlook
   - Delete files in %localappdata%\\Microsoft\\Outlook
6. **Recreate email profile**:
   - Control Panel > Mail > Show Profiles
   - Create new profile with your email settings
7. **Check mailbox size** - Delete old emails if mailbox is full
8. **Disable add-ins** - Start Outlook in safe mode to test""",
            "category": "IT"
        },
        {
            "question": "screen display monitor issues",
            "answer": """For display problems:

1. **Check cable connections** - Ensure monitor cable is securely connected
2. **Try different cable/port** - Test with another HDMI/VGA cable
3. **Adjust display settings**:
   - Right-click desktop > Display settings
   - Check resolution and orientation
4. **Update graphics drivers**:
   - Device Manager > Display adapters
   - Right-click graphics card > Update driver
5. **For multiple monitors**:
   - Windows key + P to choose display mode
   - Extend, Duplicate, or Second screen only
6. **Test with another monitor** - Isolate if issue is monitor or computer
7. **Check power saving settings** - Ensure monitor isn't in sleep mode""",
            "category": "IT"
        },
        {
            "question": "software application not opening crashing",
            "answer": """To fix application issues:

1. **Restart the application** - Close completely and reopen
2. **Run as administrator** - Right-click app > Run as administrator
3. **Check for updates** - Look for app updates in settings
4. **Restart your computer** - This clears memory and processes
5. **Check compatibility** - Ensure app is compatible with your Windows version
6. **Reinstall the application**:
   - Uninstall from Control Panel > Programs
   - Download fresh copy from official website
7. **Check Windows Event Viewer** - Look for error details
8. **Temporarily disable antivirus** - Test if security software is blocking
9. **Run System File Checker** - Open cmd as admin, run 'sfc /scannow'""",
            "category": "IT"
        }
    ]
    
    print("Adding knowledge base entries...")
    
    for entry in knowledge_entries:
        try:
            await vector_service.add_knowledge(
                question=entry["question"],
                answer=entry["answer"],
                category=entry["category"]
            )
            print(f"✓ Added: {entry['question'][:50]}...")
        except Exception as e:
            print(f"✗ Failed to add: {entry['question'][:50]}... - Error: {e}")
    
    print(f"\nCompleted! Added {len(knowledge_entries)} knowledge base entries.")

if __name__ == "__main__":
    asyncio.run(populate_knowledge_base())