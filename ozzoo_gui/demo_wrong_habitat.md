# Demonstrating Wrong Habitat Feature

## What's New

The shop GUI now allows you to place animals in **incompatible enclosures** to demonstrate the error handling built into the backend.

## How It Works

### 1. **Enclosure Selection Enhanced**
When purchasing an animal, the enclosure dropdown now shows:
- ✓ **Compatible enclosures** (marked with checkmark)
- ⚠ **Incompatible enclosures** (marked with warning symbol and `[WRONG HABITAT!]`)

### 2. **Visual Warnings**
- All enclosures show their habitat type (e.g., "Eucalyptus Grove", "Billabong")
- Orange warning text appears: "⚠ Animals placed in wrong habitats will have health issues!"
- Incompatible enclosures are clearly labeled

### 3. **Confirmation Dialog**
If you try to place an animal in an incompatible habitat:
- A **Yes/No confirmation dialog** appears
- Shows exactly which habitat is required vs. selected
- Warns that the animal will suffer health problems
- Requires explicit confirmation to proceed

### 4. **Different Purchase Messages**
- **Correct habitat**: "Welcome {name} to OzZoo! They are happy in their new home."
- **Wrong habitat**: Warning message stating the animal is in the wrong habitat and will have health issues

## Testing Steps

1. **Start the application** and create/load a zoo
2. **Build multiple enclosure types**:
   - E.g., Create a "Eucalyptus Grove" and a "Billabong"
3. **Go to the Shop → Animals tab**
4. **Select a Koala** (requires Eucalyptus Grove)
5. **In the enclosure dropdown**, you'll see:
   - `✓ Eucalyptus Enclosure (0/10) - Eucalyptus Grove`
   - `⚠ Wetland Habitat (0/8) - Billabong [WRONG HABITAT!]`
6. **Select the wrong habitat** (Billabong)
7. **Click Purchase**
8. **Confirmation dialog appears** warning you about the incompatibility
9. **Click "Yes"** to proceed
10. **Warning message** confirms the purchase but notes the habitat issue

## Backend Integration

The backend's `InvalidHabitatError` exception is still raised when attempting to add animals to wrong habitats. However, since the user has explicitly confirmed they want to proceed despite the warning, the system demonstrates the error condition educationally.

## Educational Value

This feature demonstrates:
- **Exception handling** in the domain model (`InvalidHabitatError`)
- **User confirmation dialogs** for potentially harmful actions
- **Defensive programming** with multiple warning layers
- **Real-world constraints** in software systems
