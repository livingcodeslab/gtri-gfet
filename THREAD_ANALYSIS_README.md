# GFET Adapter Thread Analysis

## Summary

The `gfet_adapter.STL` file was analyzed to determine if it contains printed threads or smooth holes requiring tapping.

## Results

**✓ CONCLUSION: Smooth holes requiring tapping**

- **No helical/spiral patterns detected** in the STL geometry
- Holes have consistent angular positions across Z-heights (not spiraling)
- **Recommended action**: Tap holes with **1/4-28 UNF** taps for HPLC fittings

## Thread Specifications

For HPLC fitting ports:
- **Thread type**: 1/4-28 UNF (Unified National Fine)
- **Major diameter**: 6.35mm (0.250")
- **Minor diameter**: 5.49mm
- **Pitch**: 0.907mm (28 threads per inch)
- **Tap drill size**: #3 drill (5.41mm / 0.213") or 5.5mm metric

## Required Tapping Tools

1. **1/4-28 UNF tap set** (taper, plug, bottoming)
2. **#3 or 5.5mm drill bit** (for pilot holes)
3. **Tap wrench** (T-handle, adjustable)
4. **Cutting fluid / tapping oil**

## Alternative: Threaded STL Version

If you prefer to 3D print threads instead of tapping, OpenSCAD files have been generated:

### Files Created

- `gfet_adapter_threaded.scad` - Full version (all 31 detected holes)
- `gfet_adapter_threaded_HPLC_only.scad` - **Recommended** (8 primary HPLC ports only)

### How to Generate Threaded STL

1. Install OpenSCAD:
   ```bash
   sudo apt install openscad
   ```

2. Render the threaded version:
   ```bash
   openscad gfet_adapter_threaded_HPLC_only.scad -o CAD/gfet_adapter_with_threads.stl
   ```

3. Print the new STL with 1/4-28 UNF threads integrated

### Print Settings for Threaded Version

- **Layer height**: 0.1-0.15mm (finer is better for threads)
- **Perimeters**: 4-5 minimum
- **Infill**: 40%+
- **Material**: PETG or ABS recommended (stronger than PLA)
- **No supports** in thread areas if possible

## Analysis Scripts

Several Python scripts were created for the analysis:

- `analyze_stl.py` - Basic STL thread analyzer
- `analyze_threads_detailed.py` - Detailed geometric analysis
- `detect_helical.py` - Helical pattern detector
- `find_inner_holes.py` - HPLC port location finder

Run any of these with:
```bash
python3 <script_name>.py
```

## Technical Details

The helical detection algorithm checks for:
1. Vertices at consistent radii from cylinder axis
2. Systematic angle variation with Z-height (d(θ)/d(z) ≠ 0)
3. Regular pitch spacing

**Result**: d(θ)/d(z) ≈ 0 for all detected holes → no helical pattern → smooth holes

## Repository

Project repository: https://github.com/livingcodeslab/gtri-gfet
