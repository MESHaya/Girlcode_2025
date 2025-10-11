print("Starting test...")

try:
    print("Attempting import...")
    from utils.multilingual_helper import MultilingualHelper
    print("Import successful!")
    
    print("Creating helper...")
    helper = MultilingualHelper()
    print("Helper created!")
    
    print("Getting English message...")
    msg = helper.get_message('ai_detected', 'en', 'ui')
    print(f"English: {msg}")
    
    print("Getting Sesotho message...")
    msg_zu = helper.get_message('ai_detected', 'st', 'ui')
    print(f"Sesotho: {msg_zu}")
    
    print("\n✅ SUCCESS! Multilingual is working!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()