import os

print("🔍 CURRENT WORKING DIRECTORY:")
print(os.getcwd())
print("\n📁 ALL FILES IN CURRENT DIRECTORY:")
for file in os.listdir('.'):
    print(f"   {file}")
print("\n🔎 SPECIFICALLY LOOKING FOR HTML FILES:")
html_files = [f for f in os.listdir('.') if f.endswith('.html')]
if html_files:
    for html_file in html_files:
        print(f"   ✅ {html_file}")
else:
    print("   ❌ No HTML files found!")
    
print(f"\n📄 Does index.html exist? {os.path.exists('index.html')}")