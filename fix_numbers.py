"""Fix existing WhatsApp numbers to international format."""
from database import get_supabase

supabase = get_supabase()

# Numbers to fix (local format → international format)
fixes = {
    "09010674385": "+2349010674385",  # Fabam
    "08071014732": "+2348071014732",  # Teemarh
    "08077048651": "+2348077048651",  # Abk
    "2347051268773": "+2347051268773"  # KitKat (missing +)
}

print("=" * 80)
print("FIXING WHATSAPP NUMBERS TO INTERNATIONAL FORMAT")
print("=" * 80)

for old_number, new_number in fixes.items():
    # Find trader with old number
    result = supabase.table("traders").select("id, business_name, whatsapp_number").eq("whatsapp_number", old_number).execute()
    
    if result.data and len(result.data) > 0:
        trader = result.data[0]
        print(f"\n✏️  Updating {trader['business_name']}: {old_number} → {new_number}")
        
        # Update to new number
        update_result = supabase.table("traders").update({
            "whatsapp_number": new_number
        }).eq("id", trader['id']).execute()
        
        print(f"✅ Updated successfully")
    else:
        print(f"⚠️  No trader found with number: {old_number}")

print("\n" + "=" * 80)
print("DELETING DUPLICATE 'WhatsApp Seller' ENTRIES")
print("=" * 80)

# Delete duplicate WhatsApp Seller entries
duplicates = supabase.table("traders").select("id, business_name, whatsapp_number, user_id").eq("business_name", "WhatsApp Seller").execute()

for dup in duplicates.data:
    print(f"\n🗑️  Deleting duplicate: {dup['whatsapp_number']} (ID: {dup['id']})")
    
    # Delete trader first (due to foreign key constraint)
    supabase.table("traders").delete().eq("id", dup['id']).execute()
    print(f"   Deleted trader: {dup['id']}")
    
    # Then delete associated user
    if dup['user_id']:
        supabase.table("users").delete().eq("id", dup['user_id']).execute()
        print(f"   Deleted user: {dup['user_id']}")

print("\n✅ All duplicates removed!")
