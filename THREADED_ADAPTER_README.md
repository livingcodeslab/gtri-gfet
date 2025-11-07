# GFET Adapter with 1/4-28 UNF Threads

## Success! ✓

Created a new version of the GFET adapter with **integrated 1/4-28 UNF threads** for HPLC fittings.

## Port Locations (Identified Programmatically)

The 2 main HPLC ports are located on the **RIGHT face** (X≈28mm):

| Port | Position (Y, Z) | Counterbore Diameter |
|------|-----------------|----------------------|
| #1   | (20.71, 11.58) | 30mm                 |
| #2   | (16.92, 12.29) | 30mm                 |

**Spacing:** 3.86mm apart

## Thread Specifications

- **Type:** 1/4-28 UNF (Unified National Fine)
- **Major diameter:** 6.35mm (0.250")
- **Minor diameter:** 5.49mm
- **Pitch:** 0.907mm (28 threads per inch)
- **Thread depth:** 15mm into part

## Files

### STL Files
- **`CAD/gfet_adapter.STL`** - Original with smooth holes (needs tapping)
- **`CAD/gfet_adapter_with_threads.stl`** - NEW! With printed 1/4-28 UNF threads (5.0MB)

### OpenSCAD Files
- **`gfet_adapter_with_threads_FINAL.scad`** - Final threaded version source
- `hplc_male_connector.scad` - 1/4-28 UNF male connector model (for reference)

### Analysis Scripts
- `find_right_face_ports.py` - Successfully identified the 2 ports
- `find_largest_cylinders.py`, `find_holes_only.py`, etc. - Earlier attempts

## Usage

### Option 1: Print the Threaded Version (Recommended)

```bash
# The STL is ready to print
# File: CAD/gfet_adapter_with_threads.stl
```

**Print Settings:**
- **Layer height:** 0.1-0.15mm (finer is better for threads)
- **Perimeters:** 4-5 minimum
- **Infill:** 40%+
- **Material:** PETG or ABS recommended (stronger than PLA)
- **No supports** in thread areas if possible

### Option 2: Tap the Original (If Preferred)

Use the original `CAD/gfet_adapter.STL` and tap with:
- **1/4-28 UNF tap set**
- **#3 drill bit** (5.41mm / 0.213") for pilot holes
- **Cutting fluid**

## How It Was Found

After multiple detection algorithms, the successful approach was:

1. User clarified: "face pointing left" with "positive X, Y, Z" = RIGHT face (X≈28)
2. Searched RIGHT face specifically for circular patterns in YZ plane
3. Found 31 holes, ranked by diameter
4. Top 2 were both 30mm diameter, 3.9mm apart
5. These are the large counterbores that the threaded channels go through

## Testing

Before printing the full part, you can test just the threads:

1. Edit `gfet_adapter_with_threads_FINAL.scad`
2. Uncomment the test thread section at the bottom
3. Render a small test piece
4. Print and test-fit with an actual 1/4-28 UNF male fitting

## Repository

https://github.com/livingcodeslab/gtri-gfet
